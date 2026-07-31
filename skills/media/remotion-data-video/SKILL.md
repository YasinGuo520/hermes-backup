---
name: remotion-data-video
description: 用Remotion(React代码视频框架)做确定性数据视频——数据榜单/可视化动效/标题字幕，文字100%准确、参数化批量出片。与AI生视频互补(AI出画面，Remotion出确定性内容)。环境已装于 ~/Desktop/hermes/remotion-lab。
---

# Remotion 数据视频

## 触发条件
需要「文字/数据/图表 100% 准确的视频」时用 Remotion（AI生视频会写错字）：数据榜单、量化推荐、产品介绍、动态图表、标题动效。典型场景：量化 Top8 榜单每日出片、带货数据复盘、排行榜内容。

## 环境（已就绪 2026-07）
- 项目：`~/Desktop/hermes/remotion-lab`（Node v22.23，npm 腾讯云镜像 mirrors.tencentyun.com/npm）
- 依赖：`npm install remotion @remotion/cli react react-dom`（**项目级**；全局装会权限失败）
- 渲染浏览器：`npx remotion browser ensure`（下载 chrome-headless-shell ~92MB，落在 node_modules/.remotion/）
- 必须 tsconfig.json，否则报 "Could not find a tsconfig.json file"
- remotion.config.ts 里 `Config.setConcurrency(N)` 必须 ≤ 机器核数（本机 2 核，设 4 报 "Maximum for --concurrency is 2"）

## 渲染命令
```
npx remotion still src/index.tsx <CompositionId> out/preview.png --frame=180   # 先看单帧验证布局
npx remotion render src/index.tsx <CompositionId> out/video.mp4               # 出片
```
- 抖音竖屏：Composition width=1080 height=1920 fps=30
- **先 still 预览再 render 全片**，避免白跑几百帧
- 2核机器 300帧 1080x1920 渲染约 2-4 分钟：background=true + notify_on_complete=true

## 项目结构
```
remotion.config.ts       # Config.setConcurrency(2) 等
tsconfig.json
src/index.tsx            # registerRoot(RemotionRoot)
src/Root.tsx             # <Composition id="DataShowcase" component durationInFrames={300} fps={30} width={1080} height={1920}/>
src/DataShowcase.tsx     # 主场景组件
```

## 数据视频套路（已验证 Top8 榜单 demo）
- **数据内嵌**：从真实系统读（量化 logs/2026-07-31.json），股票名映射硬编码
- **逐行 spring 入场**：`spring({frame: frame-delay, fps, config:{damping:200, stiffness:80}})` + `translateY((1-enter)*40px)` + opacity
- **数字滚动**：`interpolate(frame, [delay+15, delay+45], [0, target], {extrapolateLeft:'clamp', extrapolateRight:'clamp'})`
- **粒子背景**：固定种子 useMemo 生成 60 个 SVG circle，frame 驱动 `sin(frame/30*speed+phase)` 漂移 + 呼吸透明度
- **玻璃卡片**：rgba(255,255,255,.055) + backdropFilter blur(18px) + 1px border + boxShadow
- **渐变标题**：`background:linear-gradient(...)` + `WebkitBackgroundClip:'text'` + `WebkitTextFillColor:'transparent'`
- **A股配色**：红涨 #ef4444 / 绿跌 #22c55e（Yasin 标准）

## 后续扩展
- 量化每日自动出片：cron 读当天 JSON → 数据驱动组件 → render → 发抖音/小红书
- 模板化：数据文件与组件解耦，换 JSON 就出新视频

## 陷阱
1. 单核/双核机器并发必须调低（`nproc` 先查）
2. render 前先 still 单帧 + vision_analyze 看画面
3. npm 全局装 remotion 权限失败 → 项目级
4. uvicorn/fastapi 关键词会让 terminal 误判为长驻进程 → 拆开装依赖命令
