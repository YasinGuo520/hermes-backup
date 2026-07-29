# 百炼 I2V 图生视频完整构建脚本（CHAOKE潮客摄影案例）

此脚本来自实际生产会话，完整跑通了「实拍产品照 → 3条I2V动态 → 交叉淡化 → 字幕 → BGM → 配音 → 出片」全流程。

## 适用范围

- 实拍产品图（内衣/服装/配饰等）
- 产出 3 段 5s 动态 → 合成约 10s 成品
- 竖屏 9:16（832×1108）
- 总成本 ¥0.18（3条 × ¥0.06）

## 前置条件

```bash
# bl CLI 已安装并认证
which bl && bl auth status

# 环境变量
export DASHSCOPE_API_KEY="sk-xxx"
```

## 完整脚本

```python
#!/usr/bin/env python3
"""v3: 延长视频匹配配音 + 加背景音乐"""
import subprocess, os, shutil
from PIL import Image, ImageDraw, ImageFont

BASE = "/Users/mac/Desktop/hermes"
C1 = f"{BASE}/chaoke_bra_v2_pan_up.mp4"
C2 = f"{BASE}/chaoke_bra_v3_turn.mp4"
C3 = f"{BASE}/chaoke_bra_video.mp4"
VOICE = f"{BASE}/voiceover_v2.mp3"
OUTPUT = f"{BASE}/chaoke_final_hq.mp4"
TEMP = f"{BASE}/_temp_build"
os.makedirs(TEMP, exist_ok=True)

W, H, FPS = 832, 1108, 24
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"

# ====== 获取配音时长 ======
r = subprocess.run(["ffprobe","-v","quiet","-show_format",VOICE],
    capture_output=True, text=True)
voice_dur = float([l for l in r.stdout.split("\n") if "duration" in l][0].split("=")[1])
print(f"配音时长: {voice_dur:.1f}s")

# ====== 根据配音时长计算每段截取长度 ======
FADE = 0.5
NUM_CLIPS = 3
CLIP_DUR = (voice_dur + FADE * (NUM_CLIPS - 1)) / NUM_CLIPS
total_dur = CLIP_DUR * NUM_CLIPS - FADE * (NUM_CLIPS - 1)
print(f"每段截取: {CLIP_DUR:.2f}s, 总长: {total_dur:.1f}s")

# ====== Pass 1: xfade 交叉淡化 ======
print("[1/3] 交叉淡化...")
xfade1_offset = CLIP_DUR - FADE
xfade2_offset = CLIP_DUR * 2 - FADE * 2

filter1 = (
    f"[0:v]trim=0:{CLIP_DUR},setpts=PTS-STARTPTS,"
    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
    f"[1:v]trim=0:{CLIP_DUR},setpts=PTS-STARTPTS,"
    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
    f"[2:v]trim=0:{CLIP_DUR},setpts=PTS-STARTPTS,"
    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v2];"
    f"[v0][v1]xfade=transition=fade:duration={FADE}:"
    f"offset={xfade1_offset}[t1];"
    f"[t1][v2]xfade=transition=fade:duration={FADE}:"
    f"offset={xfade2_offset}[vout]"
)

crossfade_file = f"{TEMP}/crossfade.mp4"
subprocess.run([
    "ffmpeg", "-i", C1, "-i", C2, "-i", C3,
    "-filter_complex", filter1,
    "-map", "[vout]",
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-an", "-y", crossfade_file
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ====== Pass 2: PIL 字幕图 ======
print("[2/3] 生成字幕...")
subs = [
    ("CHAOKE 潮客摄影", "专注内衣视觉定制", 0.0, 3.5),
    ("专业级光影质感", "每一帧都是大片", 3.5, 6.5),
    ("让您的品牌", "在镜头前惊艳绽放", 6.5, 9.0),
    ("您的品牌视觉合伙人", None, 9.0, voice_dur),
]

def make_sub(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y_base = int(H * 0.85)
    if isinstance(lines, str):
        lines = [lines]
    for i, line in enumerate(lines):
        if not line: continue
        fs = 34 if (i == 0 and "CHAOKE" in line) else (30 if i == 0 else 28)
        font = ImageFont.truetype(FONT, fs)
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x, y = (W - tw) // 2, y_base + i * 40
        for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),
                       (0,-2),(0,2),(-2,0),(2,0)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,200))
        draw.text((x, y), line, font=font, fill=(255,255,255,255))
    return img

sub_files = []
for i, (l1, l2, start, end) in enumerate(subs):
    lines = [l for l in [l1, l2] if l]
    path = f"{TEMP}/sub_{i}.png"
    make_sub(lines).save(path)
    sub_files.append({"path": path, "start": start, "end": end, "dur": end - start})

# ====== Pass 3: 生成 BGM + 混音 + 字幕叠加 ======
print("[3/3] 合成字幕+配音+BGM...")

# BGM: 220Hz pad + 330Hz pad + 粉噪
bgm_file = f"{TEMP}/bgm.mp3"
subprocess.run([
    "ffmpeg",
    "-f", "lavfi", "-i", f"sine=frequency=220:duration={voice_dur},volume=0.15",
    "-f", "lavfi", "-i", f"sine=frequency=330:duration={voice_dur},volume=0.08",
    "-f", "lavfi", "-i", f"anoisesrc=d={voice_dur}:c=pink:a=0.02",
    "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:duration=first[bgm]",
    "-map", "[bgm]", "-y", bgm_file
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 混音: BGM 25% + 配音 100% + 300ms 延时
mixed_audio = f"{TEMP}/mixed.mp3"
subprocess.run([
    "ffmpeg", "-i", bgm_file, "-i", VOICE,
    "-filter_complex",
    "[0:a]volume=0.3[bg];[1:a]adelay=300|300[voice];"
    "[bg][voice]amix=inputs=2:duration=first:weights=0.25 1[out]",
    "-map", "[out]", "-y", mixed_audio
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 字幕叠加 (overlay 链)
inputs = ["ffmpeg", "-i", crossfade_file, "-i", mixed_audio]
for sf in sub_files:
    inputs.extend(["-loop", "1", "-t", str(sf["dur"]), "-i", sf["path"]])

prev = "0"
filter_parts = []
for i, sf in enumerate(sub_files):
    img_idx = i + 2
    src_ref = f"[{prev}:v]" if prev.isdigit() else f"[{prev}]"
    enable = f"between(t,{sf['start']},{sf['end']})"
    label = f"t{i+1}" if i < len(sub_files) - 1 else "vout"
    filter_parts.append(
        f"{src_ref}[{img_idx}:v]overlay=format=auto:enable='{enable}'[{label}]")
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
shutil.rmtree(TEMP)
print(f"✅ 完成: {OUTPUT}")
```

## 关键参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| I2V 模型 | happyhorse-1.1-i2v | ¥0.06/条，走百炼 DashScope |
| I2V 时长 | 5 秒 | bl video generate --duration 5 |
| I2V 分辨率 | 720P | 832×1108 竖屏 |
| xfade 转场 | fade, 0.5s | 交叉淡化 |
| 视频编码 | CRF 18, preset slow | 接近视觉无损 |
| 字幕字体 | STHeiti Medium.ttc | macOS 中文粗体 |
| BGM | 220Hz+330Hz+粉噪 | 极轻环境音，不压人声 |
| 配音 | edge-tts zh-CN-XiaoxiaoNeural | 中文女声，免费 |
