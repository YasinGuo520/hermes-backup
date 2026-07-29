# 百炼 I2V 实操记录（2026-07-11）

本文件记录一次完整的「实拍产品图 → 百炼 I2V → ffmpeg HQ 合成」工作流实操，供后续直接复用参数。

## 源素材

一张 CHAOKE 潮客摄影的内衣模特实拍图，白色蕾丝内衣产品展示，9:16 竖屏，832×1108。

## 上传

```bash
bl file upload \
  --file /path/to/product.jpg \
  --model happyhorse-1.1-i2v \
  --output json
```

返回的 OSS URL 格式：`oss://dashscope-instant/{hash}/2026-07-11/{uuid}/{filename}.jpg`

## 三条 I2V 生成命令

### V1 — 慢推镜头

```bash
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "oss://dashscope-instant/..." \
  --prompt "Slow push-in camera movement, model stands confidently, her long dark hair gently swaying, the white lace bra fabric subtly shimmering under soft studio lighting, elegant commercial fashion video, smooth cinematic motion, professional product showcase" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face, bad anatomy, extra limbs, ugly" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/chaoke_bra_video.mp4 --output json
```

**结果：** 5.2s, 832×1108, 4.3MB, ¥0.06

### V2 — 镜头从下往上平移

```bash
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "oss://dashscope-instant/..." \
  --prompt "Slow camera panning upward from model's waist to her face, the white lace bra comes into focus, fabric texture subtly shifting under studio light, elegant commercial fashion showcase, model looking confidently at camera, smooth professional motion" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face, bad anatomy, extra limbs" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/chaoke_bra_v2_pan_up.mp4 --output json
```

**结果：** 5.2s, 832×1108, 4.3MB, ¥0.06

### V3 — 模特转身

```bash
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "oss://dashscope-instant/..." \
  --prompt "Model gracefully turns from slight side angle to face camera, her long wavy hair flows naturally with the movement, white lace bra catches studio light, elegant confident pose, professional lingerie commercial footage, smooth cinematic rotation" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face, bad anatomy, extra limbs" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/chaoke_bra_v3_turn.mp4 --output json
```

**结果：** 5.2s, 832×1108, 3.1MB, ¥0.06

## 配音生成（LLM 脚本）

**用户明确要求先用 LLM 生成脚本。** 不要硬编码。LLM 生成脚本：

> "CHAOKE潮客摄影，专注内衣视觉定制。专业级光影质感，每一帧都是大片。让您的品牌，在镜头前惊艳绽放。"

edge-tts：`--voice zh-CN-XiaoxiaoNeural --rate +10%`，时长 ~9.9s

## 合成迭代

### Iteration 1：moviepy（❌ 被用户否决）

| 参数 | 值 |
|------|-----|
| 合成方式 | moviepy CompositeVideoClip |
| preset | ultrafast / bitrate 2500k |
| 文件 | 2.4MB (8s) |
| 用户反馈 | "成片的清晰度没有生成片段好，配音和字幕也没有" |
| 根因 | ultrafast 压缩 + 字幕渲染失败 |

### Iteration 2：ffmpeg CRF 18（✅ 方向对了）

两段 ffmpeg 直出，CRF 18 + preset slow，~5800kbps，画质接近源片。

### Iteration 3：修复配音吞尾 + 加 BGM（✅ 最终成片）

| 问题 | 修复 |
|------|------|
| 配音10s视频仅8s | 每段3s→4s（总长11s），配音完整播完 |
| 无BGM干巴巴 | ffmpeg lavfi 220Hz+330Hz pad + 粉噪 |
| 字幕渲染失败 | PIL 带描边 PNG + loop overlay |

**最终输出：** 9.9s, 832×1108, 7MB, ~6Mbps, 有配音+字幕+BGM, ¥0.18

## 关键教训

前期失败版本（硬编码，用户不满意）：用了 Hermes text_to_speech 工具
最终版本（LLM 生成脚本后用 edge-tts 命令行）：

