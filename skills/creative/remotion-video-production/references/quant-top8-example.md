# 量化 Top8 榜单视频 — 实测组件模式（2026-07-31 跑通）

项目：`~/Desktop/hermes/remotion-lab/`（1080x1920, 30fps, 300帧=10秒, 输出1.8MB）
数据源：量化系统日志 `~/Desktop/hermes/quant-skill/logs/2026-07-31.json`（真实信号）

## 组件骨架

```tsx
// Root.tsx — 注册合成
<Composition id="DataShowcase" component={DataShowcase}
  durationInFrames={300} fps={30} width={1080} height={1920} />

// DataShowcase.tsx — 主场景
<AbsoluteFill style={{fontFamily:"PingFang SC, Microsoft YaHei, sans-serif"}}>
  <Particles />                    {/* 背景层 */}
  <标题区: opacity=titleIn, translateY>   {/* spring 入场 */}
  <榜单区: STOCKS.map((s,i) => <Row delay={20+i*7}/>)}  {/* stagger */}
  <底部脚注: 权重/免责/>
</AbsoluteFill>
```

## 数据驱动要点

- 数据直接 const 内嵌（从 JSON 提取后写死进组件）—— 参数化时改这里或 fetch JSON
- `score = total * 100` 显示两位小数；`animatedScore` 用 interpolate 从 0 滚到目标
- 分歧度标签三色规则：`<0.05 信号一致(绿#22c55e)` / `<0.15 中性(黄#facc15)` / `≥0.15 分歧(红#ef4444)`
- 排名框颜色：第1金 #fbbf24，第2银 #cbd5e1，第3铜 #d97706，其余灰

## 粒子背景（SVG，无 Canvas）

```tsx
const dots = useMemo(() => { /* 固定种子 LCG 随机，60 个点 */ }, [width, height]);
// 每帧: driftY = sin((frame/30)*speed + phase)*40, twinkle = 0.5+0.5*sin(...)
// 双色粒子: hue>0.5 ? 紫 rgba(167,139,250) : 青 rgba(94,234,212)
// 极光光晕: 两个 radial-gradient div，紫色 top-left + 青色 bottom-right
```

- `useMemo` 固定种子：粒子位置渲染期间稳定，只有漂移量随帧变
- 不用 Canvas 是为了 headless chrome 逐帧渲染更稳、更快

## 渲染命令（实测）

```bash
# 预览单帧（验证布局，~5秒）
npx remotion still src/index.tsx DataShowcase out/preview.png --frame=180
# 完整渲染（300帧 2核 约2-3分钟）
npx remotion render src/index.tsx DataShowcase out/quant_top8_2026-07-31.mp4
```

## 后续自动化方向

量化 cron 8:45 出信号后 → 脚本把 `2026-MM-DD.json` 转成 `stocks.ts` 数据文件 → remotion render → 出片。
模板已跑通，改数据即可。
