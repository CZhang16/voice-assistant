@echo off
echo =========================================
echo 小白语音助手 + OpenClaw 集成
echo =========================================
echo.
echo 启动步骤：
echo 1. 启动 OpenClaw 桥接器（处理语音消息）
echo 2. 启动小白语音助手
echo.
echo 按 Ctrl+C 停止
echo =========================================
echo.

cd /d "%~dp0"

:: 设置 Python 路径
set PYTHONPATH=%~dp0

:: 启动 OpenClaw 桥接器（后台）
start "OpenClaw Voice Bridge" cmd /k "python voice_openclaw_bridge.py"

:: 等待桥接器启动
timeout /t 2 /nobreak > nul

:: 启动小白语音助手
python src/main.py

pause
