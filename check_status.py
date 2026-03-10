"""
小白语音助手状态检查
"""
import sys
import os

# 设置 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\fourStar\clawd\voice-assistant')
sys.path.insert(0, r'C:\Users\fourStar\clawd\voice-assistant')

print('=== 小白语音助手 - 状态检查 ===')
print()

# 1. 检查核心依赖
print('[1. 核心依赖]')
dependencies = {
    'pvporcupine': '唤醒词引擎',
    'pyaudio': '音频输入',
    'whisper': '语音识别',
    'pygame': '音频播放',
    'edge_tts': '语音合成',
    'webrtcvad': '语音活动检测',
}

for pkg, desc in dependencies.items():
    try:
        __import__(pkg)
        print(f'  OK {pkg}: {desc}')
    except ImportError:
        print(f'  MISSING {pkg}: {desc}')

# 2. 检查配置文件
print()
print('[2. 配置检查]')
from src.config import Config
config = Config()
name = config.get("app.name")
keywords = config.get("wake_word.keywords")
has_key = config.get("wake_word.access_key")
access_key_ok = "OK" if has_key else "Missing"
model_file = config.get("wake_word.keyword_path") or "Built-in"
tts_voice = config.get("tts.voice")
stt_engine = config.get("stt.engine")
print(f'  App: {name}')
print(f'  Wake word: {keywords}')
print(f'  Access Key: {access_key_ok}')
print(f'  Model file: {model_file}')
print(f'  TTS voice: {tts_voice}')
print(f'  STT engine: {stt_engine}')

# 3. 检查模型文件
print()
print('[3. 模型文件]')
import os
ppn_file = config.get('wake_word.keyword_path')
if ppn_file and os.path.exists(ppn_file):
    size = os.path.getsize(ppn_file)
    print(f'  OK {ppn_file}: {size} bytes')
else:
    msg = '  WARNING: Model file not found (' + str(ppn_file) + ')'
    print(msg)

# 4. 检查 Porcupine 模型语言
print()
print('[4. Porcupine 模型语言]')
import pvporcupine
model_path = os.path.join(os.path.dirname(pvporcupine.__file__), 'lib', 'common', 'porcupine_params.pv')
if os.path.exists(model_path):
    print(f'  Default model: {model_path}')
    print(f'  Language: English (en)')
    print(f'  NOTE: Chinese wake word needs porcupine_params_zh.pv')

# 5. 测试唤醒词初始化
print()
print('[5. 唤醒词测试]')
try:
    access_key = config.get('wake_word.access_key')
    porcupine = pvporcupine.create(
        access_key=access_key,
        keywords=['computer']
    )
    print(f'  OK Porcupine initialized: {porcupine.sample_rate}Hz')
    porcupine.delete()
except Exception as e:
    print(f'  ERROR: {e}')

# 6. 测试麦克风
print()
print('[6. 麦克风检查]')
try:
    import pyaudio
    pa = pyaudio.PyAudio()
    info = pa.get_default_input_device_info()
    info_name = info["name"]
    print(f'  OK Default mic: {info_name}')
    pa.terminate()
except Exception as e:
    print(f'  ERROR: {e}')

print()
print('=== 检查完成 ===')
