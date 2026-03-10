"""
小白语音助手 - 主程序
Voice Assistant for Boss
"""
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Optional

# 添加 ffmpeg 路径
ffmpeg_path = r"C:\Users\fourStar\AppData\Local\Microsoft\WinGet\Links"
if ffmpeg_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

from src.wake_word import WakeWordDetector
from src.stt import SpeechToText
from src.tts import TextToSpeech
from src.agent_bridge import AgentBridge
from src.commands import CommandHandler
from src.config import Config


class VoiceAssistant:
    """小白语音助手主类"""
    
    def __init__(self):
        self.config = Config()
        self.setup_logging()
        
        self.wake_detector: Optional[WakeWordDetector] = None
        self.stt: Optional[SpeechToText] = None
        self.tts: Optional[TextToSpeech] = None
        self.agent: Optional[AgentBridge] = None
        self.commands: Optional[CommandHandler] = None
        
        self.running = False
        self._shutdown_event = asyncio.Event()
        
    def setup_logging(self):
        """配置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config.get("logging.level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.get("logging.file", "logs/voice-assistant.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """初始化所有组件"""
        self.logger.info("正在初始化小白语音助手...")
        
        # 初始化 TTS（女声）
        self.tts = TextToSpeech(self.config)
        
        # 播放启动提示
        await self.tts.speak("小白已启动，等待唤醒")
        
        # 初始化其他组件
        self.stt = SpeechToText(self.config)
        self.agent = AgentBridge(self.config)
        self.commands = CommandHandler(self.config)
        self.wake_detector = WakeWordDetector(
            self.config,
            callback=self.on_wake_word
        )
        
        self.logger.info("初始化完成")
        
    def on_wake_word(self):
        """唤醒词回调"""
        self.logger.info("检测到唤醒词: 小白")
        # 回调从音频线程调用，需要线程安全地调度到主事件循环
        import threading
        def run_async():
            asyncio.run(self.handle_conversation())
        threading.Thread(target=run_async, daemon=True).start()
        
    async def handle_conversation(self):
        """处理一次对话"""
        try:
            # 播放唤醒提示音
            await self.tts.speak("我在")
            
            # 录音并识别
            self.logger.info("正在录音...")
            audio_data = self.stt.record()
            
            if not audio_data:
                self.logger.warning("录音为空")
                return
                
            # 语音识别
            self.logger.info("正在识别...")
            text = self.stt.transcribe(audio_data)
            
            if not text:
                await self.tts.speak("没听清，请再说一遍")
                return
                
            self.logger.info(f"识别结果: {text}")
            
            # 先尝试本地命令
            handled, response = await self.commands.handle(text)
            
            if not handled:
                # 本地命令未处理，发给 Agent
                self.logger.info("发送给 Agent...")
                response = await self.agent.chat(text)
                
            # 语音回复
            if response:
                await self.tts.speak(response)
                
        except Exception as e:
            self.logger.error(f"对话处理错误: {e}", exc_info=True)
            await self.tts.speak("出错了，请稍后再试")
            
    async def run(self):
        """主循环"""
        await self.initialize()
        
        self.running = True
        self.logger.info("小白正在监听...")
        
        # 设置信号处理
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)
            
        try:
            # 启动唤醒词检测（阻塞）
            await self.wake_detector.start()
        except Exception as e:
            self.logger.error(f"运行错误: {e}", exc_info=True)
        finally:
            await self.shutdown()
            
    def _signal_handler(self, signum, frame):
        """信号处理"""
        self.logger.info(f"收到信号 {signum}，正在关闭...")
        self._shutdown_event.set()
        self.running = False
        
    async def shutdown(self):
        """关闭清理"""
        self.logger.info("正在关闭...")
        
        if self.wake_detector:
            self.wake_detector.stop()
            
        if self.tts:
            await self.tts.speak("小白已关闭")
            
        self.logger.info("关闭完成")


def main():
    """入口函数"""
    assistant = VoiceAssistant()
    
    try:
        asyncio.run(assistant.run())
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
