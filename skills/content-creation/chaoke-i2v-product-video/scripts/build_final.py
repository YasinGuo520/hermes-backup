#!/usr/bin/env python3
"""
完整带货视频合成脚本 — 实拍产品照→百炼I2V→ffmpeg成品
用法：
  1. 先跑完 bl video generate 生成3条I2V片段
  2. 生成配音: edge-tts --voice zh-CN-XiaoxiaoNeural --rate +10% --text "..." --write-media voiceover.mp3
  3. 修改下方路径和字幕配置
  4. python3 build_final.py
"""
import subprocess, os, shutil, json
from PIL import Image, ImageDraw, ImageFont

# ==================== 配置区 ====================
BASE = os.path.dirname(os.path.abspath(__file__))
CLIPS = [
    f"{BASE}/v2_pan_up.mp4",   # 镜头1
    f"{BASE}/v3_turn.mp4",     # 镜头2
    f"{BASE}/v1_push_in.mp4",  # 镜头3
]
VOICE = f"{BASE}/voiceover.mp3"
OUTPUT = f"{BASE}/final_hq.mp4"

W, H, FPS = 832, 1108, 24
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
FADE = 0.5

# 字幕配置（每段: 行1, 行2可选, 开始秒, 结束秒）
SUBS = [
    ("CHAOKE 潮客摄影", "专注内衣视觉定制", 0.0, 3.5),
    ("专业级光影质感", "每一帧都是大片", 3.5, 6.5),
    ("让您的品牌", "在镜头前惊艳绽放", 6.5, 9.0),
    ("您的品牌视觉合伙人", None, 9.0, None),  # None结束=到配音结束
]
# =============================================

TEMP = f"{BASE}/_temp_build"
os.makedirs(TEMP, exist_ok=True)

# 1. 测配音时长
r = subprocess.run(["ffprobe","-v","quiet","-show_format",VOICE],
    capture_output=True, text=True)
voice_dur = float([l for l in r.stdout.split("\n") if "duration" in l][0].split("=")[1])
print(f"配音时长: {voice_dur:.1f}s")

# 补全None结束时间
SUBS = [(a,b,c, d if d is not None else voice_dur) for a,b,c,d in SUBS]

# 2. 算每段视频截取长度（确保视频总长≥配音）
NUM_CLIPS = len(CLIPS)
CLIP_DUR = max(4.0, (voice_dur + FADE * (NUM_CLIPS - 1)) / NUM_CLIPS + 0.2)
total_video = CLIP_DUR * NUM_CLIPS - FADE * (NUM_CLIPS - 1)
print(f"每段取{CLIP_DUR:.1f}s, 视频总长{total_video:.1f}s (配音{voice_dur:.1f}s)")

# 3. Pass 1: ffmpeg xfade 交叉淡化
print("\n[1/3] 交叉淡化...")
xfade1_off = CLIP_DUR - FADE
xfade2_off = CLIP_DUR * 2 - FADE * 2
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
cf = f"{TEMP}/crossfade.mp4"
subprocess.run(["ffmpeg","-i",CLIPS[0],"-i",CLIPS[1],"-i",CLIPS[2],
    "-filter_complex",f1,"-map","[vout]",
    "-c:v","libx264","-crf","18","-preset","slow",
    "-pix_fmt","yuv420p","-r",str(FPS),"-an","-y",cf],
    check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print("  ✅")

# 4. 生成字幕图
print("[2/3] 字幕图...")
def make_sub(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y_base = int(H * 0.85)
    if isinstance(lines, str): lines = [lines]
    for i, line in enumerate(lines):
        if not line: continue
        fs = 34 if (i == 0 and "CHAOKE" in line) else (30 if i == 0 else 28)
        font = ImageFont.truetype(FONT, fs)
        tw = draw.textbbox((0,0),line,font=font)[2]
        x, y = (W - tw)//2, y_base + i*40
        for dx,dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
            draw.text((x+dx,y+dy),line,font=font,fill=(0,0,0,200))
        draw.text((x,y),line,font=font,fill=(255,255,255,255))
    return img

sfiles = []
for i,(l1,l2,start,end) in enumerate(SUBS):
    lines = [l for l in[l1,l2] if l]
    img = make_sub(lines)
    path = f"{TEMP}/sub_{i}.png"
    img.save(path)
    sfiles.append({"path":path,"start":start,"end":end,"dur":end-start})
    print(f"  [{start}-{end}s] {l1}")

# 5. BGM + 合成
print("[3/3] 合成...")
bgm = f"{TEMP}/bgm.mp3"
subprocess.run(["ffmpeg",
    "-f","lavfi","-i",f"sine=frequency=220:duration={voice_dur},volume=0.15",
    "-f","lavfi","-i",f"sine=frequency=330:duration={voice_dur},volume=0.08",
    "-f","lavfi","-i",f"anoisesrc=d={voice_dur}:c=pink:a=0.02",
    "-filter_complex","[0:a][1:a][2:a]amix=inputs=3:duration=first[bgm]",
    "-map","[bgm]","-y",bgm],
    check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

mix = f"{TEMP}/mixed.mp3"
subprocess.run(["ffmpeg","-i",bgm,"-i",VOICE,
    "-filter_complex",
    "[0:a]volume=0.3[bg];[1:a]adelay=300|300[voice];"
    "[bg][voice]amix=inputs=2:duration=first:weights=0.25 1[out]",
    "-map","[out]","-y",mix],
    check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

inputs = ["ffmpeg","-i",cf,"-i",mix]
for sf in sfiles:
    inputs.extend(["-loop","1","-t",str(sf["dur"]),"-i",sf["path"]])

prev, parts = "0", []
for i,sf in enumerate(sfiles):
    img_idx = i+2
    src = f"[{prev}:v]" if prev.isdigit() else f"[{prev}]"
    label = f"t{i+1}" if i<len(sfiles)-1 else "vout"
    parts.append(f"{src}[{img_idx}:v]overlay=format=auto:enable='between(t,{sf['start']},{sf['end']})'[{label}]")
    prev = label

subprocess.run(inputs+["-filter_complex",";".join(parts),
    "-map","[vout]","-map","1:a",
    "-c:v","libx264","-crf","18","-preset","slow",
    "-c:a","aac","-b:a","192k",
    "-pix_fmt","yuv420p","-r",str(FPS),
    "-shortest","-y",OUTPUT], check=True)

shutil.rmtree(TEMP)

r = subprocess.run(["ffprobe","-v","quiet","-print_format","json",
    "-show_format","-show_streams",OUTPUT],capture_output=True,text=True)
d = json.loads(r.stdout)
vs = [s for s in d["streams"] if s["codec_type"]=="video"][0]
print(f"\n✅ {OUTPUT}")
print(f"   {vs['width']}x{vs['height']} | {float(d['format']['duration']):.1f}s | {int(d['format']['size'])//1024}KB")
