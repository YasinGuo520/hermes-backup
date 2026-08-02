---
name: chaoke-i2v-product-video
description: 实拍产品照 → 百炼I2V生成3条动态 → ffmpeg两段合成（交叉淡化+字幕+配音+BGM）→ 带货短视频出片。全成本¥0.18，10分钟完成。
tags:
  - 带货视频
  - 图生视频
  - 百炼
  - ffmpeg
  - I2V
---

# CHAOKE I2V 产品带货视频流水线

实拍产品照 → 百炼 I2V（¥0.06/条）→ ffmpeg 两段合成 → 成品带货短视频。

> ⚠️ **API来源：本管线走百炼，不走硅基。** 百炼 DashScope API（`bl` CLI）提供 happyhorse-1.1-i2v 模型 ¥0.06/条。
> 硅基（SiliconFlow）没有这个模型，其 Wan2.2-I2V-A14B 要 $0.29/条（≈¥2.1）。
> 用户经常搞混这两个平台，务必明确告知用的是百炼。

## 适用场景

- 内衣/时尚/饰品产品展示
- 任何有实拍产品照需要做动态效果的场景
- 成本敏感、需要快速出片的带货视频

**核心原则：产品必须实拍，不要AI生图。** AI生图的产品细节（标签、包装、logo）必跑偏。

## 前置条件

```bash
# bl CLI 已安装认证（百炼命令行工具）
which bl
bl auth status   # 应显示 API key (model): config

# ffmpeg ≥ 8.0
ffmpeg -version | head -1

# Python 依赖
pip3 install Pillow edge-tts
```

## 费用与账单

### 单价
| 模型 | 单价 | 说明 |
|------|------|------|
| happyhorse-1.1-i2v | ¥0.06/条 | 5秒720P，9:16竖屏 |
| bl file upload | 免费 | 图片上传到DashScope临时存储 |

