---
name: remotion-code-videos
description: "用 Remotion（React代码框架）生成确定性视频：数据榜单、动态图表、精确字幕。AI生视频文字会乱码时的替代方案，0成本本地渲染，参数化批量生产。"
version: 1.0
author: Yasin + Agent
created_by: agent
---

# Remotion 代码视频生成

## 触发场景

- 需要**文字100%准确**的视频（AI生视频经常写错字）：榜单、字幕、钩子文案、数据播报
- **数据驱动**内容：量化Top8榜单、带货数据复盘、排行榜动画
- 批量参数化生产：改一个数据文件就出下一个视频
- 0成本：不订阅 Codex（¥140/月），DeepSeek 驱动 + Remotion 本地渲染免费
- 与 AI 生视频互补：AI 出画面，Remotion 出数据+文字+动效，ffmpeg 合成

**不是**做网页的工具 — 输出是视频帧序列，不可交互。做网页用 HTML/Canvas 那套。

## 安装（项目级，不要全局）

```bash
mkdir -p ~/Desktop/hermes/remotion-lab && cd ~/Desktop/hermes/remotion-lab
npm init -y
npm install remotion @remotion/cli react react-dom
npx remotion browser ensure   # 下载 chrome-headless-shell ~92MB，放 node_modules/.remotion/
```

- **npm 全局安装会 EACCES**（共享主机权限）→ 一律项目级
- 腾讯云 npm registry 已是 `mirrors.tencentyun.com`，无需换源

## 项目结构（必须）

```
remotion-lab/
├── remotion.config.ts      # Config.setVideoImageFormat("jpeg"); setOverwriteOutput(true); setConcurrency(N)
├── tsconfig.json           # 没有它 CLI 直接报错，从官方模板抄
├── src/
│   ├── index.tsx           # registerRoot(RemotionRoot)
│   ├── Root.tsx            # <Composition id durationInFrames fps width height component>
│   └── DataShowcase.tsx    # 场景组件（粒子背景 + 玻璃卡片 + 动画）
└── out/                    # 输出
```

tsconfig.json 最小可用：
```json
{
  "compilerOptions": {
    "target": "ES2022", "module": "ESNext", "moduleResolution": "Bundler",
    "jsx": "react-jsx", "strict": true, "skipLibCheck": true,
    "esModuleInterop": true, "allowSyntheticDefaultImports": true, "noEmit": true
  },
  "include": ["src"]
}
```

## 工作流

1. **先出单帧预览**（秒出，验证布局再渲全片）：
   ```bash
   npx remotion still src/index.tsx DataShowcase out/preview.png --frame=180
   ```
   用 vision_analyze 检查画面：文字溢出？卡片重叠？粒子可见？
2. **再渲完整视频**（300帧@2核约2-3分钟，用 background=true + notify_on_complete）：
   ```bash
   npx remotion render src/index.tsx DataShowcase out/quant_top8_2026-07-31.mp4
   ```
3. **ffprobe 验证**：分辨率/时长/帧率
   ```bash
   ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 out/xxx.mp4
   ```

## 数据视频组件模式

见 `references/quant-top8-example.md` — 实测可用的完整组件（粒子背景 + 逐行弹入 + 数字滚动 + 分歧度三色标签）。

核心 API：
- `useCurrentFrame()` / `useVideoConfig()` — 帧号、分辨率、fps
- `spring({frame: frame - delay, fps, config:{damping, stiffness}})` — 入场动画（stagger 用不同 delay）
- `interpolate(frame, [a,b], [c,d], {extrapolateLeft:"clamp", extrapolateRight:"clamp"})` — 数字滚动
- SVG `<circle>` + `sin(frame/speed+phase)` — 粒子漂浮；`radial-gradient` 光晕
- 渐变紫标题：`background:linear-gradient(...)` + `WebkitBackgroundClip:"text"` + `WebkitTextFillColor:"transparent"`
- 玻璃卡片：`rgba(255,255,255,.055)` + `backdropFilter:"blur(18px)"` + 1px 半透明边框

## 坑

1. **并发上限 = CPU 核数**：`Config.setConcurrency(4)` 在2核机上直接报 `Maximum for --concurrency is 2`。设成核数或更小。
2. **缺 tsconfig.json 报错** "Could not find a tsconfig.json" — 先建。
3. **渲染是逐帧截屏**，300帧 1080x1920 在2核机要 2-3 分钟 — 必须后台跑 + notify。
4. 竖屏抖音/小红书：`width={1080} height={1920}`，fps 30。
5. 数字滚动要 `fontVariantNumeric:"tabular-nums"`，否则宽度跳动。
6. A股配色标准：红涨 `#ef4444` / 绿跌 `#22c55e`，所有股票内容统一。

## 可复用场景

- 量化每日 Top8 → cron 出片（改数据 JSON 即可，模板已跑通）
- 带货数据复盘：数字跳动 + 排行榜动画
- 方法论内容：确定性字幕视频（AI 语音 + Remotion 字幕层）
