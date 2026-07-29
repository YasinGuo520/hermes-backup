---
name: ai-video-production
description: 全自动AI视频生产流水线——使用本地Python工具（moviepy + edge-tts + ffmpeg）从文案到成品MP4的端到端自动化。无需GPU，无需云API。适用于抖音带货素材、知识科普、工具测评等竖屏短视频。
triggers:
  - AI视频生成
  - 自动视频
  - 视频合成
  - moviepy
  - edge-tts
  - TTS配音
  - 竖屏视频
  - Python视频
  - 文字转视频
  - 带货视频
related:
  - ai-video-content-creation  # 互补技能：云端AI视频平台生成
platforms: [macos, linux]
---

# AI Video Production（全自动AI视频生产流水线）

使用本地 Python 工具（moviepy + edge-tts + ffmpeg）从文案到成品 MP4 的端到端自动化流水线。**无需 GPU，无需云 API 调用**，全在本机运行。

**适用范围：** 抖音带货视频、AI工具测评、知识科普、产品介绍等竖屏短视频。

**与 `ai-video-content-creation` 的关系：** 互补。该技能走云端AI平台（小云雀/即梦），本技能走本地Python全自动。前者适合高质量视觉素材，后者适合快速、低成本、可批量生产的内容。

---

## 流水线架构

```
┌──────────────────────────────────────────────────────┐
│               AI 视频生产流水线                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Hermes (我)            工具             输出           │
│  ──────────────────────────────────────────────       │
│  ① 写文案 + 分镜        —              → 脚本文本     │
│  ② 生成幻灯片    →  moviepy.TextClip   → PNG帧        │
│  ③ 生成配音      →  edge-tts(Python)   → MP3语音      │
│  ④ 合成视频      →  moviepy + ffmpeg   → MP4成品      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 前置依赖

```bash
# 必装
pip3 install moviepy pydub edge-tts numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# ffmpeg 需已安装（macOS 可 brew install ffmpeg）
which ffmpeg
```

**注意：** 用 `pip3` 而非 `pip`，确保与 `python3` 对应。如遇 `ModuleNotFoundError`，在脚本头加：
```python
import sys, site
sys.path.insert(0, site.getusersitepackages())
```

---

## 核心工作流

### 1. 文案 & 分镜设计

写脚本时按「镜头」划分，每个镜头指定：**时长 + 画面描述 + 配音文案**。

**分镜模板：**

| # | 时间 | 画面 | 文案 |
|---|------|------|------|
| 1 | 0-5s | 标题封面，大字标题+小字副标题 | (无/开场白) |
| 2 | 5-10s | 痛点画面，问题描述 | "你花3小时做XX？..." |
| 3 | 10-16s | 方案介绍，工具/产品展示 | "今天测评这个..." |
| 4 | 16-24s | 步骤说明，分步卡片 | "怎么用？三步..." |
| 5 | 24-30s | 对比/效果展示 | "以前...现在..." |
| 6 | 30-35s | 结果验证 | "关键是真的能落地..." |
| 7 | 35-45s | CTA关注 | "关注我，下期..." |

**文案要求：**
- 配音语速按 **260-280字/分钟** 估算
- 45秒视频 ≈ 180-220字
- 段落之间留自然停顿

### 2. 生成幻灯片（moviepy TextClip）

**重要：moviepy 2.x API 与 1.x 差异较大，以下为 2.x 正确用法。**

```python
from moviepy import VideoClip, TextClip, CompositeVideoClip

W, H = 720, 1280  # 竖屏 9:16

def solid_bg(color):
    """返回纯色帧函数 — frame_function 参数名！"""
    def make_frame(t):
        import numpy as np
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:] = color
        return frame
    return make_frame

# 创建背景
bg = VideoClip(frame_function=solid_bg((18, 18, 30)), duration=5.0)

