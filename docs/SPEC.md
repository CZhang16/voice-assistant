# 小白语音助手 - 技术规格文档

## 项目概述
为 Boss 开发的本地语音助手，唤醒词"小白"，女声回复，简短对话风格。

## 核心功能

### 1. 唤醒检测 (wake_word.py)
- 使用 Porcupine 本地唤醒词引擎
- 唤醒词："小白" (xiaobai)
- 完全离线，保护隐私
- 检测后播放提示音

### 2. 语音识别 (stt.py)
- 方案A: Whisper 本地运行 (推荐，需要显卡)
- 方案B: Azure Speech Service (备选，需联网)
- 语言：中文普通话
- 录音时长：自动检测语音结束（VAD）

### 3. 语音合成 (tts.py)
- 使用 Edge TTS (免费，微软在线)
- 声音："zh-CN-XiaoxiaoNeural" (女声)
- 语速：适中
- 音量：适中

### 4. OpenClaw 桥接 (agent_bridge.py)
- 通过 HTTP API 与 OpenClaw 通信
- 发送用户语音转文字
- 接收 Agent 回复
- 超时处理：30秒

### 5. 本地命令 (commands.py)
- 熄屏：`screen_off()`
- 锁屏：`lock_workstation()`
- 创建 OpenClaw 任务
- 播放音乐（可选）

### 6. 主程序 (main.py)
- 状态机：监听 → 唤醒 → 录音 → 识别 → 处理 → 回复
- 多线程/异步处理
- 异常处理
- 日志记录

## 技术栈
- Python 3.11+
- FastAPI (可选，用于远程控制)
- pvporcupine (唤醒词)
- openai-whisper (语音识别)
- edge-tts (语音合成)
- pyaudio (录音)
- pygame/simpleaudio (播放)

## 配置文件 (config.yaml)
```yaml
app:
  name: "小白"
  wake_word: "小白"
  
wake_word:
  model_path: "xiaobai.ppn"  # Porcupine 模型
  sensitivity: 0.5

stt:
  engine: "whisper"  # whisper 或 azure
  model: "base"      # tiny, base, small, medium, large
  language: "zh"
  
tts:
  voice: "zh-CN-XiaoxiaoNeural"
  rate: "+0%"
  volume: "+0%"
  
agent:
  endpoint: "http://localhost:8000/api/chat"  # OpenClaw 端点
  timeout: 30
  
commands:
  enabled: true
```

## 状态机
```
[IDLE] --(检测到唤醒词)--> [LISTENING]
[LISTENING] --(语音结束)--> [PROCESSING]
[PROCESSING] --(命令)--> [EXECUTING] --> [IDLE]
[PROCESSING] --(对话)--> [ASKING_AGENT] --> [SPEAKING] --> [IDLE]
```

## 接口定义

### AgentBridge
```python
class AgentBridge:
    async def chat(self, message: str) -> str:
        """与 OpenClaw 对话，返回回复文本"""
        pass
```

### SpeechToText
```python
class SpeechToText:
    def record(self) -> bytes:
        """录音，返回音频字节"""
        pass
    
    def transcribe(self, audio: bytes) -> str:
        """识别音频，返回文字"""
        pass
```

### TextToSpeech
```python
class TextToSpeech:
    async def speak(self, text: str):
        """朗读文本"""
        pass
```

### CommandHandler
```python
class CommandHandler:
    def handle(self, text: str) -> tuple[bool, str]:
        """
        处理命令
        返回: (是否执行了本地命令, 回复文本)
        """
        pass
```

## 测试要求
- 单元测试覆盖所有模块
- 集成测试验证完整流程
- 模拟 Agent 响应进行测试

## 代码规范
- PEP 8
- 类型注解
- 文档字符串
- 异步优先
