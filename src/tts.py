"""
语音合成模块
使用 Edge TTS (微软免费在线 TTS)
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
        
        # TTS 缓存
        self._cache = {}
        
        self._init_audio()
        # 预缓存常用回复
        self._precache_common()
    
    def _precache_common(self):
        """预缓存常用回复"""
        common = ["我在", "已熄屏", "已锁屏", "没听清，请再说一遍"]
        for phrase in common:
            asyncio.create_task(self._cache_phrase(phrase))
    
    async def _cache_phrase(self, text: str):
        """缓存单个短语"""
        if text not in self._cache:
            try:
                mp3_data = await self._generate_audio(text)
                if mp3_data:
                    self._cache[text] = mp3_data
                    self.logger.debug(f"已缓存：{text}")
            except Exception as e:
                pass
    
    async def _generate_audio(self, text: str) -> Optional[bytes]:
        """生成音频数据"""
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume
            )
            
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            
            return audio_buffer.getvalue()
        except Exception as e:
            self.logger.error(f"TTS 生成失败：{e}")
            return None
        
    def _init_audio(self):
        """初始化音频播放"""
        if not EDGE_TTS_AVAILABLE:
            self.logger.error("Edge TTS 或 Pygame 未安装")
            return
            
        try:
            pygame.mixer.init(frequency=24000, size=-16, channels=2)
            self.logger.info("音频播放器初始化完成")
        except Exception as e:
            self.logger.error(f"音频初始化失败：{e}")
            
    async def speak(self, text: str):
        """朗读文本（优先使用缓存）"""
        if not EDGE_TTS_AVAILABLE:
            self.logger.error("TTS 不可用")
            print(f"[小白]: {text}")
            return
            
        if not text:
            return
        
        # 检查缓存
        if text in self._cache:
            self.logger.info(f"正在朗读 (缓存): {text}")
            self._play_audio_data(self._cache[text])
            return
            
        self.logger.info(f"正在朗读：{text}")
        
        # 生成并播放
        mp3_data = await self._generate_audio(text)
        if mp3_data:
            self._cache[text] = mp3_data
            self._play_audio_data(mp3_data)
        else:
            print(f"[小白]: {text}")
    
    def _play_audio_data(self, audio_data: bytes):
        """播放音频数据"""
        try:
            pygame.mixer.music.load(io.BytesIO(audio_data))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            self.logger.error(f"播放错误：{e}")
            
    async def speak_async(self, text: str):
        """异步朗读（不等待完成）"""
        asyncio.create_task(self.speak(text))
