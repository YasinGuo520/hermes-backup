# 全自动AI图文视频流水线 — 参考配方

本文件记录了一次成功运行的完整技术方案，供后续复用。

## 完整工作流

### 第1步：生成配图（SiliconFlow API）

模型：`Qwen/Qwen-Image` (720x1280竖屏)

7张配图提示词模板：

| 文件名 | 场景 | 提示词要点 |
|--------|------|-----------|
| title | 标题封面 | 深色科技感背景，蓝紫渐变，白字标题，灰字副标题 |
| problem | 痛点展示 | 暗红色背景，红色数字"3小时"强调 |
| tool | 工具介绍 | 深蓝紫渐变，"免费·不用注册·手机就能用" |
| steps | 步骤说明 | 深色背景，"三步搞定"+编号列表 |
| compare | 对比 | 左右分割，左红(以前3小时)右绿(现在10分钟) |
| result | 结果 | 深蓝绿背景，对勾装饰，积极氛围 |
| cta | 关注引导 | 深紫色，"关注我"发光字体+下次预告 |

### 第2步：生成配音（edge-tts）

```python
import asyncio, edge_tts
communicate = edge_tts.Communicate(
    text,
    voice="zh-CN-XiaoxiaoNeural",
    rate="+15%"
)
asyncio.run(communicate.save("voiceover.mp3"))
```

### 第3步：合成视频（moviepy 2.x）

完整脚本结构：
```python
import sys, site
sys.path.insert(0, site.getusersitepackages())

import numpy as np
from moviepy import (
    VideoClip, TextClip, CompositeVideoClip, AudioFileClip, ImageClip,
    concatenate_videoclips
)
from moviepy.video.fx import FadeIn, FadeOut

# 1. 分镜配置
SCENES = [
    ("slide_title.png",  4.5, "标题文字", "副标题文字"),
    # ...
]

# 2. 创建每帧
def make_slide(img_name, title, subtitle, duration):
    bg = ImageClip(f"slide_{img_name}").resized((720, 1280)).with_duration(duration)
    clips = [bg]
    if title:
        t = TextClip(text=title, font="/System/Library/Fonts/STHeiti Medium.ttc",
                     font_size=52, color="white", stroke_color="#000", stroke_width=2,
                     size=(640, None), method="caption", text_align="center"
        ).with_duration(duration).with_position(("center", 560))
        clips.append(t)
    if subtitle:
        s = TextClip(...).with_duration(duration).with_position(("center", 700))
        clips.append(s)
    return CompositeVideoClip(clips, size=(720, 1280))

# 3. 拼接带转场
slides = [make_slide(...) for ... in SCENES]
faded = []
for i, s in enumerate(slides):
    fx = []
    if i > 0: fx.append(FadeIn(0.3))
    if i < len(slides)-1: fx.append(FadeOut(0.3))
    faded.append(s.with_effects(fx) if fx else s)
video = concatenate_videoclips(faded, method="compose")

# 4. 对齐音频
audio = AudioFileClip("voiceover.mp3")
video = video.with_audio(audio).subclipped(0, min(video.duration, audio.duration))

# 5. 导出
video.write_videofile("output.mp4", fps=24, codec="libx264",
    audio_codec="aac", preset="ultrafast", bitrate="1500k", threads=4)
```

## 渲染性能数据（Mac i7-1068NG7, 16GB, 无独显）

| 分辨率 | 预设 | 时长 | 渲染耗时 | 文件大小 |
|--------|------|------|---------|---------|
| 720x1280 | ultrafast | 38s | ~3min | 7MB |
| 1080x1920 | medium | 52s | ~18min（超时） | − |

结论：用720p渲染，发布到抖音会自动压缩。

## 踩坑记录

1. **Qwen/Qwen-Image 通过 Hermes image_generate 调用失败**：400 Model does not exist。原因：Hermes的OpenAI兼容封装与SiliconFlow实际API格式不完全匹配。解决方案：直接用Python urllib调REST API。

2. **PingFang.ttc 不被PIL支持**：.ttc是TrueType Collection，PIL只能打开.ttf单字体文件。换用 STHeiti Medium.ttc 或 Arial Unicode.ttf。

3. **背景进程找不到numpy/moviepy**：user site-packages不在sys.path中。解决方案：脚本顶部加 `sys.path.insert(0, site.getusersitepackages())`。

4. **frame_function返回tuple报错**：moviepy 2.x期望numpy array (H, W, 3)，不是tuple (R, G, B)。解决方案：`return np.zeros((H, W, 3), dtype=np.uint8)`。

5. **逐像素遮罩导致渲染极慢（0.3fps）**：728×1280的嵌套for循环每帧执行92万次Python迭代。解决方案：直接去掉遮罩，用TextClip的stroke_color参数保证文字可读性。

6. **S3 presigned URL过期**：下载必须在API返回后立即执行，不能延迟。
