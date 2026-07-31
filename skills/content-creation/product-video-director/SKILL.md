---
name: product-video-director
description: 产品图 → 导演分镜设计（运镜/拍摄方式）→ 火山方舟 Seedance 逐镜图生视频 → ffmpeg 拼接成片。15秒以上自动多镜头不同运镜。全流程驱动：导演思维先行，不是把一张图直接丢给I2V。当用户说"产品视频""带货视频""图生视频流程""运镜""分镜""把产品图做成视频"时使用。
tags:
  - 带货视频
  - 图生视频
  - Seedance
  - 火山方舟
  - 分镜
  - 运镜
---

# 产品视频导演流水线（Seedance 版）

产品图 → **导演分镜**（运镜/拍摄设计）→ Seedance 逐镜生成 → **拼接成片**。

> ⚠️ **API来源：走火山方舟 ARK，不走百炼、不走硅基。**
> Key 在 `/home/ubuntu/backend/.env` 的 `ARK_API_KEY`，Base `https://ark.cn-beijing.volces.com/api/v3`。
> 视频生成接口：`POST /api/v3/contents/generations/tasks`（注意是 **generations**，不是 generators——拼错就404）。

## 核心原则

1. **导演思维先行**：拿到产品图先设计分镜（每镜的运镜+拍摄方式），不直接丢一张图给I2V。
2. **15秒+ = 多镜头**：总时长 ≥15s 必须拆成 ≥3 镜，每镜用**不同运镜/拍摄方式**，避免单调。
3. **产品实拍图优先**：AI生图的产品细节（标签/logo/包装）必跑偏，用实拍产品照。
4. **人物一致性靠参考图**：Seedance 2.0 支持多图参考（9图+3视频+3音频），锁脸锁服装用参考图。
5. **先出方案后烧钱**：分镜方案先给用户确认，确认后才调 API（视频模型贵）。

## 前置条件

```bash
# 检查 ARK Key
grep ARK_API_KEY /home/ubuntu/backend/.env

# ffmpeg ≥ 8.0
ffmpeg -version | head -1

# Python 依赖
pip3 install requests Pillow edge-tts
```

## 费用参考（火山方舟 Seedance 按量）

| 模型 | 价格 | 定位 |
|------|------|------|
| `doubao-seedance-1-0-pro-fast-251015` | ~0.4元/5秒 | 便宜快，日常批量 |
| `doubao-seedance-1-5-pro-251215` | ~1.7元/5秒 | 有声+质感 |
| `doubao-seedance-2-0-260128` | ~10元/5秒 | 最强一致性（多参考图） |

每个模型通常有免费 token 额度（新用户/活动，以控制台为准）。

## 完整流程（四步）

### Step 1：导演分镜设计（人看+脚本双输出）

拿到产品图+目标时长+风格后，先出**分镜表**：

| 镜号 | 时长 | 景别 | 运镜 | 拍摄方式 | 画面描述 | 提示词要点 |
|------|------|------|------|---------|---------|-----------|
| 1 | 5s | 特写 | 慢推 | 固定机位+微距 | 产品logo/细节入画 | "slow push-in on product detail" |
| 2 | 5s | 中景 | 环绕 | 轨道环绕 | 产品360°展示 | "360 degree orbit around product" |
| 3 | 5s | 全景 | 上升 | 摇臂升起 | 产品+场景 | "crane up reveal full scene" |

**运镜库（每镜选一个，15s+强制不重复）：**

| 运镜 | 英文提示词 | 适用 |
|------|-----------|------|
| 慢推近 | slow push-in | 细节特写 |
| 慢拉远 | slow pull-back | 开场/收尾 |
| 平移 | lateral pan / dolly left-right | 展示主体 |
| 环绕 | 360-degree orbit | 产品全貌 |
| 上升 | crane up / tilt up | 全景揭幕 |
| 下降 | crane down | 聚焦主体 |
| 跟拍 | tracking shot | 动态场景 |
| 微距 | macro close-up | 材质/细节 |
| 悬停 | drone hover | 大场景 |
| 手持 | handheld subtle | 生活感 |

**同时产出：**
1. 分镜表（给用户确认）
2. `storyboard.json`（脚本用，含每镜 prompt）

**暂停：用户确认分镜方案后才生成视频。**

### Step 2：Seedance 逐镜图生视频

用 `scripts/seedance_gen.py` 逐镜生成（串行，每镜 30-90 秒）：

```bash
python3 scripts/seedance_gen.py \
  --image /path/to/product.jpg \
  --storyboard /path/to/storyboard.json \
  --model doubao-seedance-1-0-pro-fast-251015 \
  --outdir /path/to/output/video_shots
```

- 每镜输出 `shot_01.mp4`、`shot_02.mp4`...
- 默认串行，避免并发限流
- 完成后自动下载到本地

### Step 3：ffmpeg 拼接成片

用 `scripts/stitch_final.py` 拼接（xfade 交叉淡化 + 可选字幕/配音/BGM）：

```bash
python3 scripts/stitch_final.py \
  --shots /path/to/output/video_shots \
  --storyboard /path/to/storyboard.json \
  --voiceover "配音文案" \
  --out /path/to/output/final.mp4
```

参数：
- 转场：xfade fade 0.5s
- 字幕：PIL 生成透明 PNG 叠加（不用 drawtext，避免 ffmpeg 没编译该滤镜）
- 配音：edge-tts 中文女声
- 输出：H264 CRF18 + AAC 192k

### Step 4：交付

- 每镜 mp4 + 拼接成片 final.mp4
- 报告：镜数/时长/模型/成本

## 项目目录结构

```
<项目名>/
├── product.jpg          # 产品图（实拍）
├── storyboard.md        # 分镜表（人看）
├── storyboard.json      # 分镜数据（脚本用）
├── video_shots/         # Seedance 每镜输出
│   ├── shot_01.mp4
│   └── ...
└── final.mp4            # 成片
```

## 常见坑点

| 问题 | 原因 | 解决 |
|------|------|------|
| 接口404 | 路径拼成 `generators` | 正确是 `contents/generations/tasks` |
| ModelNotOpen | 模型未在方舟控制台开通 | 控制台→模型广场→开通，Seedance需先充值/买资源包 |
| 下载403 | 签名URL被shell截断(&拆分) | 用 Python urllib 完整拿URL下载，不手工复制 |
| 并发中断 | 同时提交多条任务 | 串行生成，一条完成再下一条 |
| 长视频单调 | 单镜头重复 | 15s+ 强制多镜头不同运镜 |
| 人物跑偏 | 无参考图 | 用 Seedance 2.0 多图参考锁脸/服装 |

## 配套脚本

- `scripts/seedance_gen.py` — 读 storyboard.json 逐镜调 Seedance 生成+下载
- `scripts/stitch_final.py` — xfade 拼接 + 字幕/配音/BGM 合成
