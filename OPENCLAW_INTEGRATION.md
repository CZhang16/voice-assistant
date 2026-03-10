# 小白语音助手 - OpenClaw 集成说明

## 架构

```
用户语音 → 小白语音助手 → OpenClaw Bridge → OpenClaw AI → 语音回复
                ↓
          本地命令（熄屏、锁屏等）
```

## 文件说明

| 文件 | 功能 |
|------|------|
| `src/agent_bridge.py` | 语音助手端桥接（发送/接收消息） |
| `voice_openclaw_bridge.py` | OpenClaw 端处理（AI回复） |
| `start_with_openclaw.bat` | 一键启动脚本 |

## 启动方式

### 方式1：一键启动（推荐）
```bash
start_with_openclaw.bat
```
这会同时启动：
1. OpenClaw 消息处理器
2. 小白语音助手

### 方式2：分别启动
终端1 - OpenClaw 桥接：
```bash
python voice_openclaw_bridge.py
```

终端2 - 小白语音助手：
```bash
set PYTHONPATH=C:\Users\fourStar\clawd\voice-assistant
python src/main.py
```

## 使用流程

1. **唤醒** - 说 "小白"
2. **听到** - "我在"
3. **说话** - 任意指令或问题
4. **处理** - 本地命令直接执行，其他发给 OpenClaw
5. **回复** - 语音播报结果

## 支持的功能

### 本地命令（无需联网）
- 熄屏/锁屏
- 时间/日期查询
- 简单计算
- 任务记录
- 讲笑话

### OpenClaw 命令（需要桥接运行）
- 股票查询
- 健身数据
- 天气信息
- 任意问答

## 消息文件

- `~/.openclaw/voice-messages.jsonl` - 语音→OpenClaw
- `~/.openclaw/voice-messages-responses.jsonl` - OpenClaw→语音

## 扩展 OpenClaw 回复

编辑 `voice_openclaw_bridge.py` 中的 `generate_reply()` 方法：

```python
async def generate_reply(self, message: str) -> str:
    # 添加新的关键词回复
    if "你的关键词" in message:
        return "你的回复"
    # ...
```