```bash
edge-tts --voice zh-CN-XiaoxiaoNeural --rate +10% \
  --text 'CHAOKE潮客摄影，专注内衣视觉定制。专业级光影质感，每一帧都是大片。让您的品牌，在镜头前惊艳绽放。' \
  --write-media voiceover_v2.mp3
```

时长：~9.9s

## 最终合成

### ❌ 第一次尝试（moviepy，被用户否决）

| 参数 | 值 |
|------|-----|
| 合成方式 | moviepy CompositeVideoClip |
| preset | ultrafast |
| bitrate | 2500k |
| 文件大小 | 2.4MB (8s) |
| 用户反馈 | "成片的清晰度没有生成片段好，而且配音和字幕也没有" |
| 问题根因 | ultrafast 压缩太狠 + 字幕渲染失败 |

### ✅ 第二次尝试（ffmpeg CRF 18，用户说"方向对了"）

两段 ffmpeg 直出：

#### Pass 1：ffmpeg xfade 交叉淡化

用 `ffmpeg xfade=transition=fade` 链接 3 段 3s 片段，0.5s 交叉淡化。
- `-crf 18 -preset slow`：视觉无损，比特率 ~5800kbps
- `-an`：Pass 1 不混音频

#### Pass 2：PIL 字幕图 + ffmpeg overlay（转场视频上叠加字幕+配音）

**原因：** macOS brew 安装的 ffmpeg 默认没有 `drawtext` 和 `subtitles` 滤镜。不可用。

用 PIL 生成带描边的透明 PNG 字幕图，每张循环指定时长（`-loop 1 -t <dur>`），ffmpeg overlay 叠加。多段字幕用 `enable='between(t,start,end)'` 控制显隐时间。

| 参数 | 值 |
|------|-----|
| 合成方式 | ffmpeg xfade → PIL overlay → aac 混音 |
| 视频编码 | CRF 18 + preset slow |
| 音频编码 | aac 192k |
| 输出比特率 | ~5800kbps |
| 文件大小 | 5.6MB (8s) |
| 画质 | ✅ 接近源片 |
| 总费用 | ¥0.18（3条I2V）+ ¥0（配音）= ¥0.18 |

## 关键教训

| 教训 | 说明 |
|------|------|
| 先用 LLM 生成脚本 | 不要硬编码配音词。用户期望 LLM 根据上下文生成脚本 | |
| moviepy 合成降画质 | CompositeVideoClip + ultrafast/2500k 导致画质明显损失 |
| 最终合成用 ffmpeg CRF 18 | CRF 18 + preset slow 保留画质，~5800kbps |
| 字幕用 PIL+overlay | macOS brew ffmpeg 没有 drawtext，PIL 生成字幕图 + overlay 可用 |
| 字体用 STHeiti | PingFang.ttc 在 PIL 上报 `cannot open resource` |
| 配音时长必须反推视频长度 | 先生成配音 → ffprobe 测时长 → 再设置 clip_dur，不能反过来 |
| BGM 必须加 | 空手出片用户觉得干。ffmpeg lavfi sine+anoisesrc 可生成简单环境音 |
| 用户偏好直出 | 不要每步都问，直接执行。等反馈迭代 |

## 潜在升级：jianying-editor-skill

| 维度 | 评价 |
|------|------|
| 是什么 | 直接读写剪映草稿文件，绕过鼠标模拟，AI 自动剪辑 |
| 优势 | 剪映的完整特效库（字幕动画、转场、音乐库、调色）全能用 |
| 适合 | 抖音带货视频，剪映是国内短视频标配 |
| 前提 | 需要安装剪映专业版 5.9 或更低版本 |
| 不装也够用 | 当前 ffmpeg 管线能跑通：实拍图 → I2V(¥0.06) → ffmpeg 合成 → 出片

## 完整合成脚本参考

见 `~/Desktop/hermes/build_hq.py`，已验证可运行。结构：
- `build_hq.py`：Pass 1 xfade + PIL 字幕生成 + Pass 2 overlay + 混音
- 依赖：`ffmpeg`, `PIL`, `edge-tts`
