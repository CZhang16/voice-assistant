# 小白语音助手

本地语音助手，为 Boss 开发，唤醒词"小白"，女声回复。

## 功能特点

| 功能 | 说明 |
|------|------|
| 🤖 **唤醒检测** | 本地离线唤醒词"小白"，保护隐私 |
| 🎤 **语音识别** | Whisper 本地识别，无需联网 |
| 🔊 **语音合成** | Edge TTS 女声，自然流畅 |
| 💻 **本地命令** | 熄屏、锁屏、时间、计算、讲笑话 |
| 🌐 **OpenClaw 集成** | 连接 AI Agent 智能对话 |
| 🔔 **任务提醒** | 语音创建任务记录 |

## 快速开始

### 1. 安装依赖
```bash
cd C:\Users\fourStar\clawd\voice-assistant
pip install -r requirements.txt
```

### 2. 安装 ffmpeg（Whisper 需要）
```bash
winget install ffmpeg
```

### 3. 配置 Access Key
1. 访问 https://console.picovoice.ai/ 免费注册
2. 获取 Access Key
3. 填写到 `config.yaml`:
```yaml
wake_word:
  access_key: "你的Key"
```

### 4. 运行
```bash
python src/main.py
```

或使用快捷脚本：
```bash
start.bat
```

## 目录结构

```
voice-assistant/
├── src/                      # 核心源代码
│   ├── main.py              # 主程序入口
│   ├── config.py            # 配置管理
│   ├── wake_word.py         # 唤醒词检测 (Porcupine)
│   ├── stt.py               # 语音识别 (Whisper)
│   ├── tts.py               # 语音合成 (Edge TTS)
│   ├── commands.py          # 本地命令处理
│   └── agent_bridge.py     # OpenClaw 桥接
│
├── config.yaml              # 配置文件
├── requirements.txt         # Python 依赖
│
├── voice_bridge_skill.py    # OpenClaw 技能脚本
├── openclaw_voice_bridge.py # OpenClaw 桥接实现
│
├── start.bat                # 启动脚本
├── start_with_openclaw.bat  # 启动+桥接
├── run.bat                  # 运行主程序
│
├── check_status.py          # 状态检查工具
├── tests/                   # 单元测试
└── docs/                    # 详细文档
    ├── SPEC.md             # 技术规格
    └── USAGE.md            # 使用说明
```

## 配置说明

编辑 `config.yaml`:

```yaml
app:
  name: "小白"
  version: "1.0.0"

# 唤醒词配置
wake_word:
  keyword_path: "xiaobai_zh_windows.ppn"  # 唤醒词模型
  keywords: ["小白"]
  model_path: "porcupine_params_zh.pv"     # 中文模型
  sensitivity: 0.5  # 灵敏度 0.0-1.0

# 音频配置
audio:
  input_device: null  # null = 默认麦克风
  sample_rate: 16000
  frame_length: 512
  channels: 1

# 语音识别 (STT)
stt:
  engine: "whisper"   # whisper 或 azure
  model: "base"       # tiny/base/small/medium
  language: "zh"

# 语音合成 (TTS)
tts:
  voice: "zh-CN-XiaoxiaoNeural"  # 女声
  rate: "+0%"
  volume: "+0%"

# OpenClaw Agent 桥接
agent:
  enabled: true
  message_file: "C:/Users/fourStar/.openclaw/voice-messages.jsonl"

# 本地命令
commands:
  enabled: true
  keywords:
    screen_off: ["熄屏", "关闭屏幕", "关屏"]
    lock: ["锁屏", "锁定"]
    task: ["任务", "提醒", "记录"]
```

## 语音命令

| 你说 | 小白回复 | 执行动作 |
|------|---------|---------|
| "小白" | "我在" | 唤醒，等待指令 |
| "熄屏" / "关屏" | "已熄屏" | 关闭显示器 |
| "锁屏" | "已锁屏" | 锁定电脑 |
| "现在几点" | "现在是XX点XX分" | 报时 |
| "今天几号" | "今天是XXXX年XX月XX日" | 播报日期 |
| "3加5等于几" | "3 + 5 等于 8" | 简单计算 |
| "讲个笑话" | "..." | 讲笑话 |
| "提醒我下午开会" | "已记录任务：下午开会" | 创建任务 |
| [其他问题] | "..." | 发给 OpenClaw 处理 |

## OpenClaw 集成

### 工作原理
```
语音输入 → 唤醒词检测 → 语音识别 → 本地命令? 
                                              ↓ 是
                                        执行命令
                                              ↓ 否
                                   发送给 OpenClaw
                                              ↓
                                   语音合成回复
```

### 启动方式

**方式1：单独运行语音助手**
```bash
python src/main.py
```

**方式2：同时启动 OpenClaw 桥接监听**
```bash
start_with_openclaw.bat
```
这会同时运行：
1. 语音助手主程序
2. OpenClaw 消息监听（处理语音消息并回复）

**方式3：通过 heartbeat 自动处理**
在 `HEARTBEAT.md` 中配置自动检查消息队列。

### 消息协议

通过 JSONL 文件通信：
- 发送：`voice-messages.jsonl`
- 接收：`voice-messages-responses.jsonl`

## 系统要求

- Windows 10/11
- Python 3.11+
- 麦克风（录音）
- 扬声器/耳机（播放）
- 2GB+ 内存（Whisper 模型加载）

## 依赖说明

| 依赖 | 用途 |
|------|------|
| pvporcupine | 唤醒词检测 |
| pyaudio | 麦克风录音 |
| openai-whisper | 语音识别 |
| edge-tts | 语音合成 |
| pygame | 音频播放 |
| webrtcvad | 语音活动检测 |
| ffmpeg | 音频处理（Whisper 需要） |

## 故障排除

### 问题：说"小白"没反应
- 检查麦克风是否正常
- 调整 `sensitivity` 到 0.6-0.8
- 查看日志 `logs/voice-assistant.log`

### 问题：唤醒后说没听清
- 安装 ffmpeg 并加入 PATH
- 使用更大的 Whisper 模型 (`small`)
- 在更安静的环境测试

### 问题：没有声音
- 检查扬声器连接
- 确认不是静音状态

### 问题：Whisper 加载失败
- 确认 ffmpeg 已安装
- 检查网络（首次下载模型需要联网）

## 开发相关

### 运行测试
```bash
pytest tests/
```

### 查看日志
```bash
tail -f logs/voice-assistant.log
```

### 状态检查
```bash
python check_status.py
```

### 自定义唤醒词
1. 访问 https://console.picovoice.ai/porcupine
2. 创建自定义唤醒词
3. 下载 `.ppn` 文件
4. 更新 `config.yaml`

## 技术栈

- **唤醒词**: pvporcupine (Porcupine)
- **语音识别**: openai-whisper
- **语音合成**: edge-tts
- **音频处理**: pyaudio, pygame, ffmpeg
- **异步框架**: asyncio

## 许可

本项目仅供个人学习使用。