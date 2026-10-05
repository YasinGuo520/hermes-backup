# 电路板 Canvas 背景动画

PCB电路板风格的Canvas背景动画，用于科技工具风格的深色页面。
含栅格轨迹线、脉冲节点、流动数据包信号。

## 效果说明

- **PCB栅格轨迹线**：随机水平/垂直走线，每帧重新采样（静态密度波动）
- **脉冲节点**：网格排列的焊接点，带正弦呼吸脉冲
- **流动数据包**：在两个随机节点间移动的发光粒子，带径向渐变光晕
- 整体通过 `opacity: 0.35` 控制可见度，不影响上层内容可读性

## 完整实现代码

```html
<canvas id="circuit-canvas"></canvas>
```

```css
#circuit-canvas {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 0; pointer-events: none;
  opacity: 0.35;
}
```

```javascript
const canvas = document.getElementById('circuit-canvas');
const ctx = canvas.getContext('2d');
let w, h;
function resize() {
  w = canvas.width = window.innerWidth;
  h = canvas.height = document.body.scrollHeight;
}
window.addEventListener('resize', resize);
resize();

// === 节点网格 ===
const nodeSpacing = 80;
const cols = Math.ceil(w / nodeSpacing) + 4;
const rows = Math.ceil(h / nodeSpacing) + 4;
let nodes = [];
let signals = [];

function initCircuit() {
  nodes = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const offsetX = (r % 2) * (nodeSpacing / 2);
      nodes.push({
        x: c * nodeSpacing + offsetX + (Math.random() - 0.5) * 12,
        y: r * nodeSpacing + (Math.random() - 0.5) * 12,
        pulse: Math.random() * Math.PI * 2,
        connected: Math.random() > 0.25
      });
    }
  }
  // 流动信号（数据包）
  signals = [];
  for (let i = 0; i < 12; i++) {
    const a = Math.floor(Math.random() * nodes.length);
    const b = Math.floor(Math.random() * nodes.length);
    signals.push({
      x: nodes[a].x, y: nodes[a].y,
      targetX: nodes[b].x, targetY: nodes[b].y,
      progress: Math.random(),
      speed: 0.003 + Math.random() * 0.006,
      size: 1.5 + Math.random() * 2
    });
  }
}
initCircuit();

function drawCircuit() {
  ctx.clearRect(0, 0, w, h);
  const gridX = Math.floor(w / 40);
  const gridY = Math.floor(h / 40);
  ctx.strokeStyle = 'rgba(0,212,255,0.04)';
  ctx.lineWidth = 0.5;

  // 水平轨迹线
  for (let row = 0; row < gridY; row++) {
    if (Math.random() > 0.15) {
      const y = row * 40 + 10;
      const startX = Math.floor(Math.random() * 20) * 40;
      const endX = startX + 60 + Math.floor(Math.random() * 15) * 40;
      ctx.beginPath();
      ctx.moveTo(startX, y);
      ctx.lineTo(Math.min(endX, w), y);
      ctx.stroke();
    }
  }

  // 垂直轨迹线
  for (let col = 0; col < gridX; col++) {
    if (Math.random() > 0.15) {
      const x = col * 40 + 10;
      const startY = Math.floor(Math.random() * 20) * 40;
      const endY = startY + 60 + Math.floor(Math.random() * 12) * 40;
      ctx.beginPath();
      ctx.moveTo(x, startY);
      ctx.lineTo(x, Math.min(endY, h));
      ctx.stroke();
    }
  }

  // 脉冲节点
  for (const node of nodes) {
    if (!node.connected) continue;
    node.pulse += 0.02;
    const pulseSize = 1.5 + Math.sin(node.pulse) * 0.8;
    const alpha = 0.15 + Math.sin(node.pulse) * 0.08;
    ctx.beginPath();
    ctx.arc(node.x, node.y, pulseSize, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0,212,255,${alpha})`;
    ctx.fill();
  }

  // 节点间连接线
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const d = Math.sqrt(dx*dx + dy*dy);
      if (d < nodeSpacing * 1.2 && nodes[i].connected && nodes[j].connected) {
        const alpha = 0.03 * (1 - d / (nodeSpacing * 1.2));
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.strokeStyle = `rgba(0,212,255,${alpha})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }
  }

  // 流动数据包信号
  for (const s of signals) {
    s.progress += s.speed;
    if (s.progress >= 1) {
      s.progress = 0;
      const a = Math.floor(Math.random() * nodes.length);
      const b = Math.floor(Math.random() * nodes.length);
      s.x = nodes[a].x;
      s.y = nodes[a].y;
      s.targetX = nodes[b].x;
      s.targetY = nodes[b].y;
    }
    const cx = s.x + (s.targetX - s.x) * s.progress;
    const cy = s.y + (s.targetY - s.y) * s.progress;

    // 光晕
    const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, s.size * 3);
    gradient.addColorStop(0, 'rgba(0,212,255,0.6)');
    gradient.addColorStop(0.3, 'rgba(0,212,255,0.2)');
    gradient.addColorStop(1, 'rgba(0,212,255,0)');
    ctx.beginPath();
    ctx.arc(cx, cy, s.size * 3, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    // 核心亮点
    ctx.beginPath();
    ctx.arc(cx, cy, s.size, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0,212,255,0.9)';
    ctx.fill();
  }
}

function animate() {
  drawCircuit();
  requestAnimationFrame(animate);
}
animate();
```

## 关键参数调优

| 参数 | 值 | 效果 |
|------|-----|------|
| `nodeSpacing` | 80 | 节点间距（越小越密） |
| `opacity` (CSS) | 0.35 | 整体可见度 |
| `opacity` (CSS) → 0.5-0.6 | 更亮 | 主背景较浅时用 |
| `signals[i].speed` | 0.003-0.009 | 信号流动速度 |
| `signals` 数量 | 8-15 | 同时流动的数据包数量 |
| `traces` stroke rgba alpha | 0.04 | 轨迹线亮度 |
| 节点 `alpha` 范围 | 0.07-0.23 | 节点的呼吸幅度 |

## 颜色适配

当前实现使用青色 `#00d4ff`，替换方法：
- 全局搜索 `0,212,255` → 替换为你的RGB值
- 例如紫色：`108,92,231` / 金色：`251,191,36` / 粉色：`244,114,182`
