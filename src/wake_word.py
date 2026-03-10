"""
唤醒词检测模块
使用 Porcupine 本地唤醒词引擎
"""
import asyncio
import logging
import os
import struct
from typing import Callable, Optional

try:
    import pvporcupine
    import pyaudio
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    
from src.config import Config


class WakeWordDetector:
    """唤醒词检测器"""
    
    def __init__(self, config: Config, callback: Callable[[], None]):
        self.config = config
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        
        self.porcupine: Optional[pvporcupine.Porcupine] = None
        self.pa: Optional[pyaudio.PyAudio] = None
        self.audio_stream: Optional[pyaudio.Stream] = None
        
        self.running = False
        self._init_porcupine()
        
    def _init_porcupine(self):
        """初始化 Porcupine"""
        if not PORCUPINE_AVAILABLE:
            self.logger.error("Porcupine 或 PyAudio 未安装")
            return
            
        try:
            access_key = self.config.get("wake_word.access_key", "")
            keyword_paths = self.config.get("wake_word.keyword_path", "")
            model_path = self.config.get("wake_word.model_path", "")
            keywords = self.config.get("wake_word.keywords", ["小白"])
            sensitivity = self.config.get("wake_word.sensitivity", 0.5)
            
            # 构建参数
            create_args = {
                "access_key": access_key,
                "sensitivities": [sensitivity]
            }
            
            # 如果有自定义模型路径，使用它
            if model_path and os.path.exists(model_path):
                create_args["model_path"] = model_path
                self.logger.info(f"使用自定义模型: {model_path}")
            
            # 如果有自定义关键词文件，使用它
            if keyword_paths and os.path.exists(keyword_paths):
                create_args["keyword_paths"] = [keyword_paths]
                self.logger.info(f"使用自定义唤醒词: {keyword_paths}")
            else:
                # 使用内置关键词
                create_args["keywords"] = keywords if isinstance(keywords, list) else [keywords]
                self.logger.warning(f"使用内置唤醒词: {keywords}")
                
            self.porcupine = pvporcupine.create(**create_args)
            self.logger.info(f"Porcupine 初始化成功，采样率: {self.porcupine.sample_rate}")
            
        except Exception as e:
            self.logger.error(f"Porcupine 初始化失败: {e}")
            
    async def start(self):
        """开始监听"""
        if not PORCUPINE_AVAILABLE or not self.porcupine:
            self.logger.error("唤醒词检测不可用")
            return
            
        self.running = True
        self.logger.info("开始监听唤醒词...")
        
        try:
            self.pa = pyaudio.PyAudio()
            
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            self.audio_stream.start_stream()
            self.logger.info("音频流已启动，等待唤醒词...")
            
            loop_count = 0
            while self.running:
                # 读取音频帧
                try:
                    pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                    
                    # 处理音频帧
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        self.logger.info("唤醒词检测到！")
                        self.callback()
                        
                    loop_count += 1
                    if loop_count % 100 == 0:  # 每100帧输出一次
                        self.logger.debug(f"监听中... ({loop_count} frames)")
                        
                except Exception as e:
                    self.logger.error(f"音频处理错误: {e}")
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            self.logger.error(f"监听错误: {e}", exc_info=True)
        finally:
            self._cleanup()
            
    def stop(self):
        """停止监听"""
        self.running = False
        self._cleanup()
        
    def _cleanup(self):
        """清理资源"""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
            
        if self.pa:
            self.pa.terminate()
            self.pa = None
            
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
            
        self.logger.info("唤醒词检测已停止")
