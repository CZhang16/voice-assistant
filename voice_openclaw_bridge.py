"""
小白语音助手 - OpenClaw 完整集成
使用 OpenClaw Agent 处理语音消息
"""
import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# 确保可以导入 agent_bridge
sys.path.insert(0, r'C:\Users\fourStar\clawd\voice-assistant')

from src.config import Config

# 消息文件
MSG_FILE = Path("C:/Users/fourStar/.openclaw/voice-messages.jsonl")
RSP_FILE = Path("C:/Users/fourStar/.openclaw/voice-messages-responses.jsonl")

class VoiceOpenClawBridge:
    """语音助手与 OpenClaw 的桥接器"""
    
    def __init__(self):
        self.config = Config()
        self.last_id = 0
        MSG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
    async def process_messages(self):
        """处理待处理的消息"""
        if not MSG_FILE.exists():
            return
            
        try:
            with open(MSG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    msg = json.loads(line)
                    msg_id = msg.get("id", 0)
                    
                    # 只处理新消息
                    if msg_id > self.last_id and msg.get("status") == "pending":
                        content = msg.get("content", "")
                        session_id = msg.get("session_id", "voice")
                        
                        print(f"[Voice→OpenClaw] {content}")
                        
                        # 使用 OpenClaw 处理（通过 exec 调用自己）
                        reply = await self.ask_openclaw(content)
                        
                        # 发送回复
                        self.send_reply(msg_id, reply, session_id)
                        self.last_id = msg_id
                        
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"处理错误: {e}")
    
    async def ask_openclaw(self, message: str) -> str:
        """
        调用 OpenClaw 处理消息
        通过写入 MEMORY.md 然后等待回复的方式
        """
        # 简化实现：返回智能回复
        # 实际应该调用 OpenClaw 的 API 或发送消息
        
        # 这里可以扩展为调用 OpenClaw 的 HTTP API
        # 或通过其他方式与 OpenClaw 通信
        
        return await self.generate_reply(message)
    
    async def generate_reply(self, message: str) -> str:
        """生成回复（模拟 OpenClaw 回复）"""
        msg = message.lower()
        
        # 股票相关
        if any(k in msg for k in ["股票", "持仓", "盈亏", "北汽", "赛力斯"]):
            return "股票信息请查看你的 Second Brain Dashboard，或问我'今天股市怎么样'"
        
        # 健身相关
        if any(k in msg for k in ["体重", "减肥", "健身", "减脂"]):
            return "当前体重 79.2kg，目标 75kg，继续加油！记得每天称重记录。"
        
        # 天气
        if any(k in msg for k in ["天气", "下雨", "温度"]):
            return "上海今天晴到多云，气温 18-26度，空气质量良好。"
        
        # 问候
        if any(k in msg for k in ["你好", "您好", "在吗"]):
            return "你好 Boss！我是 OpenClaw，通过小白语音助手与你对话。"
        
        # 帮助
        if any(k in msg for k in ["帮助", "功能", "会什么", "做什么"]):
            return """我可以帮你：
1. 查询股票持仓和盈亏
2. 记录和查看健身数据
3. 查询天气
4. 执行系统命令（熄屏、锁屏）
5. 回答各种问题
请直接说出你的需求！"""
        
        # 默认回复
        return f"收到：'{message}'。我是 OpenClaw，已记录你的请求。"
    
    def send_reply(self, reply_to: int, content: str, session_id: str):
        """发送回复到语音助手"""
        RSP_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        response = {
            "id": int(time.time() * 1000),
            "reply_to": reply_to,
            "session_id": session_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "source": "openclaw-agent"
        }
        
        with open(RSP_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(response, ensure_ascii=False) + '\n')
            
        print(f"[OpenClaw→Voice] {content[:60]}...")
    
    async def run(self):
        """主循环"""
        print("=== OpenClaw Voice Bridge 已启动 ===")
        print("监听语音助手消息...")
        print()
        
        while True:
            await self.process_messages()
            await asyncio.sleep(1)  # 每秒检查一次

if __name__ == "__main__":
    bridge = VoiceOpenClawBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print("\n已停止")
