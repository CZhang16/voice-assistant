# 使用说明

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 获取 Porcupine Access Key
1. 访问 https://console.picovoice.ai/
2. 注册免费账号
3. 复制 Access Key
4. 粘贴到 `config.yaml` 的 `wake_word.access_key`

### 3. 运行
```bash
python src/main.py
```

## 使用语音

| 你说 | 小白回复 | 执行动作 |
|------|---------|---------|
| "小白" | "我在" | 唤醒，等待指令 |
| "熄屏" | "已熄屏" | 关闭显示器 |
| "锁屏" | "已锁屏" | 锁定电脑 |
| "提醒我下午开会" | "已记录任务：下午开会" | 创建提醒 |
| "今天股票怎么样" | "正在查询..." | 发给 Agent 处理 |

## 常见问题

### 听不到唤醒词
- 检查麦克风是否选中
- 调整 `config.yaml` 中的 `wake_word.sensitivity`（0.0-1.0）

### 识别不准确
- 在安静环境使用
- 调整录音参数
- 更换 Whisper 模型（tiny/base/small）

### 没有声音
- 检查扬声器/耳机
- 检查 Pygame 初始化是否成功

## 高级配置

编辑 `config.yaml`:

```yaml
stt:
  model: "small"  # 更大模型 = 更准确但更慢
  
tts:
  voice: "zh-CN-XiaoxiaoNeural"  # 女声
  # 可选：zh-CN-YunxiNeural (男声)
```
