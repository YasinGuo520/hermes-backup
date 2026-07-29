# 视频构建脚本模板

## 使用方法

1. 复制本模板到 `~/Desktop/hermes/build_video.py`
2. 修改 `TTS_TEXT`（配音文案）、`SCENES`（分镜配置）
3. 运行 `python3 ~/Desktop/hermes/build_video.py`

## 完整脚本

```python
#!/usr/bin/env python3
"""Ensure user site-packages are found"""
import sys, site
sys.path.insert(0, site.getusersitepackages())

"""
AI视频自动生成流水线
输出：竖屏9:16 MP4
"""

import os, math, asyncio
import numpy as np
import edge_tts

from moviepy import (
    VideoClip, TextClip, CompositeVideoClip, AudioFileClip,
    concatenate_videoclips
)

OUTPUT_DIR = "/Users/mac/Desktop/hermes"

# ===== 修改这里：配音文案 =====
TTS_TEXT = """你的配音文案写在这里。
注意控制字数，45秒视频约200字。"""

# ===== 修改这里：分镜配置 (时长秒, 标题, 副标题) =====
SCENES = [
    (5.0, "标题", "副标题"),
    (5.0, "第二屏", "详情"),
    (5.5, "第三屏", "详情"),
    (7.5, "第四屏", "详情"),
    (5.5, "第五屏", "对比"),
    (4.5, "第六屏", "结果"),
    (6.0, "关注我", "下期预告"),
]

W, H = 720, 1280  # 竖屏 9:16 (720p加速渲染)

def solid_bg(color):
    def make_frame(t):
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:] = color
        return frame
    return make_frame

def make_slide(title_text, subtitle_text, duration, is_red=False):
    bg_color = (40, 10, 10) if is_red else (18, 18, 30)
    bg = VideoClip(frame_function=solid_bg(bg_color), duration=duration)
    layer_clips = [bg]

    try:
        title_clip = TextClip(
            text=title_text,
            font="/System/Library/Fonts/STHeiti Medium.ttc",
            font_size=52,
            color="white",
            stroke_color="#6C63FF",
            stroke_width=1,
            size=(W - 120, None),
            method="caption",
            text_align="center",
        ).with_duration(duration).with_position(("center", H // 2 - 80))
        layer_clips.append(title_clip)
    except Exception as e:
        print(f"  [WARN] 标题渲染失败: {e}")

    if subtitle_text:
        try:
            sub_clip = TextClip(
                text=subtitle_text,
                font="/System/Library/Fonts/STHeiti Medium.ttc",
                font_size=28,
                color="#AAAAAA",
                size=(W - 120, None),
                method="caption",
                text_align="center",
            ).with_duration(duration).with_position(("center", H // 2 + 60))
            layer_clips.append(sub_clip)
        except Exception as e:
            print(f"  [WARN] 副标题渲染失败: {e}")

    return CompositeVideoClip(layer_clips, size=(W, H))

def generate_voiceover():
    output_path = os.path.join(OUTPUT_DIR, "voiceover.mp3")
    print("[1/3] 生成配音...")
    communicate = edge_tts.Communicate(
        TTS_TEXT,
        voice="zh-CN-XiaoxiaoNeural",
        rate="+15%",
        pitch="+0Hz"
    )
    asyncio.run(communicate.save(output_path))
    print(f"      配音已保存: {output_path}")
    return output_path

def build_video(audio_path):
    print("[2/3] 合成视频...")
    slides = []
    for duration, title, subtitle in SCENES:
        print(f"      渲染: 「{title[:20]}...」 ({duration}s)")
        slide = make_slide(title, subtitle, duration)
        slides.append(slide)

    video = concatenate_videoclips(slides, method="compose")
    audio = AudioFileClip(audio_path)

    # 对齐时长
    final_dur = min(video.duration, audio.duration)
    video = video.subclipped(0, final_dur)
    audio = audio.subclipped(0, final_dur)
    video = video.with_audio(audio)

    output_path = os.path.join(OUTPUT_DIR, "output.mp4")
    print(f"      正在渲染视频 ({video.duration:.1f}s, 720x1280)...")
    video.write_videofile(
        output_path, fps=24,
        codec="libx264", audio_codec="aac",
        preset="ultrafast", bitrate="1500k", threads=4,
    )
    print(f"\n[✓] 视频已生成: {output_path}")
    return output_path

def main():
    print("=" * 50)
    print("AI视频自动生成流水线")
    print("=" * 50)
    print(f"配音文案: {len(TTS_TEXT)}字")
    print(f"分镜数: {len(SCENES)}个")
    print("=" * 50)

    audio_path = generate_voiceover()
    video_path = build_video(audio_path)

    file_size = os.path.getsize(video_path) / 1024 / 1024
    print(f"\n✅ 全部完成！")
    print(f"  📹 视频: {video_path} ({file_size:.1f}MB)")
    print(f"  🎙️  配音: {audio_path}")

if __name__ == "__main__":
    main()
```

## 常见调整

| 需求 | 修改位置 |
|------|---------|
| 换话题/文案 | `TTS_TEXT` 变量 |
| 改分镜顺序/时长 | `SCENES` 列表 |
| 换配音语音 | `voice="zh-CN-xxx"` 参数 |
| 调语速 | `rate="+15%"` → `"+20%"` 或 `"-10%"` |
| 改分辨率 | `W, H = 720, 1280` |
| 改字体 | `font="..."` 路径 |
| 改背景色 | `(18, 18, 30)` RGB值 |
| 加强调色背景 | 分镜配置加 `is_red=True` |
