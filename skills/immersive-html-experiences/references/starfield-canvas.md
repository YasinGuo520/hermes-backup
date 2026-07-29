# 星空粒子 Canvas（流动拖尾版）

用于沉浸式深空背景。130颗彩色星点，带10帧拖尾、脉冲亮度和辉光层。

## 核心代码

```javascript
const c = document.getElementById('starfield');
const ctx = c.getContext('2d');
let w = c.width = window.innerWidth;
let h = c.height = window.innerHeight;

const stars = [];
const colors = ['#a78bfa','#f472b6','#fbbf24','#67e8f9','#e2e8f0'];

for(let i = 0; i < 130; i++){
  stars.push({
    x: Math.random()*w, y: Math.random()*h,
    s: Math.random()*2.2 + 0.4,          // size
    dx: (Math.random()-0.5)*0.35,        // drift X
    dy: Math.random()*0.25 + 0.08,       // drift Y (向上)
    col: colors[Math.floor(Math.random()*colors.length)],
    a: Math.random()*0.5 + 0.15,         // alpha
    ph: Math.random()*Math.PI*2,         // pulse phase
    ps: Math.random()*0.02 + 0.005,      // pulse speed
    tr: []                                // trail array
  });
}

function draw(){
  ctx.clearRect(0, 0, w, h);
  for(const s of stars){
    // Trail
    s.tr.push({x:s.x, y:s.y});
    if(s.tr.length > 10) s.tr.shift();
    for(let t = 0; t < s.tr.length; t++){
      const al = (t/s.tr.length) * s.a * 0.35;
      const r = s.s * (t/s.tr.length);
      ctx.beginPath();
      ctx.arc(s.tr[t].x, s.tr[t].y, r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${hexRGB(s.col)},${al})`;
      ctx.fill();
    }

    // Star body + glow
    s.ph += s.ps;
    const gl = Math.sin(s.ph) * 0.3 + 0.7;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.s * gl, 0, Math.PI*2);
    ctx.fillStyle = s.col;
    ctx.globalAlpha = s.a * gl;
    ctx.fill();
    ctx.globalAlpha = 1;

    // Glow layer (only for bigger stars)
    if(s.s > 1.3){
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.s * 3 * gl, 0, Math.PI*2);
      ctx.fillStyle = s.col;
      ctx.globalAlpha = 0.03 * gl;
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    // Move
    s.x += s.dx;
    s.y -= s.dy;
    if(s.y < -20){ s.y = h+10; s.x = Math.random()*w; }
    if(s.x < -20) s.x = w+10;
    if(s.x > w+20) s.x = -10;
  }
  requestAnimationFrame(draw);
}
draw();

// Resize handler
window.addEventListener('resize', ()=>{
  w = c.width = window.innerWidth;
  h = c.height = window.innerHeight;
});

// Helper: hex to rgba
function hexRGB(hex){
  return `${parseInt(hex.slice(1,3),16)},${parseInt(hex.slice(3,5),16)},${parseInt(hex.slice(5,7),16)}`;
}
```

## 关键参数表

| 参数 | 值 | 效果 |
|------|-----|------|
| 粒子数 | 130 | 稀疏有太空感，不密集 |
| 拖尾长度 | 10帧 | 流畅不模糊 |
| 速度Y | 0.08-0.33 | 缓慢上飘，像银河流动 |
| 速度X | ±0.175 | 轻微左右漂移 |
| 大小 | 0.4-2.6px | 远近层次感 |
| 辉光倍数 | 3x | 大星有光晕 |
| 脉冲幅度 | ±30% | 星星忽明忽暗 |

## 变体

- **更多粒子**（200+）：适合科幻密集星空
- **更快拖尾**（6帧）：更明显的流动感
- **对角线运动**：改变 dx/dy 比例，创造流星雨效果
- **粒子连线**：150px内星星连线（参考初版portfolio页面）
