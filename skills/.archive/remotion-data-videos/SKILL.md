---
name: remotion-data-videos
description: 用 Remotion（React 代码视频框架）生成「确定性视频」——数据榜单、图表动画、精确文字、模板化批量出片。与 AI 生视频互补：AI 出画面，Remotion 出数据/文字/图表。已跑通：A股量化 Top8 榜单视频全链路。
version: 1.0
author: Yasin + Agent
created_by: agent
---

# Remotion 数据视频（代码生成确定性视频）

当需要**文字/数据/图表 100% 准确**的视频（量化榜单、数据复盘、排行榜、产品介绍、字幕动效）时用 Remotion。AI 生视频（即梦/可灵/Seedance）文字会乱、数字会错——Remotion 每帧都是代码控制，绝对精确，本地渲染免费。

**定位**：AI 生视频出"画面"，Remotion 出"数据+文字+动效"，ffmpeg 合成成片。做网页动效的技术栈（React/CSS）直接复用，等于给网页动效加视频输出口。

## 已跑通实例

- `~/Desktop/hermes/remotion-lab/` — A股量化 Top8 榜单视频（1080x1920 竖屏 10s）
  - 输出：`out/quant_top8_2026-07-31.mp4`
  - 数据：真实 JSON（quant_skill/logs/2026-07-31.json）内嵌组件
  - 效果：深蓝底+漂浮粒子+玻璃卡片逐行弹入+数字滚动+三色分歧度标签

## 安装（一次性）

```bash
mkdir -p ~/Desktop/hermes/remotion-lab && cd ~/Desktop/hermes/remotion-lab
npm init -y && npm install remotion @remotion/cli react react-dom
# tsconfig.json 必须（默认模板没有会报错）：
# { "compilerOptions": { "target":"ES2022","module":"ESNext","moduleResolution":"Bundler","jsx":"react-jsx","strict":true,"skipLibCheck":true,"esModuleInterop":true,"noEmit":true }, "include":["src"] }
npx remotion browser ensure   # 下载 chrome-headless-shell（~92MB，渲染必需）
```

## 项目结构

```
remotion.config.ts   # Config.setVideoImageFormat("jpeg"); setOverwriteOutput(true); setConcurrency(2)
src/index.tsx        # registerRoot(RemotionRoot)
src/Root.tsx         # <Composition id fps durationInFrames width height>
src/DataShowcase.tsx # 主组件（粒子/卡片/数据动画）
```

## 渲染命令

```bash
# 单帧预览（先看布局再渲染，快）
npx remotion still src/index.tsx DataShowcase out/preview.png --frame=180
# 完整视频
npx remotion render src/index.tsx DataShowcase out/demo.mp4
# 验证
ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 out/demo.mp4
```

## 组件要点（DataShowcase 模式）

- **粒子背景**：SVG circle 数组（固定种子随机生成，useMemo），`Math.sin(frame/30*speed+phase)` 做漂移+闪烁。比 Canvas 稳（无头渲染同步执行）
- **玻璃卡片**：`background:rgba(255,255,255,.055)` + `backdropFilter:blur(18px)` + 边框 rgba 白
- **入场动画**：`spring({frame: frame-delay, fps, config:{damping:200,stiffness:80}})`，逐行 delay 递增（20+i*7）
- **数字滚动**：`interpolate(frame,[delay+15,delay+45],[0,target],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})`
- **渐变标题**：`linear-gradient(...)` + `WebkitBackgroundClip:"text"` + `WebkitTextFillColor:"transparent"`
- **A股配色**：红涨 #ef4444 / 绿跌 #22c55e（分歧度标签：<0.05 绿"信号一致"、<0.15 黄"中性"、≥0.15 红"分歧"）
- 底部脚注：权重 + "信号仅供研究"（数据视频必须声明性质）

## 真实数据接入

量化每日信号在 `~/Desktop/hermes/quant-skill/logs/<日期>.json`（Top8 + total + disagreement）。组件内嵌 STOCKS 数组 + DATE，改 JSON 即出新视频。**可 cron 每日自动渲染**：先跑 quant_ensemble → 生成 JSON → 更新组件 → render。

## 常见坑

1. **concurrency 不能超过 CPU 核数**：`Maximum for --concurrency is 2 (number of cores on this system)`。2核机器 `Config.setConcurrency(2)`
2. **tsconfig.json 必需**：没有报 "Could not find a tsconfig.json file"
3. **渲染时长**：1080x1920 300帧 @ 2并发 ≈ 2-3 分钟。用 `terminal(background=true)` + notify_on_complete
4. **竖屏**：抖音/小红书用 1080x1920 @ 30fps
5. **注册表**：registerRoot 后 Composition 的 id 是渲染目标名，Root.tsx 里改宽高/duration 后需重新 bundle
6. **npm registry**：腾讯云镜像 mirrors.tencentyun.com/npm 已配好，速度正常

## 可复用的后续方向

- 带货数据复盘视频（数字跳动+排行榜）
- 量化每日榜单 cron 自动出片发抖音/小红书
- 把网页动效（粒子/玻璃卡片/渐变紫）搬进视频做产品宣传片
