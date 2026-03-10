"""
测试配置和 Fixture
"""
import pytest
from unittest.mock import MagicMock, patch

from src.config import Config


@pytest.fixture
def mock_config():
    """模拟配置"""
    config = MagicMock(spec=Config)
    config.get = MagicMock(side_effect=lambda key, default=None: {
        "audio.sample_rate": 16000,
        "audio.frame_length": 512,
        "stt.model": "tiny",
        "stt.language": "zh",
        "tts.voice": "zh-CN-XiaoxiaoNeural",
        "wake_word.sensitivity": 0.5,
        "commands.enabled": True,
        "agent.enabled": True,
    }.get(key, default))
    return config


@pytest.fixture
def mock_pyaudio():
    """模拟 PyAudio"""
    with patch('pyaudio.PyAudio') as mock:
        mock_stream = MagicMock()
        mock_instance = MagicMock()
        mock_instance.open.return_value = mock_stream
        mock.return_value = mock_instance
        yield mock_instance, mock_stream
