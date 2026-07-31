---
name: remotion-video-production
description: 用 Remotion（React 代码驱动）生成确定性视频——数据榜单、动态图表、精确字幕、网页动效转视频。与 AI 生视频互补：AI 出画面，Remotion 出数据和文字（文字 100% 准确）。
---

# Remotion 代码驱动视频生产

## 什么时候用
- 需要**精确文字/真实数据**的视频（AI 生视频会写错字、数据不可控）
- **参数化量产**：改 JSON/数组就能出下一个视频（量化 Top8 榜单、带货数据复盘、排行榜）
- 网页动效（粒子/玻璃卡片/渐变紫）需要转成视频输出
- 0 成本本地渲染，不依赖付费 Agent（Codex 等）或订阅

## 环境（本机已配置）
- 项目：`~/Desktop/hermes/remotion-lab/`
- 已装：remotion, @remotion/cli, react, react-dom（npm registry 为腾讯云镜像）
- 渲染浏览器：chrome-headless-shell 已下载，位于 `node_modules/.remotion/chrome-headless-shell/`
- 2 核机器：`remotion.config.ts` 里 `Config.setConcurrency(2)`（超过报错）

## 工作流（关键：先单帧预览再全片渲染）
1. 写组件：`src/index.tsx`（registerRoot）→ `src/Root.tsx`（Composition 注册分辨率/时长/fps）→ `src/主组件.tsx`
2. **先出预览帧**：`npx remotion still src/index.tsx <CompositionId> out/preview.png --frame=180`
3. **vision_analyze 检查**布局/溢出/配色，不行就改组件重跑
4. 全片渲染（后台 + notify_on_complete）：
   `npx remotion render src/index.tsx <CompositionId> out/xxx.mp4`
   300帧 @ 1080x1920 约 3 分钟，输出约 1.8MB
5. ffprobe 验证：`ffprobe -v error -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 out/xxx.mp4`

## 必备配置文件（新项目复制）
- `tsconfig.json`：缺少时报 "Could not find a tsconfig.json file"（见仓库内示例）
- `remotion.config.ts`：`Config.setVideoImageFormat("jpeg"); Config.setOverwriteOutput(true); Config.setConcurrency(2)`

## 常用动画模式
- 粒子背景：`useMemo` + 固定种子生成点集（避免每帧重生成），frame 驱动 sin/cos 漂移 + 闪烁
- 行渐入：`spring({frame: frame - delay, fps, config: {damping: 200, stiffness: 80}})` + stagger delay
- 数字滚动：`interpolate(frame, [start, end], [0, target], {extrapolateLeft/Right: "clamp"})`
- 渐变紫标题：`background: linear-gradient(...) + WebkitBackgroundClip: "text" + WebkitTextFillColor: "transparent"`

## Pitfalls
- ❌ concurrency 超过 CPU 核数 → "Maximum for --concurrency is N"，改 config
- ❌ 缺 tsconfig.json → bundler 直接拒绝
- ❌ 粒子每次 render 生成随机点 → 画面每帧抖动，必须 useMemo + 种子
- A股配色铁律：红涨 `#ef4444` 绿跌 `#22c55e`（信号分歧度三色：绿=一致 / 黄=中性 / 红=分歧）
- 竖屏 1080x1920 适配抖音/小红书；横屏 1920x1080 适配公众号/B站

## 模板
- `templates/data-showcase.tsx`：通用数据榜单组件（粒子+玻璃卡片+逐行弹入+数字滚动），改 `STOCKS` 数组 + 标题即可换数据出片。量化每日榜单复用：直接读 `~/Desktop/hermes/quant-skill/logs/<date>.json` 的 top_k 填充。
