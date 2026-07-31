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

## Manim 程序化动画（2026-07 像素画展厅沉淀）

Manim CE 适合像素画/几何/数学类确定性动画。环境：`~/Desktop/hermes/manim-venv`（已装 v0.20.1）。当用户要「动画展示」「数学/像素动画」「展厅动画」时考虑 Manim。

### 环境（Ubuntu/腾讯云）

```bash
sudo apt-get install -y pkg-config libcairo2-dev libpango1.0-dev libffi-dev  # 先装，否则 pip 装 pycairo 报 pkg-config not found
python3 -m venv ~/Desktop/hermes/manim-venv && ~/Desktop/hermes/manim-venv/bin/pip install manim
```

中文文本需要系统 CJK 字体：`fc-list :lang=zh`（腾讯云有 WenQuanYi Zen Hei），`Text("勇者", font="WenQuanYi Zen Hei")`。没有则 `apt install fonts-wqy-zenhei`。

### 四个必踩的坑

1. **默认画幅会静默裁掉大元素**：Manim 默认 frame 14.22x8（16:9），画布/金框/标题大于画幅会**静默裁剪**——不报错，渲染出来元素消失（视觉模型会说"缺金框缺标题"）。修复：`construct()` 开头显式扩画幅 `self.camera.frame_width=16.0; self.camera.frame_height=9.0`，元素尺寸必须小于画幅。
2. **`-s` 预览黑帧**：`manim -ql -s` 存的是**最后一帧**，场景以 FadeOut 收尾时预览纯黑，会误判渲染失败。正确预览：渲染完视频后 `ffmpeg -ss 6 -i out.mp4 -frames:v 1 preview.png` 抽中间帧。
3. **多场景批量渲染**：10个场景一次 `manim -qm script.py Art01_XX Art02_YY ...`，后台跑 + notify_on_complete，720p30 每场景约1分钟（2核机）。
4. **动画验收用中间帧**：视觉模型检查渲染结果时，抽动画中部帧（像素点亮完毕、浮动开始处）而不是首尾帧。

### 展厅/展示页动画设计模式（用户拍板方向）

- ❌ 不要做成「10个独立课件式动画」——用户反馈「像课件演示，不够炫酷」
- ✅ 页面侧走沉浸式：深色星空粒子 + 3D环形画廊（CSS perspective + rotateY 环形排列 + 拖拽旋转 + 玻璃卡片 hover 弹出），完整组件见 `visual-component-patterns` 的 3D 环形展厅
- ✅ 视频侧更炫方向：展厅巡游大片（MovingCameraScene 镜头推拉扫作品墙）/ 像素进化链 morph / 粒子汇聚成形 / 沉浸式3D页面（用户已选 D）
- 交付节奏：用户说「直接生成就可以」= 别再中途多轮预览确认，一次做完渲染+页面+验证再交付