### 账单查询限制
`bl usage stats` 需要 console login（`bl auth login --console`），无法直接从 CLI 拿到账单。
**查余额/欠费需要去百炼控制台：** [https://bailian.console.aliyun.com](https://bailian.console.aliyun.com)
- 百炼是后付费模式，先欠着后结账
- 如果欠费，API仍会返回200但费用会累积

### 典型单条视频成本
3条I2V × ¥0.06 = **¥0.18**（不包含配音，配音用本地 edge-tts 免费）

> 详细账单对比、平台区别、常见误解见 `references/bailian-billing.md`

## 完整流程（三步）

### Step 1：上传产品图 + 生成3条I2V动态

```bash
# 1.1 上传实拍产品图到百炼临时存储（48h有效期）
UPLOAD_JSON=$(bl file upload --file /path/to/product.jpg \
  --model happyhorse-1.1-i2v --output json)
IMG_URL=$(echo "$UPLOAD_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['url'])")
echo "图片URL: $IMG_URL"

# 1.2 生成3条不同镜头的动态
# 镜头1：慢推进
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "$IMG_URL" \
  --prompt "Slow push-in camera movement, model looking at camera, elegant commercial fashion, smooth cinematic motion, product comes into focus" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/to/output/v1_push_in.mp4 --output json

# 镜头2：从下往上平移
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "$IMG_URL" \
  --prompt "Slow camera panning upward from waist to face, product detail in focus, elegant commercial fashion footage, confident model looking at camera" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/to/output/v2_pan_up.mp4 --output json

# 镜头3：模特转身/侧转正
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "$IMG_URL" \
  --prompt "Model gracefully turns from slight side angle to face camera, long hair flows naturally, white fabric catches studio light, elegant confident pose, smooth cinematic rotation" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/to/output/v3_turn.mp4 --output json
```

**费用：** 3条 × ¥0.06 = ¥0.18

### Step 2：用LLM生成配音文案+字幕时间轴

不要硬编码。先让LLM根据产品/品牌上下文生成3-4句配音文案，每句8-15字，同步设计字幕时间轴。

**推荐格式：**

| 时间段 | 画面 | 字幕行1 | 字幕行2 | 配音 |
|--------|------|---------|---------|------|
| 0-3.5s | V2上移 | CHAOKE 潮客摄影 | 专注内衣视觉定制 | CHAOKE潮客摄影，专注内衣视觉定制 |
| 3.5-6.5s | V3转身 | 专业级光影质感 | 每一帧都是大片 | 专业级光影质感，每一帧都是大片 |
| 6.5-9s | V1慢推 | 让您的品牌 | 在镜头前惊艳绽放 | 让您的品牌，在镜头前惊艳绽放 |
| 9-10s | 收尾 | 您的品牌视觉合伙人 | — | — |

使用 edge-tts 生成配音：`edge-tts --voice zh-CN-XiaoxiaoNeural --rate +10% --text "..." --write-media voiceover.mp3`

### Step 3：ffmpeg两段合成

#### Pass 1：交叉淡化（xfade）

```python
import subprocess

BASE = "/path/to/output"
C1, C2, C3 = f"{BASE}/v2_pan_up.mp4", f"{BASE}/v3_turn.mp4", f"{BASE}/v1_push_in.mp4"
PASS1 = f"{BASE}/_temp_crossfade.mp4"

DUR = 4.0   # 每段取4秒（可调）
FADE = 0.5  # 转场0.5秒
W, H = 832, 1108  # 保持原片分辨率
FPS = 24

f1 = (
    f"[0:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
    f"[1:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
    f"[2:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:"
    f"force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v2];"
    f"[v0][v1]xfade=transition=fade:duration={FADE}:offset={DUR-FADE}[t1];"
    f"[t1][v2]xfade=transition=fade:duration={FADE}:offset={DUR*2-FADE*2-FADE}[vout]"
)

subprocess.run([
    "ffmpeg", "-i", C1, "-i", C2, "-i", C3,
    "-filter_complex", f1, "-map", "[vout]",
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", "-y", PASS1
], check=True)
```

**参数说明：** CRF 18 ≈ 视觉无损 | preset slow 在i7上≈25fps渲染 | 不要用moviepy合成，画质必掉

#### Pass 2：PIL字幕图 + overlay + BGM + 配音

**坑点：** macOS brew安装的ffmpeg没有drawtext滤镜。正确的做法是用PIL生成透明PNG字幕图，再用ffmpeg overlay叠加。

```python
from PIL import Image, ImageDraw, ImageFont

# 2.1 生成配音
import edge_tts, asyncio
asyncio.run(edge_tts.Communicate(
    "配音文案文本",
    voice="zh-CN-XiaoxiaoNeural",
    rate="+10%"
).save("voiceover.mp3"))

# 2.2 从配音获取时长
import subprocess, json
r = subprocess.run([
    "ffprobe", "-v", "quiet", "-print_format", "json",
    "-show_format", "voiceover.mp3"
], capture_output=True, text=True)
voice_dur = float(json.loads(r.stdout)["format"]["duration"])

# 2.3 生成字幕图（PIL）
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"  # ⚠️ 不要用PingFang.ttc
W, H = 832, 1108

subs = [
    ("CHAOKE 潮客摄影", "专注内衣视觉定制", 0.0, 3.5),
    ("专业级光影质感", "每一帧都是大片", 3.5, 6.5),
    ("让您的品牌", "在镜头前惊艳绽放", 6.5, 9.0),
    ("您的品牌视觉合伙人", None, 9.0, voice_dur),
]

import os, tempfile
SUBS_DIR = tempfile.mkdtemp()
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
        # 描边
        for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0,0,0,200))
        draw.text((x, y), line, font=font, fill=(255,255,255,255))
    path = f"{SUBS_DIR}/sub_{i}.png"
    img.save(path)
    sub_files.append({"path": path, "start": start, "end": end, "dur": end-start})

# 2.4 生成背景音乐（极轻环境音pad）
bgm_file = f"{SUBS_DIR}/bgm.mp3"
subprocess.run([
    "ffmpeg",
    "-f", "lavfi", "-i", f"sine=frequency=220:duration={voice_dur},volume=0.15",
    "-f", "lavfi", "-i", f"sine=frequency=330:duration={voice_dur},volume=0.08",
    "-f", "lavfi", "-i", f"anoisesrc=d={voice_dur}:c=pink:a=0.02",
    "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:duration=first[bgm]",
    "-map", "[bgm]", "-y", bgm_file
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 2.5 混音：BGM(25%) + 配音(100%)
mixed_audio = f"{SUBS_DIR}/mixed.mp3"
subprocess.run([
    "ffmpeg", "-i", bgm_file, "-i", "voiceover.mp3",
    "-filter_complex",
    "[0:a]volume=0.3[bg];[1:a]adelay=300|300[voice];"
    "[bg][voice]amix=inputs=2:duration=first:weights=0.25 1[out]",
    "-map", "[out]", "-y", mixed_audio
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 2.6 ffmpeg overlay 叠加字幕 + 混音输出
inputs_list = ["ffmpeg", "-i", PASS1, "-i", mixed_audio]
for sf in sub_files:
    inputs_list.extend(["-loop", "1", "-t", str(sf["dur"]), "-i", sf["path"]])

prev, parts = "0", []
for i, sf in enumerate(sub_files):
    img_idx = i + 2
    src = f"[{prev}:v]" if prev.isdigit() else f"[{prev}]"
    enable = f"between(t,{sf['start']},{sf['end']})"
    label = f"t{i+1}" if i < len(sub_files)-1 else "vout"
    parts.append(f"{src}[{img_idx}:v]overlay=format=auto:enable='{enable}'[{label}]")
    prev = label

OUTPUT = f"{BASE}/final_hq.mp4"
subprocess.run(inputs_list + [
    "-filter_complex", ";".join(parts),
    "-map", "[vout]", "-map", "1:a",
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-shortest", "-y", OUTPUT
], check=True)

# 清理
import shutil
shutil.rmtree(SUBS_DIR)
os.remove(PASS1)

print(f"✅ 完成: {OUTPUT}")
```

## 出片参数一览

| 参数 | 值 | 说明 |
|------|-----|------|
| 分辨率 | 832×1108 | 保持百炼I2V原片分辨率 |
| 帧率 | 24fps | 够用 |
| 编码 | H.264 CRF18 | 接近视觉无损 |
| 预设 | slow | 画质优先 |
| 比特率 | ~5500-5800kbps | 视频部分 |
| 音频 | AAC 192kbps | 配音+BGM混音 |
| 时长 | ~10s | 适配3条I2V+0.5s转场 |
| 文件大小 | ~5-7MB | 10秒视频 |
| **总成本** | **¥0.18** | 3条I2V费用 |

## 常见坑点

| 问题 | 原因 | 解决 |
|------|------|------|
| 成片画质不如单条I2V | moviepy合成+preset ultrafast | 改用ffmpeg两段法+CRF18 |
| drawtext: No such filter | macOS brew ffmpeg没编译drawtext | 改走PIL生成字幕图+overlay |
| PingFang.ttc报错 | PIL不支持.ttc集合字体 | 换用STHeiti Medium.ttc |
| 配音没播完视频没了 | 视频时长<配音 | 延长每段clip的取片时长 |
| adelay参数类型错误 | ffmpeg版本差异 | 用`adelay=300|300` 双声道写法 |
| 剪辑草稿不兼容 | skill为剪映5.9设计，用户装CapCut7.4 | 保持ffmpeg管线，暂不依赖剪映skill |
| **并行生成中断** `exit 130` | `bl video generate` 是同步阻塞调用，并行跑2条以上时第二条被中断 | **逐条串行生成**，每次等前一条完成再跑下一条。单条约60-90秒 |
| **用户问"为什么走百炼不是硅基"** | skill描述没写清API来源，用户以为在烧SiliconFlow余额 | 生成前先告知 "视频生成走百炼 DashScope ¥0.06/条，不是硅基" |

## 配套文件

- `scripts/build_final.py` — 完整可运行合成脚本（修改配音+字幕配置后直接 `python3 build_final.py` 出片）

## 与剪映skill的关系

ffmpeg管线实现了核心需求（交叉淡化+字幕+配音+BGM），够用但不花哨。如果以后需要：
- 花字动画
- 特效转场
- 剪映音乐库
- 批量导出

才需要折腾剪映中文版5.9 + jianying-editor-skill。目前ffmpeg管线已经能出可用的带货视频。
