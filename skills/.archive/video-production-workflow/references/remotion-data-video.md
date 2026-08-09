# Remotion 代码驱动数据视频（已装）

Remotion = 用 React 代码写视频的开源框架（瑞士团队），免费本地渲染，无需剪辑软件。
与 AI 生视频互补：AI 生视频（即梦/可灵/Seedance）出画面但文字/数据易错；Remotion 文字/数据/图表 100% 精确。

适用场景：数据复盘、量化榜单、排行榜动效、标题/字幕动画、参数化量产（改数据文件即出新视频）。

## 安装状态（2026-07 已就绪）

- 项目：`~/Desktop/hermes/remotion-lab/`
- 依赖：`remotion @remotion/cli react react-dom`（npm 项目级安装）
- 渲染浏览器：已执行 `npx remotion browser ensure` 下载 chrome-headless-shell
  （位于 `node_modules/.remotion/chrome-headless-shell/linux64/...`，约 92MB）
- npm registry 已是腾讯云镜像 `mirrors.tencentyun.com`，国内直连快

## 注意

- **全局 `npm install -g remotion` 会权限报错**（EPERM）→ 用项目级安装：
  `mkdir -p 项目目录 && cd 项目目录 && npm init -y && npm install remotion @remotion/cli react react-dom`
- 首次渲染前必须 `npx remotion browser ensure`，否则找不到浏览器
- CLI 验证：`npx remotion --version`

## 待验证

- 实际渲染 demo：写 Composition（React 组件）→ `npx remotion render` 出 mp4
- 与 ffmpeg 合成链路（配音/BGM 叠加）对接现有流水线
