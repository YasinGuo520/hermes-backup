// 通用数据榜单视频组件（已验证可渲染）
// 用法：改 STOCKS 数组（code/name/total/disagreement）+ 标题文字即可出片
// 竖屏 1080x1920 / 30fps / 300帧(10秒)
// 项目结构：src/index.tsx(registerRoot) → src/Root.tsx(Composition) → 本组件
// Root.tsx 注册: <Composition id="DataShowcase" component={DataShowcase} durationInFrames={300} fps={30} width={1080} height={1920} />

import React, { useMemo } from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ===== 数据源（替换为真实数据，量化场景读 quant-skill/logs/<date>.json 的 top_k）=====
const STOCKS = [
  { code: "600900", name: "长江电力", total: 0.3498932574422854, disagreement: 0.147 },
  { code: "601127", name: "赛力斯", total: 0.2885282230447208, disagreement: 0.093 },
  { code: "300750", name: "宁德时代", total: 0.28469597135155494, disagreement: 0.204 },
  { code: "601857", name: "中国石油", total: 0.2708600703279891, disagreement: 0.016 },
  { code: "000858", name: "五粮液", total: 0.2651405792582107, disagreement: 0.148 },
  { code: "600406", name: "国电南瑞", total: 0.2615201593264253, disagreement: 0.039 },
  { code: "601328", name: "交通银行", total: 0.2561809993832195, disagreement: 0.029 },
  { code: "002142", name: "宁波银行", total: 0.23102439831640148, disagreement: 0.074 },
];

const DATE = "2026-07-31";
const N_SCORED = 69;

const RED = "#ef4444";
const GREEN = "#22c55e";
const YELLOW = "#facc15";

const disagreementLabel = (d: number) => {
  if (d < 0.05) return { text: "信号一致", color: GREEN };
  if (d < 0.15) return { text: "中性", color: YELLOW };
  return { text: "分歧", color: RED };
};

// ===== 粒子背景（固定种子，SVG 圆点 + 极光光晕）=====
const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const dots = useMemo(() => {
    let seed = 42; // 固定种子，否则每帧重生成 → 画面抖动
    const rnd = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };
    return Array.from({ length: 60 }, (_, i) => ({
      id: i,
      x: rnd() * width,
      y: rnd() * height,
      r: 1.5 + rnd() * 3.5,
      speed: 0.4 + rnd() * 1.2,
      phase: rnd() * Math.PI * 2,
      opacity: 0.15 + rnd() * 0.5,
      hue: rnd(),
    }));
  }, [width, height]);

  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #070b22 0%, #0d1137 55%, #131a4d 100%)" }}>
      <div style={{ position: "absolute", top: -300, left: -200, width: 900, height: 900, borderRadius: "50%", background: "radial-gradient(circle, rgba(124,58,237,0.35) 0%, transparent 70%)" }} />
      <div style={{ position: "absolute", bottom: -400, right: -250, width: 1000, height: 1000, borderRadius: "50%", background: "radial-gradient(circle, rgba(34,211,238,0.22) 0%, transparent 70%)" }} />
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        {dots.map((d) => {
          const driftY = Math.sin((frame / 30) * d.speed + d.phase) * 40;
          const driftX = Math.cos((frame / 30) * d.speed * 0.7 + d.phase) * 25;
          const twinkle = 0.5 + 0.5 * Math.sin((frame / 18) * d.speed + d.phase);
          const fill = d.hue > 0.5 ? `rgba(167,139,250,${d.opacity * twinkle})` : `rgba(94,234,212,${d.opacity * twinkle})`;
          return <circle key={d.id} cx={d.x + driftX} cy={d.y + driftY} r={d.r} fill={fill} />;
        })}
      </svg>
    </AbsoluteFill>
  );
};

// ===== 玻璃卡片行（stagger 弹入 + 数字滚动）=====
const Row: React.FC<{ stock: (typeof STOCKS)[number]; rank: number; delay: number }> = ({ stock, rank, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame: frame - delay, fps, config: { damping: 200, stiffness: 80 } });
  const score = stock.total * 100;
  const animatedScore = interpolate(frame, [delay + 15, delay + 45], [0, score], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const dg = disagreementLabel(stock.disagreement);
  const rankColors = ["#fbbf24", "#cbd5e1", "#d97706"];

  return (
    <div style={{ opacity: enter, transform: `translateY(${(1 - enter) * 40}px)`, display: "flex", alignItems: "center", background: "rgba(255,255,255,0.055)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 22, padding: "20px 28px", marginBottom: 18, backdropFilter: "blur(18px)", boxShadow: "0 8px 32px rgba(0,0,0,0.35)" }}>
      <div style={{ width: 64, height: 64, borderRadius: 18, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34, fontWeight: 800, color: rankColors[rank] || "#94a3b8", background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", marginRight: 24 }}>{rank + 1}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 40, fontWeight: 700, color: "#f1f5f9", letterSpacing: 1 }}>
          {stock.name}
          <span style={{ fontSize: 26, fontWeight: 400, color: "#64748b", marginLeft: 14 }}>{stock.code}</span>
        </div>
        <div style={{ fontSize: 26, color: "#94a3b8", marginTop: 4 }}>分歧度 {stock.disagreement.toFixed(3)}</div>
      </div>
      <div style={{ textAlign: "right" }}>
        <div style={{ fontSize: 52, fontWeight: 800, fontVariantNumeric: "tabular-nums", background: "linear-gradient(90deg,#a78bfa,#818cf8,#22d3ee)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", lineHeight: 1 }}>{animatedScore.toFixed(2)}</div>
        <div style={{ display: "inline-block", marginTop: 8, padding: "4px 16px", borderRadius: 999, fontSize: 22, fontWeight: 600, color: dg.color, background: `${dg.color}1f`, border: `1px solid ${dg.color}55` }}>{dg.text}</div>
      </div>
    </div>
  );
};

// ===== 主画面 =====
export const DataShowcase: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleIn = spring({ frame, fps, config: { damping: 200, stiffness: 90 } });
  const subIn = spring({ frame: frame - 8, fps, config: { damping: 200, stiffness: 90 } });

  return (
    <AbsoluteFill style={{ fontFamily: "PingFang SC, Microsoft YaHei, sans-serif" }}>
      <Particles />
      <div style={{ position: "absolute", top: 120, left: 0, right: 0, textAlign: "center", opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)` }}>
        <div style={{ fontSize: 30, letterSpacing: 8, color: "#818cf8", fontWeight: 600, marginBottom: 16 }}>A股量化 · 多因子信号</div>
        <div style={{ fontSize: 84, fontWeight: 900, letterSpacing: 4, background: "linear-gradient(90deg,#c4b5fd,#818cf8,#22d3ee)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", textShadow: "0 0 60px rgba(129,140,248,0.35)" }}>TOP 8 榜单</div>
        <div style={{ opacity: subIn, fontSize: 30, color: "#94a3b8", marginTop: 14, letterSpacing: 2 }}>{DATE} · 扫描 {N_SCORED} 只标的 · 红涨绿跌信号</div>
      </div>
      <div style={{ position: "absolute", top: 480, left: 56, right: 56 }}>
        {STOCKS.map((s, i) => <Row key={s.code} stock={s} rank={i} delay={20 + i * 7} />)}
      </div>
      <div style={{ position: "absolute", bottom: 90, left: 0, right: 0, textAlign: "center", fontSize: 24, color: "#475569", letterSpacing: 1 }}>量化糅合系统 v2 · tech 0.45 / kronos 0.30 / flow 0.25 · 信号仅供研究</div>
    </AbsoluteFill>
  );
};
