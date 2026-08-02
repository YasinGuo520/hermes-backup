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

## 安装与项目结构（合并自 remotion-code-videos / remotion-data-video / remotion-data-videos）

```bash
mkdir -p ~/Desktop/hermes/remotion-lab && cd ~/Desktop/hermes/remotion-lab
npm init -y
npm install remotion @remotion/cli react react-dom   # 项目级；npm 全局装会 EACCES（共享主机权限）
npx remotion browser ensure   # 下载 chrome-headless-shell ~92MB，放 node_modules/.remotion/
```

```
remotion-lab/
├── remotion.config.ts      # Config.setVideoImageFormat("jpeg"); setOverwriteOutput(true); setConcurrency(2)
├── tsconfig.json           # 没有它 CLI 直接报 "Could not find a tsconfig.json file"
├── src/
│   ├── index.tsx           # registerRoot(RemotionRoot)
│   ├── Root.tsx            # <Composition id durationInFrames fps width height component>
│   └── DataShowcase.tsx    # 场景组件（粒子背景 + 玻璃卡片 + 动画）
└── out/                    # 输出
```

tsconfig.json 最小可用：
```json
{ "compilerOptions": {
    "target": "ES2022", "module": "ESNext", "moduleResolution": "Bundler",
    "jsx": "react-jsx", "strict": true, "skipLibCheck": true,
    "esModuleInterop": true, "allowSyntheticDefaultImports": true, "noEmit": true },
  "include": ["src"] }
```

核心 API：`useCurrentFrame()` / `useVideoConfig()`；粒子用 SVG `<circle>` + `sin(frame/speed+phase)`（比 Canvas 稳，无头渲染同步执行）；数字滚动加 `fontVariantNumeric:"tabular-nums"` 否则宽度跳动；玻璃卡片 `rgba(255,255,255,.055)` + `backdropFilter blur(18px)` + 1px 半透明边框。

- **真实数据接入**：量化每日信号在 `~/Desktop/hermes/quant-skill/logs/<日期>.json`（Top8 + total + disagreement），组件内嵌 STOCKS 数组 + DATE，改 JSON 即出新视频。**可 cron 每日自动渲染**：先跑 quant_ensemble → 生成 JSON → 更新组件 → render。
- **脚注铁律**：数据视频底部加权重 + "信号仅供研究"声明。
- 改 Root.tsx 里 Composition 的宽高/duration 后需重新 bundle 才生效。
- **终端工具误判**：命令含 uvicorn/fastapi 关键词会被 terminal 误判为长驻进程 → 拆开装依赖命令。
- 完整可复用组件实例见 `references/quant-top8-example.md`（粒子背景 + 逐行弹入 + 数字滚动 + 分歧度三色标签）。

## 模板
- `templates/data-showcase.tsx`：通用数据榜单组件（粒子+玻璃卡片+逐行弹入+数字滚动），改 `STOCKS` 数组 + 标题即可换数据出片。量化每日榜单复用：直接读 `~/Desktop/hermes/quant-skill/logs/<date>.json` 的 top_k 填充。
