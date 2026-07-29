# 语音交互完整搭建笔记 (Linux / Tencent Cloud)

## 环境

- 腾讯云轻量服务器 (Ubuntu)
- Hermes Agent (DeepSeek V4-Flash)
- 飞书 (Feishu) 通道

## 语音输入 (STT)

**已装组件**：
- `faster-whisper` (1.2.1) — CPU int8模式
- 模型: `Systran/faster-whisper-tiny` (从 HF mirror 下载)
- 脚本: `~/.hermes/skills/media/voice-input/scripts/transcribe_linux.py`

**模型首次下载** (HF mirror，国内必用)：
```bash
export HF_ENDPOINT=https://hf-mirror.com
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('Systran/faster-whisper-tiny')
"
```

**测试命令**：
```bash
python3 ~/.hermes/skills/media/voice-input/scripts/transcribe_linux.py input.wav --model tiny
```

## 语音输出 (TTS)

### 方案A：edge-tts（Microsoft，质量好但国内网络不稳定）

```bash
pip install edge-tts --break-system-packages
edge-tts --text "你好" --voice zh-CN-YunxiNeural --write-media out.mp3
```

**坑**：从中国服务器连接 MS Edge TTS 间歇性不可用 (`NoAudioReceived` 错误)。重试2-3次通常能通。

### 方案B：espeak-ng（离线，纯合成音，适合机械声）

```bash
sudo apt-get install espeak-ng
espeak-ng "星刃启动完毕" -v cmn -p 60 -s 140 -g 10 -w out.wav
```

**中文发音**：基于拼音合成，不如 edge-tts 自然。

## 机械音效果 (ffmpeg)

将普通TTS转换为机器人/星刃风格声音的三段式管线：

```bash
# 1. 生成原始语音 (edge-tts男声或espeak-ng)
edge-tts --text "星刃启动完毕" --voice zh-CN-YunxiNeural --write-media raw.mp3

# 2. ffmpeg 机械效果 (lowpass + aphaser + echo)
ffmpeg -y -i raw.mp3 \
  -af "lowpass=f=2500,aphaser=0.5:0.6,aecho=0.6:0.4:35:0.25,volume=2.0" \
  -codec:a libmp3lame -b:a 128k \
  final_robot.mp3
```

### 参数说明

| 滤镜 | 作用 | 参数解释 |
|------|------|----------|
| `lowpass=f=2500` | 切除高频，制造沉闷机械感 | 2500Hz以下保留 |
| `aphaser=0.5:0.6` | 相位调制，产生合成器声波效果 | in_gain=0.5, out_gain=0.6 |
| `aecho=0.6:0.4:35:0.25` | 金属感回响 | 延迟35ms，衰减0.25 |
| `volume=4.0` | 音量增益 | 补偿滤波后的音量损失（`volume=2.0`偏小，用户反馈过） |
| `loudnorm=I=-16:LRA=11:TP=-1.5` | 响度归一化 | 统一输出音量，避免忽大忽小 |

### 完整经过验证的管线

```bash
edge-tts --text "星刃启动完毕" --voice zh-CN-YunxiNeural --write-media raw.mp3
ffmpeg -y -i raw.mp3 \
  -af "lowpass=f=2500,aphaser=0.5:0.6,aecho=0.6:0.4:35:0.25,volume=4.0,loudnorm=I=-16:LRA=11:TP=-1.5" \
  -codec:a libmp3lame -b:a 128k \
  final_robot.mp3
```

### ffmpeg版本兼容性

Ubuntu 24.04 自带 ffmpeg 6.1.1，`aphaser` 只支持 `in_gain` 和 `out_gain` 参数（`type/t/decay/delay/speed` 不可用）。如果要用高级相位参数，需自行编译或升级ffmpeg。

