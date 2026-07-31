#!/usr/bin/env python3
"""Seedance 多镜头拼接成片（xfade 交叉淡化 + 字幕 + 配音 + BGM）
用法:
  python3 stitch_final.py --shots video_shots --storyboard storyboard.json \
      --voiceover "配音文案" --out final.mp4

- xfade 转场拼接（不重编码每镜内容，只拼接）
- PIL 生成透明字幕 PNG 叠加（不用 drawtext，避免 ffmpeg 无该滤镜）
- edge-tts 中文配音 + 轻 BGM 混音
"""
import argparse, json, os, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFont

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys_exit(f"❌ 命令失败: {' '.join(cmd)}\n{r.stderr[-800:]}")
    return r

def sys_exit(msg):
    import sys
    print(msg)
    sys.exit(1)

def get_duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", path
    ], capture_output=True, text=True)
    import json as _json
    return float(_json.loads(r.stdout)["format"]["duration"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True, help="镜头目录 shot_01.mp4...")
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--voiceover", default="", help="配音文案，留空则不配音")
    ap.add_argument("--out", default="final.mp4")
    ap.add_argument("--fade", type=float, default=0.5, help="转场秒数")
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    args = ap.parse_args()

    with open(args.storyboard) as f:
        sb = json.load(f)

    # 收集镜头
    shot_files = sorted(
        [os.path.join(args.shots, x) for x in os.listdir(args.shots) if x.endswith(".mp4")]
    )
    if not shot_files:
        sys_exit("❌ shots 目录没有 mp4")
    print(f"📽️ 拼接 {len(shot_files)} 段")

    # 统一分辨率/帧率/时长（用第一段做基准）
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "json", shot_files[0]
    ], capture_output=True, text=True)
    import json as _json
    stream = _json.loads(probe.stdout)["streams"][0]
    W, H = stream["width"], stream["height"]
    fps_num, fps_den = map(int, stream["r_frame_rate"].split("/"))
    FPS = round(fps_num / fps_den)

    # 每段时长 = 最短段（避免配音溢出），转场裁剪
    durs = [get_duration(s) for s in shot_files]
    DUR = min(durs) - args.fade
    print(f"🎞️ 每段取 {DUR:.1f}s, 分辨率 {W}x{H}, {FPS}fps")

    # Pass 1: xfade 拼接
    tmp = tempfile.mkdtemp()
    pass1 = os.path.join(tmp, "pass1.mp4")
    inputs = []
    for s in shot_files:
        inputs += ["-i", s]
    fc_parts = []
    for i in range(len(shot_files)):
        fc_parts.append(
            f"[{i}:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
            f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1[v{i}]"
        )
    prev = "v0"
    for i in range(1, len(shot_files)):
        offset = DUR * i - args.fade * i
        label = f"vout" if i == len(shot_files) - 1 else f"t{i}"
        fc_parts.append(f"[{prev}][v{i}]xfade=transition=fade:duration={args.fade}:offset={offset:.3f}[{label}]")
        prev = label
    run(["ffmpeg", "-y"] + inputs + [
        "-filter_complex", ";".join(fc_parts),
        "-map", f"[{prev}]", "-c:v", "libx264", "-crf", "18",
        "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", pass1
    ])

    total_dur = get_duration(pass1)

    # Pass 2: 配音 + BGM + 字幕
    audio_inputs = ["-i", pass1]
    audio_fc = []
    has_voice = bool(args.voiceover.strip())

    if has_voice:
        # edge-tts 配音
        voice_file = os.path.join(tmp, "voice.mp3")
        import asyncio, edge_tts
        asyncio.run(edge_tts.Communicate(args.voiceover, voice=args.voice, rate="+10%").save(voice_file))
        audio_inputs += ["-i", voice_file]
        voice_dur = get_duration(voice_file)
        # BGM: 极轻 pad
        bgm_file = os.path.join(tmp, "bgm.mp3")
        run(["ffmpeg", "-y",
             "-f", "lavfi", "-i", f"sine=frequency=220:duration={voice_dur},volume=0.12",
             "-f", "lavfi", "-i", f"sine=frequency=330:duration={voice_dur},volume=0.06",
             "-f", "lavfi", "-i", f"anoisesrc=d={voice_dur}:c=pink:a=0.015",
             "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:duration=first[bgm]",
             "-map", "[bgm]", bgm_file])
        audio_inputs += ["-i", bgm_file]
        audio_fc.append("[1:a]adelay=300|300[voice]")
        audio_fc.append("[2:a]volume=0.25[bg]")
        audio_fc.append("[voice][bg]amix=inputs=2:duration=first:weights=1 0.25[aout]")
    else:
        audio_fc.append("anullsrc=r=44100:cl=stereo[aout]")

    # 字幕（PIL 透明 PNG）
    sub_files = []
    subs = sb.get("subtitles", [])
    if subs:
        font_path = None
        for cand in ["/System/Library/Fonts/STHeiti Medium.ttc",
                     "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                     "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
            if os.path.exists(cand):
                font_path = cand
                break
        if not font_path:
            print("⚠️ 无中文字体，跳过字幕")
        else:
            for i, sub in enumerate(subs):
                text = sub.get("text", "")
                start = sub.get("start", 0)
                end = sub.get("end", total_dur)
                dur = end - start
                img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype(font_path, 34)
                bbox = draw.textbbox((0, 0), text, font=font)
                x = (W - (bbox[2] - bbox[0])) // 2
                y = int(H * 0.85)
                for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
                    draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,200))
                draw.text((x, y), text, font=font, fill=(255,255,255,255))
                p = os.path.join(tmp, f"sub_{i}.png")
                img.save(p)
                sub_files.append((p, start, end, dur))

    # 最终合成
    final_inputs = audio_inputs[:]
    for p, s, e, d in sub_files:
        final_inputs += ["-loop", "1", "-t", str(d), "-i", p]

    parts = []
    prev_label = "0:v"
    for i, (p, s, e, d) in enumerate(sub_files):
        img_idx = 1 + len(audio_inputs) - 1 + i  # 视频0 + 音频N + 字幕i
        label = f"vout" if i == len(sub_files) - 1 else f"sv{i}"
        parts.append(f"[{prev_label}][{img_idx}:v]overlay=format=auto:enable='between(t,{s},{e})'[{label}]")
        prev_label = label

    map_v = "[vout]" if sub_files else "0:v"
    cmd = ["ffmpeg", "-y"] + final_inputs + [
        "-filter_complex", ";".join(audio_fc + parts),
        "-map", map_v, "-map", "[aout]",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-shortest", args.out
    ]
    run(cmd)

    shutil.rmtree(tmp)
    print(f"🎉 成片完成: {args.out} ({total_dur:.1f}s)")

if __name__ == "__main__":
    main()
