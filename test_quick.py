"""
快速测试小白语音助手
"""
import sys
sys.path.insert(0, r'C:\Users\fourStar\clawd\voice-assistant')

import asyncio
from src.config import Config
from src.tts import TextToSpeech
from src.commands import CommandHandler

async def test():
    config = Config()
    
    print("=== 测试 TTS ===")
    tts = TextToSpeech(config)
    await tts.speak("小白已启动，等待唤醒")
    
    print("\n=== 测试命令 ===")
    cmds = CommandHandler(config)
    
    # 测试命令
    test_commands = ["熄屏", "锁屏", "任务 提醒我开会", "未知命令"]
    for cmd in test_commands:
        handled, response = await cmds.handle(cmd)
        print(f"命令: {cmd} -> 处理: {handled}, 响应: {response}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test())
