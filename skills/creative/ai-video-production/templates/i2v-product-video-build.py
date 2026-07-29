#!/usr/bin/env python3
"""
完整 I2V 产品带货视频合成脚本
用法：
  1. 修改下方配置（PRODUCT_IMAGE, TTS_TEXT 等）
  2. python3 build_product_video.py
  3. 成品在 OUTPUT 路径

依赖: pip3 install Pillow edge-tts
前置: bl CLI 已认证，ffmpeg 已安装
"""

import subprocess, os, shutil, json, asyncio
from PIL import Image, ImageDraw, ImageFont

# ====================== 配置区 ======================
PRODUCT_IMAGE = "/path/to/your/product.jpg"   # 实拍产品图
TTS_TEXT = (
    "CHAOKE潮客摄影，专注内衣视觉定制。"
    "专业级光影质感，每一帧都是大片。"
    "让您的品牌，在镜头前惊艳绽放。"
)
OUTPUT_DIR = os.path.expanduser("~/Desktop/hermes")
PROJECT_NAME = "product_video"
# ==================================================

# 常量
W, H, FPS = 832, 1108, 24
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
FADE = 0.5
NUM_CLIPS = 3
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMP = os.path.join(OUTPUT_DIR, f"_build_{PROJECT_NAME}")
os.makedirs(TEMP, exist_ok=True)

def log(msg): print(f"[{PROJECT_NAME}] {msg}")

# ====== Step 1: 上传图片 ======
log("上传产品图...")
r = subprocess.run(
    ["bl", "file", "upload", "--file", PRODUCT_IMAGE,
     "--model", "happyhorse-1.1-i2v", "--output", "json"],
    capture_output=True, text=True, check=True)
img_url = json.loads(r.stdout)["url"]

# ====== Step 2: 并发生成3条I2V ======
prompts = [
    ("v1_push_in", "Slow push-in camera movement, model looking at camera, elegant commercial fashion, smooth cinematic motion, product comes into focus"),
    ("v2_pan_up", "Slow camera panning upward from waist to face, product detail in focus, elegant commercial fashion footage"),
    ("v3_turn", "Model gracefully turns from slight side angle to face camera, hair flows naturally, fabric catches studio light, smooth cinematic rotation"),
]

log("并发生成3条I2V...")
procs = []
for name, prompt in prompts:
    out = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}_{name}.mp4")
    p = subprocess.Popen([
        "bl", "video", "generate",
        "--model", "happyhorse-1.1-i2v",
        "--image", img_url,
        "--prompt", prompt,
        "--negative-prompt", "Disfigured, deformed, blurry, low quality, distorted face",
        "--resolution", "720P", "--ratio", "9:16", "--duration", "5",
        "--watermark", "false", "--download", out, "--output", "json"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append((name, p))

for name, p in procs:
    p.wait()
log("3条I2V生成完成")

CLIPS = [os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}_{n}.mp4") for n, _ in prompts]

# ====== Step 3: 生成配音 ======
log("生成配音...")
voiceover = os.path.join(TEMP, "voiceover.mp3")
async def tts():
    import edge_tts
    await edge_tts.Communicate(TTS_TEXT, voice="zh-CN-XiaoxiaoNeural", rate="+10%").save(voiceover)
asyncio.run(tts())

# ====== Step 4: 测配音时长 ======
r = subprocess.run(["ffprobe","-v","quiet","-show_format",voiceover],
    capture_output=True, text=True)
voice_dur = float([l for l in r.stdout.split("\n") if "duration" in l][0].split("=")[1])
log(f"配音时长: {voice_dur:.1f}s")
CLIP_DUR = (voice_dur + FADE * (NUM_CLIPS - 1)) / NUM_CLIPS
xfade1_off = CLIP_DUR - FADE
xfade2_off = CLIP_DUR * 2 - FADE * 2

# ====== Step 5: Pass 1 - xfade交叉淡化 ======
log("Pass 1 交叉淡化...")
crossfade_file = os.path.join(TEMP, "crossfade.mp4")
f1 = (
    f"[0:v]trim=0:{CLIP_DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
    f"[1:v]trim=0:{CLIP_DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
    f"[2:v]trim=0:{CLIP_DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v2];"
    f"[v0][v1]xfade=transition=fade:duration={FADE}:offset={xfade1_off}[t1];"
    f"[t1][v2]xfade=transition=fade:duration={FADE}:offset={xfade2_off}[vout]"
)
subprocess.run([
    "ffmpeg","-i",CLIPS[0],"-i",CLIPS[1],"-i",CLIPS[2],
    "-filter_complex",f1,"-map","[vout]",
    "-c:v","libx264","-crf","18","-preset","slow",
    "-pix_fmt","yuv420p","-r",str(FPS),"-an","-y",crossfade_file
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ====== Step 6: PIL字幕图 ======
log("生成字幕图...")
subs = [
    ("CHAOKE 潮客摄影", "专注内衣视觉定制", 0.0, 3.5),
    ("专业级光影质感", "每一帧都是大片", 3.5, 6.5),
    ("让您的品牌", "在镜头前惊艳绽放", 6.5, 9.0),
    ("您的品牌视觉合伙人", None, 9.0, voice_dur),
]
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
    path = os.path.join(TEMP, f"sub_{i}.png")
    img.save(path)
    sub_files.append({"path": path, "start": start, "end": end, "dur": end-start})

# ====== Step 7: BGM + 混音 ======
log("生成BGM+混音...")
bgm = os.path.join(TEMP, "bgm.mp3")
subprocess.run([
    "ffmpeg",
    "-f","lavfi","-i",f"sine=frequency=220:duration={voice_dur},volume=0.15",
    "-f","lavfi","-i",f"sine=frequency=330:duration={voice_dur},volume=0.08",
    "-f","lavfi","-i",f"anoisesrc=d={voice_dur}:c=pink:a=0.02",
    "-filter_complex","[0:a][1:a][2:a]amix=inputs=3:duration=first[bgm]",
    "-map","[bgm]","-y",bgm
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

mixed = os.path.join(TEMP, "mixed.mp3")
subprocess.run([
    "ffmpeg","-i",bgm,"-i",voiceover,
    "-filter_complex",
    "[0:a]volume=0.3[bg];[1:a]adelay=300|300[voice];"
    "[bg][voice]amix=inputs=2:duration=first:weights=0.25 1[out]",
    "-map","[out]","-y",mixed
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ====== Step 8: overlay字幕 + 输出 ======
log("合成最终视频...")
OUTPUT = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}_final_hq.mp4")
inputs = ["ffmpeg","-i",crossfade_file,"-i",mixed]
for sf in sub_files:
    inputs.extend(["-loop","1","-t",str(sf["dur"]),"-i",sf["path"]])

prev, parts = "0", []
for i, sf in enumerate(sub_files):
    img_idx = i + 2
    src = f"[{prev}:v]" if prev.isdigit() else f"[{prev}]"
    label = f"t{i+1}" if i < len(sub_files)-1 else "vout"
    parts.append(f"{src}[{img_idx}:v]overlay=format=auto:enable='between(t,{sf['start']},{sf['end']})'[{label}]")
    prev = label

subprocess.run(inputs + [
    "-filter_complex",";".join(parts),
    "-map","[vout]","-map","1:a",
    "-c:v","libx264","-crf","18","-preset","slow",
    "-c:a","aac","-b:a","192k",
    "-pix_fmt","yuv420p","-r",str(FPS),
    "-shortest","-y",OUTPUT
], check=True)

shutil.rmtree(TEMP)
log(f"✅ 完成: {OUTPUT}")
