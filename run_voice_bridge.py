#!/usr/bin/env python3
"""
小白语音助手 - OpenClaw 桥接器
一键启动，实时监听消息并回复
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 添加技能路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from voice_bridge_skill import check_voice_messages
    print("[OK] 桥接技能已加载")
except ImportError as e:
    print(f"[ERROR] 无法加载桥接技能: {e}")
    sys.exit(1)

def main():
    print("=" * 50)
    print("小白语音助手 - OpenClaw 桥接器")
    print("=" * 50)
    print()
    print("功能：监听语音消息，自动AI回复")
    print("消息文件: ~/.openclaw/voice-messages.jsonl")
    print("回复文件: ~/.openclaw/voice-messages-responses.jsonl")
    print()
    print("按 Ctrl+C 停止")
    print("-" * 50)
    print()
    
    check_count = 0
    
    try:
        while True:
            # 检查消息
            result = check_voice_messages()
            
            if result:
                for msg_id, content, reply in result:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")
                    print(f"  收到: {content}")
                    print(f"  回复: {reply}")
                    print()
            
            check_count += 1
            if check_count % 10 == 0:
                print(f".", end='', flush=True)  # 进度点
            
            # 每秒检查一次
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[STOP] 桥接器已停止")

if __name__ == "__main__":
    main()
