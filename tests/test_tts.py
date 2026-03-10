"""
测试语音合成
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from src.tts import TextToSpeech


class TestTextToSpeech:
    """测试语音合成器"""
    
    @pytest.fixture
    def tts(self, mock_config):
        with patch('pygame.mixer.init'):
            return TextToSpeech(mock_config)
    
    def test_init(self, tts):
        """测试初始化"""
        assert tts.voice == "zh-CN-XiaoxiaoNeural"
        assert tts.rate == "+0%"
    
    @pytest.mark.asyncio
    async def test_speak(self, tts):
        """测试朗读"""
        with patch('edge_tts.Communicate') as mock_communicate, \
             patch('pygame.mixer.music') as mock_music:
            
            mock_comm = AsyncMock()
            mock_communicate.return_value = mock_comm
            
            await tts.speak("你好")
            
            # 验证 Edge TTS 被调用
            mock_communicate.assert_called_once_with(
                text="你好",
                voice="zh-CN-XiaoxiaoNeural",
                rate="+0%",
                volume="+0%"
            )
            mock_comm.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_speak_empty(self, tts):
        """测试空文本"""
        with patch('edge_tts.Communicate') as mock_communicate:
            await tts.speak("")
            mock_communicate.assert_not_called()
