"""
语音识别模块
使用 Whisper 本地识别
"""
import io
import logging
import tempfile
from typing import Optional

try:
    import whisper
    import numpy as np
    import soundfile as sf
    import webrtcvad
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    
from src.config import Config


class SpeechToText:
    """语音识别器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.model = None
        self.vad = None
        self.pa = None
        
        self._init_whisper()
        self._init_vad()
        
    def _init_whisper(self):
        """初始化 Whisper 模型"""
        if not WHISPER_AVAILABLE:
            self.logger.error("Whisper 未安装")
            return
            
        try:
            model_name = self.config.get("stt.model", "base")
            self.logger.info(f"加载 Whisper 模型: {model_name}")
            self.model = whisper.load_model(model_name)
            self.logger.info("Whisper 模型加载完成")
        except Exception as e:
            self.logger.error(f"Whisper 加载失败: {e}")
            
    def _init_vad(self):
        """初始化语音活动检测"""
        if not WHISPER_AVAILABLE:
            return
            
        try:
            # VAD 模式：0=普通，1=低比特率，2=激进，3=非常激进
            self.vad = webrtcvad.Vad(2)
            self.logger.info("VAD 初始化完成")
        except Exception as e:
            self.logger.error(f"VAD 初始化失败: {e}")
            
    def record(self, timeout: int = 10) -> Optional[bytes]:
        """
        录音，使用 VAD 自动检测语音结束
        
        Args:
            timeout: 最大录音时长（秒）
            
        Returns:
            音频字节数据（WAV格式）
        """
        if not PYAUDIO_AVAILABLE:
            self.logger.error("PyAudio 未安装")
            return None
            
        sample_rate = self.config.get("audio.sample_rate", 16000)
        frame_duration = 30  # ms
        frame_length = int(sample_rate * frame_duration / 1000)
        
        try:
            self.pa = pyaudio.PyAudio()
            stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=frame_length
            )
            
            self.logger.info("开始录音...")
            frames = []
            silence_count = 0
            max_silence = self.config.get("vad.max_silence", 30)  # 从配置读取，默认30帧（约0.9秒）
            max_frames = int(timeout * 1000 / frame_duration)
            
            stream.start_stream()
            
            for i in range(max_frames):
                data = stream.read(frame_length, exception_on_overflow=False)
                frames.append(data)
                
                # VAD 检测
                if self.vad and len(data) == frame_length * 2:
                    is_speech = self.vad.is_speech(data, sample_rate)
                    if is_speech:
                        silence_count = 0
                    else:
                        silence_count += 1
                        
                    # 检测到足够静音，结束录音
                    if silence_count > max_silence and len(frames) > 30:
                        self.logger.info("检测到语音结束")
                        break
                        
            stream.stop_stream()
            stream.close()
            
            # 转换为 WAV 格式
            audio_data = b''.join(frames)
            
            # 使用 soundfile 创建 WAV
            with io.BytesIO() as wav_io:
                import wave
                with wave.open(wav_io, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data)
                return wav_io.getvalue()
                
        except Exception as e:
            self.logger.error(f"录音错误: {e}")
            return None
        finally:
            if self.pa:
                self.pa.terminate()
                self.pa = None
                
    def transcribe(self, audio_data: bytes) -> str:
        """
        识别音频为文字
        
        Args:
            audio_data: WAV 格式音频字节
            
        Returns:
            识别出的文字
        """
        if not WHISPER_AVAILABLE or not self.model:
            self.logger.error("Whisper 不可用")
            return ""
            
        try:
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
                
            # Whisper 识别
            language = self.config.get("stt.language", "zh")
            result = self.model.transcribe(
                tmp_path,
                language=language,
                fp16=False
            )
            
            text = result.get("text", "").strip()
            self.logger.info(f"识别结果: {text}")
            return text
            
        except Exception as e:
            self.logger.error(f"识别错误: {e}")
            return ""
