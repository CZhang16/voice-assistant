"""
OpenClaw Voice Assistant Bridge
处理来自小白语音助手的消息
"""
import json
import time
from pathlib import Path
from datetime import datetime

# 消息文件路径
VOICE_MSG_FILE = Path("C:/Users/fourStar/.openclaw/voice-messages.jsonl")
VOICE_RSP_FILE = Path("C:/Users/fourStar/.openclaw/voice-messages-responses.jsonl")

def process_voice_messages():
    """处理语音助手消息"""
    if not VOICE_MSG_FILE.exists():
        return []
        
    messages = []
    with open(VOICE_MSG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    if msg.get("status") == "pending":
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
    return messages

def send_reply(reply_to_id: int, content: str, session_id: str = None):
    """发送回复到语音助手"""
    VOICE_RSP_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    response = {
        "id": int(time.time() * 1000),
        "reply_to": reply_to_id,
        "session_id": session_id,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "source": "openclaw-agent"
    }
    
    with open(VOICE_RSP_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(response, ensure_ascii=False) + '\n')
        
    print(f"[Voice Bridge] 回复 [{reply_to_id}]: {content[:50]}...")

def mark_message_processed(msg_id: int):
    """标记消息为已处理"""
    if not VOICE_MSG_FILE.exists():
        return
        
    lines = []
    with open(VOICE_MSG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                msg = json.loads(line.strip())
                if msg.get("id") == msg_id:
                    msg["status"] = "processed"
                lines.append(json.dumps(msg, ensure_ascii=False))
            except:
                lines.append(line.strip())
                
    with open(VOICE_MSG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

if __name__ == "__main__":
    # 测试
    messages = process_voice_messages()
    print(f"找到 {len(messages)} 条待处理消息")
    for msg in messages:
        print(f"  [{msg['id']}] {msg['content']}")
