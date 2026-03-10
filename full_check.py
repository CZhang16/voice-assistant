"""
小白语音助手 - 全流程检查
"""
import sys
sys.path.insert(0, r'C:\Users\fourStar\clawd\voice-assistant')

print('=' * 50)
print('小白语音助手 - 全流程检查')
print('=' * 50)

# 1. 检查文件结构
print('\n【1. 文件结构检查】')
import os
from pathlib import Path

base_path = Path(r'C:\Users\fourStar\clawd\voice-assistant')
required_files = {
    'src/main.py': '主程序',
    'src/wake_word.py': '唤醒词模块',
    'src/stt.py': '语音识别',
    'src/tts.py': '语音合成',
    'src/commands.py': '命令处理',
    'src/agent_bridge.py': 'Agent桥接',
    'src/config.py': '配置模块',
    'config.yaml': '配置文件',
    'xiaobai_zh_windows.ppn': '中文唤醒词模型',
    'porcupine_params_zh.pv': '中文语言模型',
}

missing = []
for file, desc in required_files.items():
    path = base_path / file
    exists = path.exists()
    status = 'OK' if exists else 'MISSING'
    print(f'  [{status}] {file} ({desc})')
    if not exists:
        missing.append(file)

if missing:
    print(f'\n  ⚠️ 缺少 {len(missing)} 个文件')

# 2. 检查依赖
print('\n【2. Python依赖检查】')
dependencies = [
    ('pvporcupine', '唤醒词引擎'),
    ('pyaudio', '音频输入'),
    ('whisper', '语音识别'),
    ('pygame', '音频播放'),
    ('edge_tts', '语音合成'),
    ('webrtcvad', '语音活动检测'),
    ('yaml', '配置解析'),
]

missing_deps = []
for pkg, desc in dependencies:
    try:
        __import__(pkg)
        print(f'  [OK] {pkg} ({desc})')
    except ImportError:
        print(f'  [MISSING] {pkg} ({desc})')
        missing_deps.append(pkg)

# 3. 检查配置
print('\n【3. 配置检查】')
from src.config import Config
config = Config()

checks = [
    ('app.name', '应用名称'),
    ('wake_word.access_key', 'Access Key'),
    ('wake_word.keyword_path', '唤醒词模型'),
    ('wake_word.model_path', '语言模型'),
    ('tts.voice', 'TTS声音'),
    ('stt.engine', 'STT引擎'),
    ('agent.enabled', 'Agent启用'),
]

for key, desc in checks:
    value = config.get(key)
    if isinstance(value, str) and len(value) > 20:
        value = value[:20] + '...'
    print(f'  {desc}: {value}')

# 4. 检查模型文件
print('\n【4. 模型文件检查】')
ppn = config.get('wake_word.keyword_path')
model = config.get('wake_word.model_path')

if ppn and os.path.exists(ppn):
    print(f'  [OK] 唤醒词模型: {ppn} ({os.path.getsize(ppn)} bytes)')
else:
    print(f'  [MISSING] 唤醒词模型: {ppn}')

if model and os.path.exists(model):
    print(f'  [OK] 语言模型: {model} ({os.path.getsize(model)} bytes)')
else:
    print(f'  [MISSING] 语言模型: {model}')

# 5. 检查Porcupine初始化
print('\n【5. Porcupine初始化测试】')
try:
    import pvporcupine
    porcupine = pvporcupine.create(
        access_key=config.get('wake_word.access_key'),
        keyword_paths=[ppn],
        model_path=model,
        sensitivities=[0.5]
    )
    print(f'  [OK] Porcupine初始化成功')
    print(f'       采样率: {porcupine.sample_rate}Hz')
    print(f'       帧长度: {porcupine.frame_length}')
    porcupine.delete()
except Exception as e:
    print(f'  [ERROR] Porcupine初始化失败: {e}')

# 6. 检查麦克风
print('\n【6. 麦克风检查】')
try:
    import pyaudio
    pa = pyaudio.PyAudio()
    info = pa.get_default_input_device_info()
    print(f'  [OK] 默认麦克风: {info["name"]}')
    pa.terminate()
except Exception as e:
    print(f'  [ERROR] 麦克风检查失败: {e}')

# 7. 检查OpenClaw桥接
print('\n【7. OpenClaw桥接检查】')
msg_file = Path(r'C:\Users\fourStar\.openclaw\voice-messages.jsonl')
rsp_file = Path(r'C:\Users\fourStar\.openclaw\voice-messages-responses.jsonl')

print(f'  消息文件: {msg_file}')
print(f'    存在: {msg_file.exists()}')
if msg_file.exists():
    print(f'    大小: {msg_file.stat().st_size} bytes')

print(f'  回复文件: {rsp_file}')
print(f'    存在: {rsp_file.exists()}')
if rsp_file.exists():
    print(f'    大小: {rsp_file.stat().st_size} bytes')

# 8. 检查命令功能
print('\n【8. 本地命令功能检查】')
from src.commands import CommandHandler
cmd = CommandHandler(config)

test_cmds = [
    '现在几点',
    '今天几号',
    '3加5等于几',
    '讲个笑话',
    '你会什么',
]

async def test_commands():
    for tc in test_cmds:
        handled, response = await cmd.handle(tc)
        status = 'OK' if handled else 'SKIP'
        resp_short = response[:30] + '...' if len(response) > 30 else response
        print(f'  [{status}] "{tc}" -> "{resp_short}"')

import asyncio
asyncio.run(test_commands())

# 9. 检查Agent桥接
print('\n【9. Agent桥接功能检查】')
from src.agent_bridge import AgentBridge
agent = AgentBridge(config)
print(f'  Agent启用: {agent.enabled}')
print(f'  消息文件: {agent.message_file}')
print(f'  回复文件: {agent.response_file}')

print('\n' + '=' * 50)
print('检查完成')
print('=' * 50)
