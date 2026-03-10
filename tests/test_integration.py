"""
集成测试
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """测试完整对话流程"""
        # 模拟所有组件
        with patch('src.main.WakeWordDetector') as mock_wake, \
             patch('src.main.SpeechToText') as mock_stt, \
             patch('src.main.TextToSpeech') as mock_tts, \
             patch('src.main.AgentBridge') as mock_agent, \
             patch('src.main.CommandHandler') as mock_cmd:
            
            # 设置 mock
            mock_wake_instance = AsyncMock()
            mock_wake.return_value = mock_wake_instance
            
            mock_stt_instance = MagicMock()
            mock_stt_instance.record.return_value = b"fake_audio"
            mock_stt_instance.transcribe.return_value = "帮我熄屏"
            mock_stt.return_value = mock_stt_instance
            
            mock_tts_instance = AsyncMock()
            mock_tts.return_value = mock_tts_instance
            
            mock_agent_instance = AsyncMock()
            mock_agent_instance.chat.return_value = "这是Agent回复"
            mock_agent.return_value = mock_agent_instance
            
            mock_cmd_instance = AsyncMock()
            mock_cmd_instance.handle.return_value = (True, "已熄屏")
            mock_cmd.return_value = mock_cmd_instance
            
            # 测试流程
            from src.main import VoiceAssistant
            assistant = VoiceAssistant()
            
            # 模拟唤醒后处理
            await assistant.handle_conversation()
            
            # 验证调用
            mock_stt_instance.record.assert_called_once()
            mock_stt_instance.transcribe.assert_called_once()
            mock_cmd_instance.handle.assert_called_once()
