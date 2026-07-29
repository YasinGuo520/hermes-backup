# Canvas 粒子星空背景（可复用模板）

> 适用场景：全屏沉浸式页面底层，深空背景 + 流动星光拖尾
> 引用自: immersive-visual-effects skill

## 核心结构

```html
<canvas id="starfield"></canvas>
```
```css
#starfield{position:fixed;inset:0;z-index:0;pointer-events:none;}
```

## 配置速查

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 粒子数 | 120-150 | 移动端降至60 |
| 粒子色 | #a78bfa, #f472b6, #fbbf24, #67e8f9 | 紫/粉/金/青 |
| 粒子尺寸 | 0.4-2.4px | — |
| 拖尾长度 | 10-12帧 | 短拖尾更清晰 |
| 速度X | ±0.35 | 横向漂移 |
| 速度Y | 0.08-0.33 | 纵向上升 |

## 完整代码

```javascript
(function(){
  const c = document.getElementById('starfield');
  const ctx = c.getContext('2d');
  let w = c.width = window.innerWidth;
  let h = c.height = window.innerHeight;

  const stars = [];
  const colors = ['#a78bfa','#f472b6','#fbbf24','#67e8f9','#e2e8f0'];

  for(let i = 0; i < 130; i++){
    stars.push({
      x: Math.random() * w,
      y: Math.random() * h,
      size: Math.random() * 2.2 + 0.4,
      speedX: (Math.random() - 0.5) * 0.35,
      speedY: Math.random() * 0.25 + 0.08,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: Math.random() * 0.5 + 0.15,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: Math.random() * 0.02 + 0.005,
      trail: []
    });
  }

  function draw(){
    ctx.clearRect(0, 0, w, h);
    for(const s of stars){
      // 拖尾
      s.trail.push({x: s.x, y: s.y});
      if(s.trail.length > 10) s.trail.shift();
      for(let t = 0; t < s.trail.length; t++){
        const alpha = (t / s.trail.length) * s.alpha * 0.35;
        const radius = s.size * (t / s.trail.length);
        ctx.beginPath();
        ctx.arc(s.trail[t].x, s.trail[t].y, radius, 0, Math.PI * 2);
        ctx.fillStyle = hexToRgba(s.color, alpha);
        ctx.fill();
      }
      // 星核
      s.pulse += s.pulseSpeed;
      const glow = Math.sin(s.pulse) * 0.3 + 0.7;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.size * glow, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.globalAlpha = s.alpha * glow;
      ctx.fill();
      ctx.globalAlpha = 1;
      // 外发光（大粒子）
      if(s.size > 1.3){
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.size * 3 * glow, 0, Math.PI * 2);
        ctx.fillStyle = s.color;
        ctx.globalAlpha = 0.03 * glow;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      // 位移 + 环绕
      s.x += s.speedX;
      s.y -= s.speedY;
      if(s.y < -20){ s.y = h + 10; s.x = Math.random() * w; }
      if(s.x < -20) s.x = w + 10;
      if(s.x > w + 20) s.x = -10;
    }
    requestAnimationFrame(draw);
  }

  function hexToRgba(hex, alpha){
    const r = parseInt(hex.slice(1,3), 16);
    const g = parseInt(hex.slice(3,5), 16);
    const b = parseInt(hex.slice(5,7), 16);
    return `rgba(${r},${g},${b},${alpha})`;
  }

  draw();
  window.addEventListener('resize', ()=>{
    w = c.width = window.innerWidth;
    h = c.height = window.innerHeight;
  });
})();
```

## 变体

| 变体 | 改动 |
|------|------|
| 简约无拖尾 | 去掉 trail 相关代码 |
| 彩色雨（斜坠） | speedX±0.5-1.0, speedY +0.5-1.0, 粒子减至50-80 |
| 极光大光晕 | 粒子30-40, 尺寸5-15px, alpha 0.02-0.05 |

## 性能

- 130粒子+10帧拖尾 = ~1300次drawCall/帧，桌面流畅
- 移动端: 粒子≤60, 拖尾≤6帧
- resize时重置canvas尺寸
