"""
语音合成模块
使用 Edge TTS (微软免费在线TTS)
"""
import asyncio
import io
import logging
import tempfile
from typing import Optional

try:
    import edge_tts
    import pygame
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    
from src.config import Config


class TextToSpeech:
    """语音合成器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.voice = self.config.get("tts.voice", "zh-CN-XiaoxiaoNeural")
        self.rate = self.config.get("tts.rate", "+0%")
        self.volume = self.config.get("tts.volume", "+0%")
        
        self._init_audio()
        
    def _init_audio(self):
        """初始化音频播放"""
        if not EDGE_TTS_AVAILABLE:
            self.logger.error("Edge TTS 或 Pygame 未安装")
            return
            
        try:
            pygame.mixer.init(frequency=24000, size=-16, channels=2)
            self.logger.info("音频播放器初始化完成")
        except Exception as e:
            self.logger.error(f"音频初始化失败: {e}")
            
    async def speak(self, text: str):
        """
        朗读文本
        
        Args:
            text: 要朗读的文字
        """
        if not EDGE_TTS_AVAILABLE:
            self.logger.error("TTS 不可用")
            print(f"[小白]: {text}")
            return
            
        if not text:
            return
            
        try:
            self.logger.info(f"正在朗读: {text}")
            
            # 生成语音
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume
            )
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name
                await communicate.save(tmp_path)
                
            # 播放
            self._play_audio(tmp_path)
            
        except Exception as e:
            self.logger.error(f"TTS 错误: {e}")
            print(f"[小白]: {text}")
            
    def _play_audio(self, file_path: str):
        """播放音频文件"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            self.logger.error(f"播放错误: {e}")
            
    async def speak_async(self, text: str):
        """异步朗读（不等待完成）"""
        asyncio.create_task(self.speak(text))