# 创建文字
title = TextClip(
    text="标题文字",
    font="/System/Library/Fonts/STHeiti Medium.ttc",  # macOS中文字体
    font_size=52,          # 720p 下 52pt 合适
    color="white",
    stroke_color="#6C63FF",
    stroke_width=1,
    size=(W - 120, None),  # 左右留边距
    method="caption",       # 2.x 用 caption 而非 label
    text_align="center",
).with_duration(5.0).with_position(("center", H // 2 - 80))

# 合成
composite = CompositeVideoClip([bg, title], size=(W, H))
```

**关键 API 差异（2.x vs 1.x）：**

| 概念 | 1.x | 2.x |
|------|-----|-----|
| 帧函数参数 | `make_frame` | `frame_function` |
| 帧返回值 | tuple `(0,0,0)` | numpy array `np.zeros((H,W,3))` |
| TextClip.text | `txt` 参数 | `text` 参数 |
| TextClip.method | `label`(默认) | `caption`(推荐，自动换行) |
| 设置时长 | 构造时传 | `.with_duration(n)` |
| 设置位置 | 构造时传 | `.with_position(x, y)` |
| 截取片段 | `.subclip(s, e)` | `.subclipped(s, e)` |
| 合并视频 | `concatenate_videoclips` | 同名但 method='compose' |
| 加音频 | `.set_audio(a)` | `.with_audio(a)` |

### 3. 生成配音（edge-tts）

```python
import edge_tts, asyncio

communicate = edge_tts.Communicate(
    "配音文本内容",
    voice="zh-CN-XiaoxiaoNeural",  # 中文女声，自然清晰
    rate="+15%",   # 语速加快15%（适配短视频节奏）
    pitch="+0Hz"
)
asyncio.run(communicate.save("/path/to/output.mp3"))
```

**推荐中文语音选项：**

| 语音 | 性别 | 风格 | 适合场景 |
|------|------|------|---------|
| `zh-CN-XiaoxiaoNeural` | 女 | 自然亲切 | **通用推荐** |
| `zh-CN-YunxiNeural` | 男 | 活力 | 测评/科技 |
| `zh-CN-YunjianNeural` | 男 | 专业 | 知识科普 |
| `zh-CN-XiaoyiNeural` | 女 | 活泼 | 带货/种草 |

### 4. 合成视频（带音频对齐）

```python
from moviepy import AudioFileClip

audio = AudioFileClip("voiceover.mp3")
video = concatenate_videoclips(slides, method="compose")

# 对齐时长
final_dur = min(video.duration, audio.duration)
video = video.subclipped(0, final_dur)
audio = audio.subclipped(0, final_dur)
video = video.with_audio(audio)

# 输出
video.write_videofile(
    "output.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    preset="ultrafast",  # 无独显机器用 ultrafast
    bitrate="1500k",
    threads=4,
)
```

---

## 性能优化（Intel Mac 无独显）

| 优化项 | 建议值 | 效果 |
|--------|--------|------|
| 分辨率 | 720×1280（非1080p） | 帧数减少55% |
| 编码预设 | `ultrafast`（非 medium） | 速度提升3-5倍 |
| 码率 | 1500k（非 3000k） | 渲染更快，文件更小 |
| 帧率 | 24fps | 够用 |
| 线程数 | 4（i7 4核8线程） | 充分利用CPU |

**实测数据（MacBook i7-1068NG7）：**
- 1080p medium → ~1.1fps 渲染，~18分钟/50秒视频
- 720p ultrafast → ~2.7fps 渲染，~6.5分钟/50秒视频（包含语音生成时间）

---

## macOS 字体注意

| 字体路径 | 支持中文 | 说明 |
|---------|:-------:|------|
| `/System/Library/Fonts/STHeiti Medium.ttc` | ✅ | **推荐**，简化字，粗体适中 |
| `/System/Library/Fonts/PingFang.ttc` | ✅ | 但 PIL/ImageFont 可能报错 |
| `/Library/Fonts/Arial Unicode.ttf` | ✅ | 可用但字形较老 |
| `/System/Library/Fonts/Hiragino Sans GB.ttc` | ✅ | 细体，适合副标题 |

**PingFang.ttc 报错解决：** 如果报 `cannot open resource`，换用 `STHeiti Medium.ttc`。`.ttc` 是集合字体格式，PIL 不一定能打开所有索引。

---

### 字幕/副标题位置规则（用户偏好）

| 元素 | 位置 | 说明 |
|------|------|------|
| **主标题** | `(center, H//2 - 120)` | 居中偏上 |
| **副标题/解说文字** | `(center, H - 180)` | **底部**，不要放中间 |

### 程序化渐变背景（AI生图质量不足时的回退方案）

当用户反馈「图太low了」「没有科技感」时，**立即切换到此方案**，不要继续优化AI生图提示词。

```python
def gradient_bg(color_top, color_bot):
    def make_frame(t):
        import numpy as np
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            ratio = y / H
            frame[y, :] = [
                int(color_top[0]*(1-ratio) + color_bot[0]*ratio),
                int(color_top[1]*(1-ratio) + color_bot[1]*ratio),
                int(color_top[2]*(1-ratio) + color_bot[2]*ratio),
            ]
        return frame
    return make_frame
```

推荐配色（科技深色主题）：

| 场景 | 顶色(RGB) | 底色(RGB) | 风格 |
|------|-----------|-----------|------|
| 标题/开场 | (10,10,50) | (40,10,80) | 蓝紫科技 |
| 痛/警告 | (50,10,10) | (80,20,20) | 红强调 |
| 工具/产品 | (10,20,60) | (20,40,100) | 蓝光 |
| 步骤/教程 | (10,10,40) | (30,20,70) | 紫蓝 |
| 对比 | (40,10,10) | (10,40,10) | 红→绿 |
| 结果/肯定 | (10,30,20) | (20,60,40) | 绿科技 |
| CTA/关注 | (20,10,50) | (50,20,90) | 紫发光 |

### ⚠️ VideoFileClip + 淡入淡出不兼容

永远不要对包含 VideoFileClip 的 CompositeVideoClip 应用 FadeIn/FadeOut。会导致：
```
AttributeError: 'NoneType' object has no attribute 'get_frame'
```

原因：FadeIn/FadeOut 创建 mask 触发 clip 变换，VideoFileClip reader 在复合剪辑中被关闭。

正确做法有两个：

#### 方案A：硬切（最稳）

循环短视频做背景，直接拼接硬切：

```python
def make_slide(bg_clip, title_text, subtitle_text, duration):
    bg_dur = bg_clip.duration
    loops = max(1, math.ceil(duration / bg_dur))
    parts = [bg_clip] * loops
    bg_looped = concatenate_videoclips(parts, method="chain")
    bg_segment = bg_looped.subclipped(0, duration).resized((W, H))
    # ... 叠加文字 ...
    return CompositeVideoClip(clips, size=(W, H))
```

#### 方案B：交叉溶解 CrossFadeIn（推荐，平滑过渡）

**已验证可用。** `CrossFadeIn` 来自 `moviepy.video.fx`，与 VideoFileClip 兼容：

```python
from moviepy.video.fx import CrossFadeIn

slides = [...]  # 所有分镜已完成

OVERLAP = 0.3  # 重叠时长（秒）
composite_clips = []
current_t = 0.0
for i, s in enumerate(slides):
    if i > 0:
        # 第二帧开始加 CrossFadeIn 渐显
        s = s.with_effects([CrossFadeIn(OVERLAP)])
    composite_clips.append(s.with_start(current_t))
    current_t += s.duration - OVERLAP

video = CompositeVideoClip(composite_clips, size=(W, H))
video = video.with_duration(current_t + slides[-1].duration)
```

**原理：** 两帧重叠 OVERLAP 秒，上一帧渐隐的同时下一帧渐现。不经过黑屏，画面连续。

**注意事项：**
- `CrossFadeIn` 只影响叠加层中靠后的帧，前一帧（无 CrossFadeIn）维持原透明度
- 第一帧不加 CrossFadeIn（直接显示），最后一帧不特殊处理（自然结束）
- 最终视频总时长 = 所有分镜时长之和 - (分镜数-1) × OVERLAP
- 不要混合使用 FadeIn/FadeOut + CrossFadeIn — 两者生效机制冲突

### Wan2.2视频作为动态背景

流程：
1. 调SiliconFlow Wan2.2 T2V生成氛围视频（约5秒竖屏）
2. 循环该视频至所需总时长
3. 作为背景叠加文字和配音

详见 `references/wan-t2v-pipeline.md`

### 🧠 重要：先用 LLM 生成视频脚本/配音文案

**不要硬编码配音词。** 用户明确要求用 LLM 生成脚本。每次做带货视频前：

1. 根据品牌/产品/目标用户上下文，用 LLM 生成 3-4 句配音文案
2. 同步设计字幕时间轴（每句对应哪段画面、什么时候出现）
3. 让用户确认文案后再生成 TTS

**推荐长度：** 8-10秒视频≈3-4句，每句 8-15 字。edge-tts 语速 +10%~+15%。

## 百炼 I2V 图生视频管线（实拍产品 → AI动效）

当你有 **实拍产品照片** 需要做成动态视频时，走阿里百炼 DashScope API 做 I2V。
**优势：** 产品100%一致（实拍图），成本极低（¥0.06/条），5秒出片。市面上最便宜的图生视频方案。

### 前置条件

```bash
export DASHSCOPE_API_KEY="sk-xxx"
# bl CLI 需已安装（pip3 install bailian）
which bl
```

### 三步流程

#### 1️⃣ 上传产品图片到临时存储

```bash
bl file upload --file /path/to/product.jpg --model happyhorse-1.1-i2v --output json
```

返回 `{"url": "oss://dashscope-instant/...", "model": "happyhorse-1.1-i2v"}`。有效期 48 小时，`bl` CLI 自动处理 `X-DashScope-OssResourceResolve` header。

#### 2️⃣ 生成 I2V 视频（不同镜头变化产多条）

```bash
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "oss://dashscope-instant/..." \
  --prompt "Slow push-in camera movement, model looking at camera, elegant commercial fashion, smooth cinematic motion" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face" \
  --resolution "720P" \
  --ratio "9:16" \
  --duration 5 \
  --watermark false \
  --download /path/output.mp4 \
  --output json
```

**提示词示例（不同镜头变化）：**

| 镜头类型 | 提示词关键词 | 适合 |
|----------|-------------|------|
| 慢推进 | `Slow push-in camera, zoom in, product comes into focus` | 开场/产品特写 |
| 上移 | `Camera panning upward from waist to face` | 产品展示引导 |
| 转身 | `Model turns from side to face camera, hair flows naturally` | 多角度展示 |
| 环绕 | `Slow camera orbit around subject, 360 view` | 全方位展示 |

#### 3️⃣ 多条 I2V 片段 + 交叉淡化合成成片

```python
from moviepy import VideoFileClip, CompositeVideoClip, vfx

clips = [
    VideoFileClip("v2_pan_up.mp4").subclipped(0, 3),
    VideoFileClip("v3_turn.mp4").subclipped(0, 3),
    VideoFileClip("v1_push_in.mp4").subclipped(0, 3),
]

FADE = 0.5
layers = []
t = 0.0

for i, clip in enumerate(clips):
    if i == 0:
        c = clip.with_effects([vfx.FadeIn(FADE)])
        layers.append(c.with_start(t))
    elif i == len(clips) - 1:
        c = clip.with_effects([vfx.FadeIn(FADE), vfx.FadeOut(FADE)])
        layers.append(c.with_start(t - FADE))
    else:
        c = clip.with_effects([vfx.FadeIn(FADE), vfx.FadeOut(FADE)])
        layers.append(c.with_start(t - FADE))
    t += clip.duration

total_dur = sum(c.duration for c in clips) - FADE * (len(clips) - 1)
video = CompositeVideoClip(layers + text_clips, size=clips[0].size)
video = video.with_duration(total_dur).with_audio(voiceover_audio)
```

**原理：** 后一段 start 时间减去 FADE 秒重叠上一段，前一段淡出的同时后一段淡入，形成平滑交叉淡化。

### ⚠️ 成品画质警告：moviepy 合成后画质会下降

用 moviepy `CompositeVideoClip` + `write_videofile` 合成的视频画质**明显低于单条 I2V 源片**。原因：
- moviepy 每次合成都要重新编码全部帧（包括没变化的部分）
- `preset="ultrafast"` + `bitrate="1500k"` 压得不够，细节全丢
- **用户明确反馈过这个问题**（"成片的清晰度没有生成片段好"）

**补救方案：两段 ffmpeg 直出（保留画质）**

两段法：Pass 1 做交叉淡化，Pass 2 叠加字幕+配音。ffmpeg + CRF 18（视觉无损），不要用 moviepy 做最后合成。

#### Pass 1：ffmpeg xfade 交叉淡化

```python
import subprocess

DUR, FADE = 3.0, 0.5
W, H = 832, 1108
CLIPS = ["clip1.mp4", "clip2.mp4", "clip3.mp4"]

f1 = (
    f"[0:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
    f"[1:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
    f"[2:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v2];"
    f"[v0][v1]xfade=transition=fade:duration={FADE}:offset=2.5[t1];"
    f"[t1][v2]xfade=transition=fade:duration={FADE}:offset=5.0[vout]"
)

subprocess.run([
    "ffmpeg", "-i", CLIPS[0], "-i", CLIPS[1], "-i", CLIPS[2],
    "-filter_complex", f1, "-map", "[vout]",
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-pix_fmt", "yuv420p", "-r", "24", "-an", "-y", "temp_crossfade.mp4"
], check=True)
```

**参数说明：**
- `crf 18`：视觉无损（软件编码器恒定质量模式），成品比特率约 5000-6000kbps
- `preset slow`：压缩效率高，Intel Mac i7 渲染速度约 25fps（8秒视频≈8秒完成）
- `-an`：Pass 1 不要音频，Pass 2 再加

**xfade offset 计算公式（3段通用）：**
```python
CLIP_DUR = (VOICE_DUR + FADE * (NUM_CLIPS - 1)) / NUM_CLIPS
# xfade1: 第1→2段过渡，offset = CLIP_DUR - FADE
# xfade2: 第2→3段过渡，offset = CLIP_DUR * 2 - FADE * 2
# 例: CLIP_DUR=4.0, FADE=0.5 → xfade1_offset=3.5, xfade2_offset=7.0
```
确保 `CLIP_DUR * NUM_CLIPS - FADE * (NUM_CLIPS - 1) >= VOICE_DUR`。

#### Pass 2：PIL 字幕图 + ffmpeg overlay（避开 macOS ffmpeg 无 drawtext）

**macOS brew 安装的 ffmpeg 默认没有 `drawtext` 和 `subtitles` 滤镜。** 不要尝试用 `drawtext`，会报 `No such filter: 'drawtext'`。

正确做法：用 PIL 生成透明 PNG 字幕图 → ffmpeg `overlay` 叠加。

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 832, 1108
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
FPS = 24
OUTPUT = "final_hq.mp4"

# 1. 生成字幕图（每段字幕区域一张透明PNG）
subs = [
    ("CHAOKE 潮客摄影", "专注内衣视觉定制", 0.0, 3.0),
    ("专业级光影质感", "每一帧都是大片", 3.0, 6.0),
    ("让您的品牌", "在镜头前惊艳绽放", 6.0, 8.5),
    ("您的品牌视觉合伙人", None, 8.5, 10.0),
]

import os
os.makedirs("_subs", exist_ok=True)
sub_files = []
for i, (l1, l2, start, end) in enumerate(subs):
    lines = [l for l in [l1, l2] if l]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y_base = int(H * 0.85)
    for j, line in enumerate(lines):
        fs = 34 if (j == 0 and "CHAOKE" in line) else (30 if j == 0 else 28)
        font = ImageFont.truetype(FONT, fs)
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x, y = (W - tw) // 2, y_base + j * 40
        for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,200))
        draw.text((x, y), line, font=font, fill=(255,255,255,255))
    path = f"_subs/sub_{i}.png"
    img.save(path)
    sub_files.append({"path": path, "start": start, "end": end, "dur": end - start})

# 2. ffmpeg overlay 链：每张图用 -loop 1 -t <dur> 循环指定时长
import subprocess, json

inputs = ["ffmpeg", "-i", "temp_crossfade.mp4", "-i", "voiceover.mp3"]
for sf in sub_files:
    inputs.extend(["-loop", "1", "-t", str(sf["dur"]), "-i", sf["path"]])

# 构建 overlay 链（用 enable='between(t,start,end)' 控制显示时间）
prev = "0"
filter_parts = []
for i, sf in enumerate(sub_files):
    img_idx = i + 2
    src_ref = f"[{prev}:v]" if prev.isdigit() else f"[{prev}]"
    enable = f"between(t,{sf['start']},{sf['end']})"
    label = f"t{i+1}" if i < len(sub_files) - 1 else "vout"
    filter_parts.append(f"{src_ref}[{img_idx}:v]overlay=format=auto:enable='{enable}'[{label}]")
    prev = label

cmd = inputs + [
    "-filter_complex", ";".join(filter_parts),
    "-map", "[vout]", "-map", "1:a",
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-shortest", "-y", OUTPUT,
]
subprocess.run(cmd, check=True)
```

**最终输出参数：** CRF 18 + preset slow ≈ 5500-5800kbps，画质接近源片。对比 moviepy ultrafast 2500kbps 提升明显。

#### 出画质对比

| 方案 | 编码预设 | 比特率 | 文件大小(8s) | 画质 |
|------|---------|--------|------------|------|
| moviepy ultrafast 2500k | ultrafast | ~2500kbps | 2.4MB | ❌ 细节丢失 |
| ffmpeg CRF18 slow | slow | ~5800kbps | 5.6MB | ✅ 接近源片 |

### ⚠️ 配音时长匹配视频长度（重要坑点）

**不要硬算视频时长。** 配音生成后才能知道确切长度。步骤：

1. 先生成配音 → edge-tts 出 MP3
2. 用 `ffprobe -v quiet -show_format voiceover.mp3 | grep duration` 测时长
3. 根据配音时长反推每段视频截取长度：
   - `clip_dur = (voice_dur + FADE * (NUM_CLIPS - 1)) / NUM_CLIPS`
   - 确保 `clip_dur * NUM_CLIPS - FADE * (NUM_CLIPS - 1) >= voice_dur`
4. 配音时长 > 视频时长 = 文案被吞。**这是用户最反感的低级错误。**

### 背景音乐生成（ffmpeg lavfi）

最终合成前用 ffmpeg 工具生成简单的环境音 BGM，不要空手出片。

生成3层 BGM（220Hz pad + 330Hz pad + 粉噪）：
```bash
ffmpeg -f lavfi -i "sine=frequency=220:duration=10,volume=0.15" \
  -f lavfi -i "sine=frequency=330:duration=10,volume=0.08" \
  -f lavfi -i "anoisesrc=d=10:c=pink:a=0.02" \
  -filter_complex "[0:a][1:a][2:a]amix=inputs=3:duration=first[BGM]" \
  -map "[BGM]" -y bgm.mp3
```

混音：BGM 25% + 配音 100% + 300ms 延时起步（不压人声）：
```bash
ffmpeg -i bgm.mp3 -i voiceover.mp3 \
  -filter_complex \
  "[0:a]volume=0.3[bg];[1:a]adelay=300|300[voice];[bg][voice]amix=inputs=2:duration=first:weights=0.25 1[out]" \
  -map "[out]" -y mixed.mp3
```

**费用参考**

| 项目 | 费用 |
|------|------|
| bl I2V (happyhorse-1.1-i2v) | **¥0.06/条** |
| bl file upload | ¥0 |
| edge-tts 配音 | ¥0 |
| SiliconFlow Wan2.2-I2V（对比） | $0.21-0.29/条 ≈¥1.5-2.1 |

**并发生成多条 I2V（推荐）：** 百炼单条生成约 30-60 秒，顺序跑3条要3分钟。
后台并行跑（`&` + `wait`）压缩到1分钟：
```bash
bl video generate --model happyhorse-1.1-i2v --image "oss://..." \
  --prompt "Slow push-in camera, elegant commercial fashion" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download clip1.mp4 --output json &
bl video generate --model happyhorse-1.1-i2v --image "oss://..." \
  --prompt "Camera panning upward from waist to face" \
  --download clip2.mp4 --output json &
bl video generate --model happyhorse-1.1-i2v --image "oss://..." \
  --prompt "Model turns from side to face camera, hair flows naturally" \
  --download clip3.mp4 --output json &
wait
echo "全部生成完成"
```

### 核心原则：产品必须实拍，不要 AI 生

**不要用 AI 生成产品图再转视频。** AI 生图的产品细节（标签文字、包装颜色、logo）必跑偏，带货挂小黄车退货率炸。

正确管线：
```
实拍产品照 → bl upload → bl video generate（多条不同镜头）
→ moviepy 合成 + 配音 + 字幕 → 带货视频成品
```

详见 `references/bailian-i2v-session.md` 和 `references/jianying-capcut-compatibility.md`。

## 🚀 执行清单 Cheat Sheet（一条接一条）

从拿到产品图到出片，按顺序执行：

### 步骤1：生成配音文案（LLM）
```
当前模型生成 3-4 句脚本 → 让用户确认 → edge-tts 出 MP3
```

### 步骤2：上传产品图 → 生成3条I2V动态
```bash
# 上传图片
bl file upload --file product.jpg --model happyhorse-1.1-i2v --output json
# 记住返回的 oss://... URL

# 并发生成3条不同镜头（并行执行不排队）
bl video generate --model happyhorse-1.1-i2v --image "oss://..." \
  --prompt "Slow push-in camera, elegant commercial fashion" \
  --negative-prompt "Disfigured, deformed, blurry" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download clip1.mp4 --output json &

bl video generate --model happyhorse-1.1-i2v --image "oss://..." \
  --prompt "Camera panning upward from waist to face" \
  ... --download clip2.mp4 &

bl video generate --model happyhorse-1.1-i2v --image "oss://..." \
  --prompt "Model turns from side to face camera" \
  ... --download clip3.mp4 &

wait  # 等全部完成
```

### 步骤3：测配音时长
```bash
ffprobe -v quiet -show_format voiceover.mp3 | grep duration
# → duration=9.936000
```

### 步骤4：根据配音时长计算每段截取长度
```python
VOICE_DUR = 9.94  # 上一步测出
FADE = 0.5
NUM_CLIPS = 3
# clip_dur * 3 - FADE * 2 >= VOICE_DUR
CLIP_DUR = (VOICE_DUR + FADE * (NUM_CLIPS - 1)) / NUM_CLIPS
# → 约 3.65 秒/段
```

### 步骤5：Pass 1 — ffmpeg xfade 交叉淡化
```bash
# xfade offset 公式：
# xfade1_offset = CLIP_DUR - FADE
# xfade2_offset = CLIP_DUR * 2 - FADE * 2
# 3段 = 2个xfade
```

参考上节「Pass 1：ffmpeg xfade 交叉淡化」完整命令。

### 步骤6：Pass 2 — PIL字幕图 + ffmpeg overlay + BGM + 配音混音

参考上节「Pass 2」「背景音乐生成」「配音时长匹配」三段内容合成最终视频。

## 常见坑点

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'moviepy'` | Python 路径问题 | 脚本头加 `sys.path.insert(0, site.getusersitepackages())` |
| `tuple' object has no attribute 'shape'` | frame 函数返回了 tuple 而非 numpy array | 返回 `np.zeros((H,W,3), dtype=np.uint8)` |
| `Invalid font ... cannot open resource` | PIL 无法打开 .ttc 字体 | 换用 `STHeiti Medium.ttc` |
| `end_time should be smaller or equal to the clip's duration` | audio/video 时长差太小 | 用 `min(dur1, dur2)` 统一裁剪 |
| TTS 无输出/报错 | edge-tts 网络问题 | 重试，或检查 `voice` 参数名 |
| `No such filter: 'drawtext'` | macOS brew ffmpeg 默认不含 drawtext 滤镜 | 不要尝试用 drawtext。改走 PIL 生成字幕 PNG + ffmpeg overlay 叠加 | | 1080p + medium preset | 降为 720p + ultrafast |
| background 进程报 `ModuleNotFoundError` | 后台进程 PYTHONPATH 不同 | 用 foreground 终端执行 |
| 视频突然出声 | Camofox 自动播放 | 打 firefoxUserPrefs 静音补丁（见 hermes-china-setup） |

---

## 剪映/CapCut 渲染备选（jianying-editor-skill）

### ⚠️ 版本兼容性：只支持 ≤5.9 ⚠️

**剪映 10.x+ 已加密 draft_info.json（纯二进制），整个 skill 完全不可用。** 必须用 5.9 或更低版本。详见 `references/jianying-capcut-compatibility.md`。

当用户有 **剪映专业版 5.9** 时，可以用 [jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill) 替代 ffmpeg 做最终合成。优势：
- 剪映原生特效、字幕动画、转场库（比 ffmpeg xfade 丰富得多）
- 内置云端音乐库
- 可视化编辑（出问题可以手动调）

劣势：
- 依赖剪映 5.9 或更低版本的自动导出（CapCut 国际版兼容性需测试）
- 草稿文件 API 不允许重叠片段（需手动写 transition 而不是依赖时间轴重叠）
- macOS 路径：自动检测 `~/Movies/JianyingPro Drafts/`，可手工指定

接入方式：
```python
from jy_wrapper import JyProject
proj = JyProject(project_name="my_draft", width=832, height=1108, overwrite=True)
proj.add_media_safe(video_path, start_time="0s", duration="3s", track_name="VideoTrack")
proj.add_text_simple("品牌名", start_time="0.5s", duration="2.5s", anim_in="淡入")
proj.save()  # 打开剪映即可看到草稿
```

适用于需要花字动画、专业转场、特效的高级场景。快速出片仍用 ffmpeg 两段法。

参考 `templates/i2v-product-video-build.py`（参数化脚本，改 PRODUCT_IMAGE 和 TTS_TEXT 直接跑）和 `references/build-script-template.md` 获取可复用的完整 Python 脚本模板。

使用方法：
1. 复制模板
2. 修改 `TTS_TEXT`（配音文案）
3. 修改 `SCENES`（分镜配置）
4. 运行 `python3 build_video.py`
