"""
小白语音助手桥接技能
监听 voice-messages.jsonl 并自动回复
"""
import json
import time
from pathlib import Path
from datetime import datetime

# 文件路径
MSG_FILE = Path("C:/Users/fourStar/.openclaw/voice-messages.jsonl")
RSP_FILE = Path("C:/Users/fourStar/.openclaw/voice-messages-responses.jsonl")
LAST_CHECKED_ID = 0

def check_voice_messages():
    """
    检查小白语音助手的消息并回复
    在 HEARTBEAT.md 中调用此函数
    """
    global LAST_CHECKED_ID
    
    if not MSG_FILE.exists():
        return None
        
    responses = []
    
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
                if msg_id > LAST_CHECKED_ID and msg.get("status") == "pending":
                    content = msg.get("content", "")
                    session_id = msg.get("session_id")
                    
                    print(f"[Voice] 收到消息 [{msg_id}]: {content}")
                    
                    # 生成回复（实际应该调用AI处理）
                    reply_content = process_message(content)
                    
                    # 发送回复
                    send_voice_reply(msg_id, reply_content, session_id)
                    
                    # 更新最后处理ID
                    LAST_CHECKED_ID = msg_id
                    responses.append((msg_id, content, reply_content))
                    
            except json.JSONDecodeError:
                continue
                
        return responses if responses else None
        
    except Exception as e:
        print(f"[Voice] 检查消息错误: {e}")
        return None

def process_message(content: str) -> str:
    """
    处理消息内容，生成回复
    这里可以调用AI模型生成回复
    """
    # 简单回复示例
    # 实际应该调用 OpenClaw 的AI能力
    
    greetings = ["你好", "您好", "在吗", "嗨"]
    if any(g in content for g in greetings):
        return "你好！我是OpenClaw，有什么可以帮你的？"
    
    if "谢谢" in content:
        return "不客气！有需要随时叫我。"
    
    if "再见" in content or "拜拜" in content:
        return "再见！小白语音助手随时待命。"
    
    # 默认回复
    return f"收到你的消息：'{content}'。我是OpenClaw Agent，可以通过语音助手与你对话。"

def send_voice_reply(reply_to: int, content: str, session_id: str = None):
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
        
    print(f"[Voice] 回复 [{reply_to}]: {content[:50]}...")

# 如果直接运行此文件，执行一次检查
if __name__ == "__main__":
    result = check_voice_messages()
    if result:
        print(f"\n处理了 {len(result)} 条消息")
    else:
        print("\n没有新消息")
