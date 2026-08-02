---
name: ai-video-full-pipeline
description: 全自动AI视频生成流水线 - Wan2.2动态背景 + edge-tts配音 + moviepy文字叠加 + 淡入淡出转场
---

# AI视频全自动生成流水线

三步走：**Wan2.2生成动态背景 → edge-tts生成配音 → moviepy合成文字+转场**

## 前置条件

```bash
pip3 install moviepy edge-tts numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

字体路径：`/System/Library/Fonts/STHeiti Medium.ttc`

## 步骤

### 1️⃣ 生成Wan2.2动态背景视频

**提交**：`POST https://api.siliconflow.cn/v1/video/submit`
```json
{
  "model": "Wan-AI/Wan2.2-T2V-A14B",
  "prompt": "深色科技感动态背景，深蓝到紫色渐变...竖屏9:16",
  "image_size": "720x1280"
}
```
返回 `{"requestId": "..."}`

**轮询**：`POST https://api.siliconflow.cn/v1/video/status`
```json
{"requestId": "..."}
```
轮询间隔10s，状态"Succeed"时取 `results.videos[0].url` 下载

### 2️⃣ 生成配音

```python
import asyncio, edge_tts
communicate = edge_tts.Communicate(TTS_TEXT, voice="zh-CN-XiaoxiaoNeural", rate="+15%")
asyncio.run(communicate.save("voiceover.mp3"))
```

### 3️⃣ 合成视频（moviepy v2.1.2）

核心API要点（踩坑记录）：

#### 加载背景视频
```python
from moviepy import VideoFileClip
bg = VideoFileClip("ai_generated_video.mp4")
```

#### 循环短背景
```python
bg_dur = bg_clip.duration
loops = max(1, math.ceil(duration / bg_dur))
bg_parts = [bg_clip] * loops
bg_looped = concatenate_videoclips(bg_parts, method="chain")
bg_segment = bg_looped.subclipped(0, duration).resized((W, H))
```

#### ⚠️ 淡入淡出（不要用FadeIn/FadeOut!!!）
`FadeIn/FadeOut` 与 `VideoFileClip` 有兼容问题（`NoneType object has no attribute get_frame`）。

**正确做法**：手动创建黑帧遮罩叠加
```python
import numpy as np

def make_fade_slide(bg_clip, title_text, subtitle_text, duration, fade_in=False, fade_out=False, fade_dur=0.3):
    # ... 先组装好composite slide ...
    def fade_frame(t):
        alpha = 1.0
        if fade_in and t < fade_dur:
            alpha = max(0, 1.0 - t / fade_dur)
        if fade_out and t > duration - fade_dur:
            alpha = max(0, (t - (duration - fade_dur)) / fade_dur)
        return np.full((H, W, 3), int(255 * alpha), dtype=np.uint8)
    fade_clip = VideoClip(frame_function=fade_frame, duration=duration)
    return CompositeVideoClip([composite, fade_clip], size=(W, H))
```

#### 文字位置
- 标题：居中偏上 `("center", H // 2 - 120)`
- 副标题/解说：底部 `("center", H - 180)`

#### 对齐音视频时长
```python
dur = min(video.duration, audio.duration) - 0.01
video = video.subclipped(0, dur)
audio = audio.subclipped(0, dur)
video = video.with_audio(audio)
```

#### 渲染参数（720p）
```python
video.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac",
    preset="ultrafast", bitrate="1500k", threads=4)
```
Mac i7-1068NG7上720p/38s视频渲染约4-7分钟。

## 已知问题
- Qwen-Image 生成科技感风格效果差（用户评价"太low"），不要用
- 视频渲染慢（CPU软编码），有独显机器快10倍+
- Wan2.2生成约8-9分钟（排队+推理）
- 如果有多段背景需要循环，用 `concatenate_videoclips` 先loop再subclip

## 文件位置
所有脚本和生成文件存在 `~/Desktop/hermes/`

## 参考

- **`ai-video-production` skill** — 更全面的视频生产流水线，含百炼 I2V 图生视频（¥0.06/条）+ ffmpeg CRF18 高质量合成方案

## ⚠️ 画质警告（2026-07 用户反馈）

用 moviepy `preset="ultrafast", bitrate="1500k"` 合成的视频**画质明显低于源片**。如果追求画质：
1. 用 ffmpeg 做最终合成：`-crf 18 -preset slow`（比特率 ~5800kbps）
2. macOS brew ffmpeg 没有 drawtext → 用 PIL 生成字幕 PNG + overlay 叠加
3. 详见 `ai-video-production` skill 的「ffmpeg 两段合成」章节
