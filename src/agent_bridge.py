"""
与 OpenClaw Agent 通信
直接通过 CLI 调用 OpenClaw Agent
"""
import asyncio
import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Optional

from src.config import Config


class AgentBridge:
    """OpenClaw Agent 桥接器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.enabled = self.config.get("agent.enabled", True)
        
        # 生成一个固定的 session_id，用于语音助手会话
        self.my_id = self.config.get("agent.session_id", "voice-assistant")
        
        # 保留旧配置的 message_file 路径（用于兼容）
        self.message_file = Path(self.config.get(
            "agent.message_file", 
            "C:/Users/fourStar/.openclaw/voice-messages.jsonl"
        ))
        
        # 查找 openclaw 命令路径
        self._openclaw_path = self._find_openclaw()
        
    def _find_openclaw(self) -> str:
        """查找 openclaw 命令路径"""
        # 首先尝试从配置获取
        cli_path = self.config.get("agent.cli_path", "")
        if cli_path and shutil.which(cli_path):
            return cli_path
            
        # 尝试直接在 PATH 中查找
        openclaw = shutil.which("openclaw")
        if openclaw:
            return "openclaw"
            
        # Windows 常见的 npm 全局路径
        npm_global = os.path.join(os.environ.get("APPDATA", ""), "npm", "openclaw.cmd")
        if os.path.exists(npm_global):
            return npm_global
            
        # 返回默认命令，让系统报错更清晰
        return "openclaw"
        
    async def chat(self, message: str, timeout: int = 30) -> str:
        """
        与 Agent 对话 - 直接调用 OpenClaw CLI
        
        Args:
            message: 用户消息
            timeout: 等待回复超时时间（秒）
            
        Returns:
            Agent 回复
        """
        if not self.enabled:
            return "Agent 功能已禁用"
            
        try:
            self.logger.info(f"发送消息: {message}")
            
            # 构建命令：使用 --json 输出 JSON 格式，指定 session-id
            cmd = [
                self._openclaw_path, "agent", 
                "--message", message,
                "--session-id", self.my_id,
                "--json",
                "--timeout", str(timeout)
            ]
            
            # 直接调用 OpenClaw CLI
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                await proc.kill()
                await proc.wait()
                self.logger.warning(f"Agent 调用超时")
                return "思考超时，请稍后重试"
            
            if proc.returncode == 0:
                try:
                    # 解析 JSON 输出
                    response = json.loads(stdout.decode('utf-8'))
                    
                    # 检查响应状态
                    if response.get("status") == "ok":
                        # 提取文本内容
                        result = response.get("result", {})
                        payloads = result.get("payloads", [])
                        if payloads and len(payloads) > 0:
                            content = payloads[0].get("text", "")
                            if content:
                                self.logger.info(f"收到回复: {content[:50]}...")
                                return content
                        
                        # 如果没有 payloads，可能返回了其他格式
                        self.logger.warning(f"响应中无文本内容: {response}")
                        return "收到"
                    else:
                        error_msg = response.get("error", "未知错误")
                        self.logger.error(f"Agent 返回错误: {error_msg}")
                        return f"处理失败: {error_msg}"
                        
                except json.JSONDecodeError as e:
                    # 如果不是 JSON，直接返回文本
                    reply = stdout.decode('utf-8').strip()
                    if reply:
                        self.logger.info(f"收到回复: {reply[:50]}...")
                        return reply
                    return "收到"
            else:
                error_msg = stderr.decode('utf-8').strip()
                self.logger.error(f"OpenClaw 错误: {error_msg}")
                return "处理失败，请稍后重试"
                
        except FileNotFoundError:
            self.logger.error("未找到 openclaw 命令，请确保已安装 OpenClaw")
            return "抱歉，AI 服务未配置"
        except Exception as e:
            self.logger.error(f"Agent 调用错误: {e}")
            return "抱歉，我现在无法连接"
            
    def send_notification(self, message: str):
        """
        发送通知（不需要回复）
        由于使用 CLI 调用，这里简化为打印日志
        """
        if not self.enabled:
            return
            
        # 记录通知日志
        self.logger.info(f"通知: {message}")
        
        # 可选：可以通过 CLI 发送通知
        # 这里保持简单，不阻塞发送通知
        
    async def _legacy_chat(self, message: str, timeout: int = 30) -> str:
        """
        旧的文件轮询方式（保留作为后备）
        如果 CLI 调用失败，可以 fallback 到这个方法
        """
        try:
            from datetime import datetime
            
            msg_id = int(time.time() * 1000)
            
            # 写入消息文件
            msg = {
                "id": msg_id,
                "session_id": self.my_id,
                "source": "voice-assistant",
                "type": "chat",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            with open(self.message_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                
            self.logger.info(f"消息已发送 (legacy) [{msg_id}]: {message}")
            
            # 等待回复
            return await self._wait_for_reply(msg_id, timeout)
            
        except Exception as e:
            self.logger.error(f"Legacy Agent 通信错误: {e}")
            return "抱歉，我现在无法连接"
            
    async def _wait_for_reply(self, message_id: int, timeout: int) -> str:
        """轮询等待回复（仅用于后备模式）"""
        response_file = Path(str(self.message_file).replace('.jsonl', '-responses.jsonl'))
        start_time = time.time()
        check_interval = 0.5
        
        while time.time() - start_time < timeout:
            try:
                if response_file.exists():
                    with open(response_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    for line in reversed(lines):
                        try:
                            response = json.loads(line.strip())
                            if response.get("reply_to") == message_id:
                                return response.get("content", "收到")
                        except json.JSONDecodeError:
                            continue
                            
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"读取回复错误: {e}")
                await asyncio.sleep(check_interval)
                
        self.logger.warning(f"等待回复超时 [{message_id}]")
        return "思考中，请稍后再问"