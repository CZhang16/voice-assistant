"""
本地命令处理
执行本地操作（熄屏、锁屏、时间、天气等）
"""
import asyncio
import ctypes
import logging
import subprocess
import random
from datetime import datetime
from typing import Tuple

from src.config import Config


class CommandHandler:
    """本地命令处理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.enabled = self.config.get("commands.enabled", True)
        self.keywords = self.config.get("commands.keywords", {})
        
    async def handle(self, text: str) -> Tuple[bool, str]:
        """
        处理命令
        
        Args:
            text: 识别的文字
            
        Returns:
            (是否处理了命令, 回复文本)
        """
        if not self.enabled:
            return False, ""
            
        text_lower = text.lower()
        
        # ========== 系统控制命令 ==========
        # 检查熄屏命令
        screen_off_keywords = self.keywords.get("screen_off", ["熄屏", "关闭屏幕", "关屏"])
        if any(kw in text for kw in screen_off_keywords):
            return self._screen_off()
            
        # 检查锁屏命令
        lock_keywords = self.keywords.get("lock", ["锁屏", "锁定"])
        if any(kw in text for kw in lock_keywords):
            return self._lock_screen()
        
        # ========== 时间日期命令 ==========
        # 检查时间
        if any(kw in text for kw in ["几点", "时间", "现在几点"]):
            return self._get_time()
            
        # 检查日期
        if any(kw in text for kw in ["几号", "日期", "今天几号", "星期几"]):
            return self._get_date()
        
        # ========== 计算器命令 ==========
        if any(kw in text for kw in ["计算", "等于", "加上", "减去", "乘", "除"]):
            result = self._calculate(text)
            if result:
                return True, result
        
        # ========== 天气/资讯命令 ==========
        if any(kw in text for kw in ["天气", "温度", "下雨", "晴天"]):
            return self._get_weather()
            
        if any(kw in text for kw in ["新闻", "资讯"]):
            return self._get_news()
        
        # ========== 娱乐命令 ==========
        if any(kw in text for kw in ["讲个笑话", "笑话", "搞笑"]):
            return self._tell_joke()
            
        if any(kw in text for kw in ["你会什么", "你能做什么", "功能", "帮助", "help"]):
            return self._list_commands()
        
        # ========== 任务/提醒命令 ==========
        task_keywords = self.keywords.get("task", ["任务", "提醒", "记录"])
        if any(kw in text for kw in task_keywords):
            return self._create_task(text)
            
        # 未识别的命令
        return False, ""
        
    def _screen_off(self) -> Tuple[bool, str]:
        """关闭屏幕"""
        try:
            self.logger.info("执行：熄屏")
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
            return True, "已熄屏"
        except Exception as e:
            self.logger.error(f"熄屏失败: {e}")
            return True, "熄屏失败"
            
    def _lock_screen(self) -> Tuple[bool, str]:
        """锁定屏幕"""
        try:
            self.logger.info("执行：锁屏")
            ctypes.windll.user32.LockWorkStation()
            return True, "已锁屏"
        except Exception as e:
            self.logger.error(f"锁屏失败: {e}")
            return True, "锁屏失败"
    
    def _get_time(self) -> Tuple[bool, str]:
        """获取当前时间"""
        now = datetime.now()
        time_str = now.strftime("%H点%M分")
        return True, f"现在是{time_str}"
    
    def _get_date(self) -> Tuple[bool, str]:
        """获取当前日期"""
        now = datetime.now()
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        weekday = weekdays[now.weekday()]
        date_str = now.strftime(f"%Y年%m月%d日，星期{weekday}")
        return True, f"今天是{date_str}"
    
    def _calculate(self, text: str) -> str:
        """简单计算器"""
        try:
            # 替换中文数字和运算符
            text = text.replace("加上", "+").replace("加", "+")
            text = text.replace("减去", "-").replace("减", "-")
            text = text.replace("乘以", "*").replace("乘", "*")
            text = text.replace("除以", "/").replace("除", "/")
            text = text.replace("等于", "=")
            text = text.replace("计算", "").strip()
            
            # 提取数字和运算符
            import re
            # 简单模式：数字 运算符 数字
            match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', text)
            if match:
                a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
                if op == '+': result = a + b
                elif op == '-': result = a - b
                elif op == '*': result = a * b
                elif op == '/':
                    if b == 0:
                        return "除数不能为零"
                    result = a / b
                    if result == int(result):
                        result = int(result)
                return f"{a} {op} {b} 等于 {result}"
            return None
        except Exception as e:
            self.logger.error(f"计算错误: {e}")
            return None
    
    def _get_weather(self) -> Tuple[bool, str]:
        """获取天气（简化版）"""
        # 这里可以接入天气API，目前返回固定回复
        weathers = [
            "今天上海晴到多云，气温18到26度，适合出行",
            "今天上海多云，气温20到28度，体感舒适",
            "今天上海阴天，气温19到25度，建议带伞"
        ]
        return True, random.choice(weathers)
    
    def _get_news(self) -> Tuple[bool, str]:
        """获取新闻（简化版）"""
        return True, "新闻功能需要接入新闻API，你可以说'讲个笑话'来测试"
    
    def _tell_joke(self) -> Tuple[bool, str]:
        """讲笑话"""
        jokes = [
            "程序员最讨厌的四件事：1. 写注释 2. 写文档 3. 别人不写注释 4. 别人不写文档",
            "为什么程序员总是分不清圣诞节和万圣节？因为 Oct 31 == Dec 25",
            "程序员去吃饭，点了一份炒饭，服务员问：'要加蛋吗？'程序员说：'默认不加'",
            "产品经理：'这个功能很简单啊，为什么需要做这么久？'程序员：'那你来？'",
            "程序员：'我的代码没问题啊，肯定是环境的问题！'",
            "为什么程序员喜欢穿格子衫？因为那是他们的'Hello World'",
            "老板：'这个需求很简单，明天能上线吗？'程序员：'...'（正在收拾东西）"
        ]
        return True, random.choice(jokes)
    
    def _list_commands(self) -> Tuple[bool, str]:
        """列出支持的命令"""
        commands = """我会这些功能：
1. 系统控制：熄屏、锁屏
2. 时间查询：现在几点、今天几号
3. 简单计算：3加5等于几
4. 天气查询：今天天气怎么样
5. 任务记录：记录任务xxx
6. 娱乐功能：讲个笑话
7. 其他指令：可以连接OpenClaw Agent回复
试试说吧！"""
        return True, commands
            
    def _create_task(self, text: str) -> Tuple[bool, str]:
        """创建任务/提醒"""
        try:
            self.logger.info(f"创建任务: {text}")
            task_content = text
            for kw in ["任务", "提醒", "记录", "帮我", "请"]:
                task_content = task_content.replace(kw, "")
            task_content = task_content.strip()
            
            if not task_content:
                return True, "请告诉我具体要记录什么"
                
            return True, f"已记录任务：{task_content}"
            
        except Exception as e:
            self.logger.error(f"创建任务失败: {e}")
            return True, "记录任务失败"
