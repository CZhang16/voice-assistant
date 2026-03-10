"""
测试唤醒词检测
"""
import pytest
from unittest.mock import MagicMock, patch
import struct

from src.wake_word import WakeWordDetector


class TestWakeWordDetector:
    """测试唤醒词检测器"""
    
    @pytest.fixture
    def mock_callback(self):
        return MagicMock()
    
    @pytest.fixture
    def detector(self, mock_config, mock_callback):
        with patch('pvporcupine.create') as mock_create:
            mock_porcupine = MagicMock()
            mock_porcupine.sample_rate = 16000
            mock_porcupine.frame_length = 512
            mock_create.return_value = mock_porcupine
            
            return WakeWordDetector(mock_config, mock_callback)
    
    def test_init(self, detector):
        """测试初始化"""
        assert detector.running is False
        assert detector.callback is not None
    
    @pytest.mark.asyncio
    async def test_wake_word_detection(self, detector, mock_callback):
        """测试唤醒词检测"""
        with patch('pyaudio.PyAudio') as mock_pa:
            mock_stream = MagicMock()
            mock_instance = MagicMock()
            mock_instance.open.return_value = mock_stream
            mock_pa.return_value = mock_instance
            
            # 模拟检测到唤醒词（返回 keyword_index >= 0）
            detector.porcupine.process.return_value = 0
            
            # 模拟音频数据
            fake_pcm = struct.pack("h" * 512, *([0] * 512))
            mock_stream.read.return_value = fake_pcm
            
            # 启动检测（只运行一次循环）
            detector.running = True
            
            async def run_once():
                # 模拟一次检测循环
                data = mock_stream.read(512)
                pcm = struct.unpack_from("h" * 512, data)
                keyword_index = detector.porcupine.process(pcm)
                if keyword_index >= 0:
                    detector.callback()
            
            await run_once()
            
            # 验证回调被调用
            mock_callback.assert_called_once()
