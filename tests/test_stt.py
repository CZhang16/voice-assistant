"""
测试语音识别
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open

from src.stt import SpeechToText


class TestSpeechToText:
    """测试语音识别器"""
    
    @pytest.fixture
    def stt(self, mock_config):
        with patch('whisper.load_model'):
            with patch('webrtcvad.Vad'):
                return SpeechToText(mock_config)
    
    def test_init(self, stt):
        """测试初始化"""
        assert stt.model is not None
        assert stt.vad is not None
    
    @patch('pyaudio.PyAudio')
    def test_record(self, mock_pa, stt):
        """测试录音"""
        mock_stream = MagicMock()
        mock_instance = MagicMock()
        mock_instance.open.return_value = mock_stream
        mock_pa.return_value = mock_instance
        
        # 模拟音频数据
        mock_stream.read.return_value = b'\x00\x01' * 512
        
        # 模拟 VAD 检测（静音足够长，触发结束）
        stt.vad.is_speech.return_value = False
        
        result = stt.record(timeout=1)
        
        # 验证返回了 WAV 数据
        assert result is not None
        assert isinstance(result, bytes)
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('whisper.load_model')
    def test_transcribe(self, mock_load, mock_temp, stt):
        """测试语音识别"""
        # 模拟 Whisper 模型
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "你好小白"}
        stt.model = mock_model
        
        # 模拟临时文件
        mock_file = MagicMock()
        mock_file.name = "test.wav"
        mock_temp.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_temp.return_value.__exit__ = MagicMock(return_value=False)
        
        result = stt.transcribe(b"fake_audio_data")
        
        assert result == "你好小白"
        mock_model.transcribe.assert_called_once()
