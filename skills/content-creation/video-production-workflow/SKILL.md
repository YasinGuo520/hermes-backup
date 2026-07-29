---
name: video-production-workflow
description: "视频生产流水线：VC 出文案 → LLM-video-maker（带货短视频）或 Aliang（短剧/绘本）出成片。旧管线 Wan2.2+moviepy 做兜底。一条龙交付。选型速查见 [references/video-tools-catalog.md](references/video-tools-catalog.md) —— 12款视频工具按场景/平台/成本排列。"
metadata:
  version: 1.0.0
  created: 2026-07-10
  tags: [带货, 短视频, 工作流, 抖音]
---

# 视频生产流水线

> 用户确认的标准工作流。当用户说「做个视频」「出个片」「做个带货视频」时，按此执行。

## 决策树

```
用户给产品/主题/方向
       │
       ▼
  ┌─ 是短剧/剧情类？ ──→ Aliang (aliang-shortvideo)
  │
  └─ 是带货/种草/测评？ ──→ LLM-video-maker (HyperFrames)
       │
       └─ 应急/兜底？ ──→ 旧管线 (Wan2.2+moviepy)
```

## 标准流程（带货短视频）

### 第1步：VC 出文案

```bash
python3 ~/Desktop/hermes/viral_copywriter.py \
  --mode A --product "<产品名>" \
  --category "<品类>" --target "<目标人群>" \
  --price <价格> --platform douyin
```

或直接 alias vc 调用：
```bash
vc --mode A --product "..." --category "..." --price 89
```

- Mode A：扒爆款结构 → 生成带货文案（3-4版，选最佳）
- Mode B：直接生成（没有参考爆款时）
- 输出包含：钩子 + 痛点 + 解决方案 + 逼单话术

### 第2步：转 LLM-video-maker 出片

1. 把 VC 输出的文案整理成 `brief.json`，丢到 `~/Desktop/hermes/video-maker/briefs/`
2. `npx hyperframes init projects/<project-id>`
3. 写 HTML/GSAP 构图（含文案分段、动画、转场）
4. `npx hyperframes render projects/<project-id> -o renders/<id>.mp4 -q draft`
5. 合并 edge-tts 配音：`edge-tts --voice zh-CN-XiaoxiaoNeural --text "$(cat script.txt)" --write-media narration.mp3 --rate +15%`
6. 音画合成：`ffmpeg -y -i rendered.mp4 -i narration.mp3 -c:v copy -c:a aac final.mp4`

### 第3步：交付

- 成片存 `~/Desktop/hermes/video-maker/projects/<id>/renders/`
- 如需改文案 → 跑 VC 重出
- 如需改画面 → 调 HTML/GSAP 构图后重渲染

## 短剧走 Aliang

当用户说「做个短剧」时，走 `aliang-shortvideo` skill：

1. 确认：灵感 + 题材 + 总时长 + 画风
2. 生成剧情大纲 → 用户确认
3. 分集剧本 → 用户确认
4. 分镜表 + storyboard.json → 用户确认
5. 批量出图（bl image）
6. 图生视频（bl video，**用户确认付费后**）
7. 拼接成片

## 旧管线兜底

当 LLM-video-maker 或 Aliang 不可用/太慢/出错时，回退到旧管线：

```bash
# Wan2.2 动态背景 + edge-tts 配音 + moviepy 字幕
```

## 要点

- **文案必须先跑 VC**，不要手工写。VC 有爆款拆解能力，转化率有保障。
- **画面优先 LLM-video-maker**，GSAP 动画质感远好于旧管线。
- **旧管线不做首选**，只做故障应急。
- 带货视频字幕放 **底部**（H-180），不要居中。
- 转场必须 **淡入淡出**，不要硬切。
