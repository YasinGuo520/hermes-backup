# 百炼 I2V 图生视频 → 带货成片（唯一权威版）

> 实拍产品图 → 阿里百炼 HappyHorse-1.1-I2V → 动态片段 → ffmpeg 合成带货成片。
> **本文件是全库唯一权威版**：原 `references/bailian-i2v-session.md`、`references/bailian-i2v-session-v2-build-script.md` 与 `douyin-livestream-ecommerce` 的 `references/bailian-i2v-product-video.md` 已并入此处（事件叙事已剥离，只留规则）。

## 铁律：产品实拍，AI 只负责「动」

带货视频用 AI 生图的最大坑：AI 画出来的产品细节不可控（标签乱码、包装颜色不对、logo 变形）→ 挂小黄车退货率炸。正确做法是**用手机实拍产品照做 I2V 源图**，让 AI 只负责让画面动起来。

- **I2V 的 prompt 描述的是「镜头怎么动」，不是「画面有什么」**（画面由输入图决定）
- 实测：产品 100% 一致，成本 **¥0.06/条**（3 条 = ¥0.18），5 秒出片——市面上最便宜的产品级 I2V 方案
- 对比：SiliconFlow Wan2.2-I2V ≈ $0.21-0.29/条（¥1.5-2.1）；T2V 不能控产品；文生图→I2V 的产品细节不可控
- 管线：实拍产品图 → `bl file upload` → `bl video generate` ×N 角度 →（VC 文案）→ edge-tts 配音 → ffmpeg 两段合成 → 成品 MP4

## 命令链

```bash
# 1. 上传（返回 oss:// URL，48h 有效）
bl file upload --file /path/product.jpg --model happyhorse-1.1-i2v --output json

# 2. 生成（prompt 只写镜头运动）
bl video generate \
  --model "happyhorse-1.1-i2v" \
  --image "oss://dashscope-instant/..." \
  --prompt "Slow push-in camera movement, model stands confidently, hair gently swaying, fabric subtly shimmering under soft studio lighting, elegant commercial fashion, smooth cinematic motion" \
  --negative-prompt "Disfigured, deformed, blurry, low quality, distorted face, bad anatomy, extra limbs, ugly" \
  --resolution "720P" --ratio "9:16" --duration 5 --watermark false \
  --download /path/clip1.mp4 --output json
```

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `--model` | `happyhorse-1.1-i2v` | 百炼默认 I2V，质量好速度快 |
| `--resolution` | `720P` | 实测输出 832×1108（接近 9:16 竖屏） |
| `--ratio` | `9:16` | 抖音竖屏 |
| `--duration` | `5` | 单段 5 秒，方便后期拼接 |
| `--watermark` | `false` | 带货去水印 |
| 耗时/费用 | ~60s（含排队）/ **¥0.06** | 文件 ~4.3MB |

## I2V 提示词模板（四类）

```text
# 产品特写
Slow push-in camera, product texture subtly revealed under soft studio lighting, elegant commercial showcase, premium feel

# 模特展示（内衣/服装）
Model stands confidently, hair gently swaying in soft breeze, fabric subtly shimmering under studio lighting, elegant commercial fashion video, slow cinematic camera movement

# 开箱/桌面演示
Camera slowly panning from left to right, product on clean table, natural daylight, premium unboxing feel, smooth motion

# 对比展示 → 分两段 I2V（每个产品一段）+ 后期转场，不要在一个 prompt 里做复杂动作
```

## 合成：ffmpeg 两段法（不要用 moviepy 收尾）

| 方案 | 编码 | 比特率 | 画质 |
|------|------|-------:|------|
| moviepy ultrafast 2500k | ultrafast | ~2500kbps | ❌ 细节丢失（用户实际否决过） |
| **ffmpeg CRF18 preset slow** | slow | ~5800kbps | ✅ 接近源片 |

- **Pass 1**：`xfade=transition=fade:duration=0.5` 交叉淡化；`-crf 18 -preset slow -an`。offset 公式：`offset_n = CLIP_DUR × n − FADE × n`
- **Pass 2**：PIL 生成带描边的透明 PNG 字幕图 → ffmpeg `overlay` + `enable='between(t,start,end)'`（**macOS brew 的 ffmpeg 没有 `drawtext`/`subtitles` 滤镜，别试**）；音频 `-c:a aac -b:a 192k`
- 字幕字体用 `/System/Library/Fonts/STHeiti Medium.ttc`（PingFang.ttc 在 PIL 上报 `cannot open resource`）；带货字幕放底部（H-180 / 0.85H）
- **BGM 必加**（空手出片用户觉得干）：`lavfi` sine 220Hz(0.15) + 330Hz(0.08) + 粉噪 → `amix` → 与配音混音 `weights=0.25 1`、`adelay=300`
- **配音先行，反推时长**：先生成配音 → `ffprobe` 测时长 → `CLIP_DUR = (voice_dur + FADE×(N−1)) / N`。**配音比视频长 = 文案被吞，这是用户最反感的低级错误**
- 配音：edge-tts `zh-CN-XiaoxiaoNeural --rate +10%~+15%`（约 9.9s / 3 句）；文案必须让 LLM 按上下文生成，**不要硬编码**

**出片参数**：832×1108 / 24fps / H.264 CRF18 / preset slow / AAC 192k / ~5800kbps / 约 10s / ¥0.18（3 条 I2V）

## 坑

- 上传文件 48h 过期，过期需重新 `bl file upload`；输入图建议 ≥1080×1080，太小放大后糊
- I2V 会微调原图（光线/角度轻微变化），不影响产品识别
- 避免复杂动态 prompt（「模特转身走两步」大概率崩）；首选推近/拉远/平移/风吹衣物头发
- ⚠️ **并行 vs 串行**：`bl video generate` 是同步阻塞调用，实测并行跑多条会 `exit 130` 中断（→ 逐条串行）；也有 `&` + `wait` 跑通的记录。**默认串行，追求速度时再试并行，中断就回到串行**
- 百炼是后付费：欠费仍返回 200 但费用累积；余额/账单去控制台 `bailian.console.aliyun.com`（`bl usage stats` 需 console login）
- 需要 `bl` CLI 已 `auth login` 且有余额

## 可运行脚本与延伸

- **完整可运行脚本（本次会话实跑）**：`references/bailian-i2v-session-build-script.md`（Pass1 xfade + PIL 字幕 + BGM 混音一条龙，改路径即用）
- 参数化模板：`templates/i2v-product-video-build.py`（改 `PRODUCT_IMAGE`/`TTS_TEXT` 直接跑）；本地合成脚本 `scripts/build_final.py`
- 高级特效/字幕动画需剪映时：`references/jianying-capcut-compatibility.md`（只支持剪映 ≤5.9）与 `jianying-editor` 技能
- 平台选型与账单：`china-ai-platforms` 技能（百炼/硅基/火山三平台矩阵）
