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
        if cli_path and os.path.exists(cli_path):
            return cli_path
            
        # 尝试直接在 PATH 中查找
        openclaw = shutil.which("openclaw")
        if openclaw:
            return "openclaw"
            
        # Windows 常见的 npm 全局路径
        npm_global = os.path.join(os.environ.get("APPDATA", ""), "npm", "openclaw.cmd")
        if os.path.exists(npm_global):
            return npm_global
            
        # 尝试 openclaw.ps1
        npm_ps1 = os.path.join(os.environ.get("APPDATA", ""), "npm", "openclaw.ps1")
        if os.path.exists(npm_ps1):
            return f"powershell -File {npm_ps1}"
            
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
            # 添加语音友好提示词
            voice_prompt = "【语音回复要求】简短 1-2 句话，纯文本无格式，口语化，直接回答核心内容。问题："
            formatted_message = f"{voice_prompt}{message}"
            
            self.logger.info(f"发送消息：{message}")
            
            # 构建命令：使用 --local 本地运行，--json 输出 JSON 格式
            cmd = [
                self._openclaw_path, "agent", 
                "--local",
                "--session-id", self.my_id,
                "-m", formatted_message,
                "--json",
                "--timeout", str(timeout)
            ]
            
            # 直接调用 OpenClaw CLI，使用 shell=True 支持 .cmd 文件
            proc = await asyncio.create_subprocess_shell(
                ' '.join(cmd),
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
                    # 解析 JSON 输出 - 先尝试找到 JSON 起始位置
                    output = stdout.decode('utf-8').strip()
                    
                    # 查找 JSON 起始位置（可能在调试输出之后）
                    json_start = output.find('{')
                    if json_start > 0:
                        # 跳过调试输出
                        output = output[json_start:]
                    
                    response = json.loads(output)
                    
                    # 提取文本内容 - payloads 直接在根级别
                    payloads = response.get("payloads", [])
                    if payloads and len(payloads) > 0:
                        content = payloads[0].get("text", "")
                        if content:
                            self.logger.info(f"收到回复：{content[:50]}...")
                            return content
                    
                    # 如果没有 payloads，可能返回了其他格式
                    self.logger.warning(f"响应中无文本内容：{response}")
                    return "收到"
                        
                except json.JSONDecodeError as e:
                    # 如果不是 JSON，直接返回文本
                    reply = stdout.decode('utf-8').strip()
                    if reply:
                        # 尝试跳过调试输出
                        json_start = reply.find('{')
                        if json_start > 0:
                            reply = reply[json_start:]
                        self.logger.info(f"收到回复：{reply[:50]}...")
                        return reply
                    return "收到"
            else:
                error_msg = stderr.decode('utf-8').strip()
                self.logger.error(f"OpenClaw 错误：{error_msg}")
                return "处理失败，请稍后重试"
                
        except FileNotFoundError:
            self.logger.error("未找到 openclaw 命令，请确保已安装 OpenClaw")
            return "抱歉，AI 服务未配置"
        except Exception as e:
            self.logger.error(f"Agent 调用错误：{e}")
            return "抱歉，我现在无法连接"
            
    def send_notification(self, message: str):
        """
        发送通知（不需要回复）
        由于使用 CLI 调用，这里简化为打印日志
        """
        if not self.enabled:
            return
            
        # 记录通知日志
        self.logger.info(f"通知：{message}")
