"""
测试命令处理器
"""
import pytest
from unittest.mock import MagicMock, patch

from src.commands import CommandHandler


class TestCommandHandler:
    """测试命令处理器"""
    
    @pytest.fixture
    def handler(self, mock_config):
        return CommandHandler(mock_config)
    
    @pytest.mark.asyncio
    async def test_screen_off_command(self, handler):
        """测试熄屏命令"""
        with patch('ctypes.windll.user32.SendMessageW') as mock_send:
            handled, response = await handler.handle("帮我熄屏")
            
            assert handled is True
            assert "熄屏" in response
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_lock_command(self, handler):
        """测试锁屏命令"""
        with patch('ctypes.windll.user32.LockWorkStation') as mock_lock:
            handled, response = await handler.handle("锁屏")
            
            assert handled is True
            assert "锁屏" in response
            mock_lock.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_task_command(self, handler):
        """测试任务命令"""
        handled, response = await handler.handle("提醒我下午开会")
        
        assert handled is True
        assert "下午开会" in response
    
    @pytest.mark.asyncio
    async def test_unknown_command(self, handler):
        """测试未知命令"""
        handled, response = await handler.handle("今天天气怎么样")
        
        assert handled is False
        assert response == ""
