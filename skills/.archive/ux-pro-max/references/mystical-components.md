# 玄学/古风视觉组件

> 从玄机灵签占卜页面提炼的可复用玄学风格组件。
> 适用场景：占卜、命理、古风、神秘学、传统文化类网页。

---

## 1. 烟雾粒子背景 (Smoke Particle)

Canvas 粒子系统模拟焚香烟雾，自底部升起、缓慢飘散、柔和消融。

### 实现要点

- 粒子自屏幕底部 70%-95% 区间生成
- 每个粒子拥有：位置(x,y)、速度(vx,vy)、半径(r)、生命(life/maxLife)、衰减率(decay)、漂移(drift)、旋转(rot)
- 上升过程中：半径逐渐增大(+0.08/frame)，透明度先升后降(0→0.12→0)
- 双层径向渐变绘制：主烟雾 blob + 偏移小的高光 blob，营造立体感
- 数量上限 80，自然衰减与补充平衡
- 点击抽签时触发爆发粒子（中心向外扩散的烟雾团）

### 关键参数

```js
// 自然生成
vy: -(0.15 + Math.random() * 0.35)   // 上升速度
r: 40 + Math.random() * 80            // 初始半径
decay: 0.003 + Math.random() * 0.003  // 生命衰减
maxLife: 0.8 + Math.random() * 0.6    // 最大生命

// 颜色
rgba(180,160,130, opacity)   // 主烟雾色
rgba(200,185,160, opacity)   // 高光层
```

---

## 2. 古风卷轴卡片 (Scroll Card)

宣纸底色 + 金色边框 + 上下卷轴杆 + 两端圆轴端盖的卡片组件。

### DOM 结构

```
.scroll-inner
  ├── .roller-end.l / .roller-end.r       (上卷轴两端圆盖)
  ├── .roller-end-b.l / .roller-end-b.r   (下卷轴两端圆盖)
  ├── .inner-border                        (内层金色细边框)
  ├── .light-sweep                          (光扫过场动画)
  ├── .fortune-icon / .fortune-title / ...
```

### 样式要点

- 主体背景：`linear-gradient(180deg, #f5e6c8, #f0dbb8, #e8d4a8)` — 宣纸渐变
- 边框：`2px solid #c9a84c`（古金色）
- 卷轴杆：`::before`/`::after` 伪元素，`linear-gradient(90deg, #8b6914, #c9a84c 20%, #e8d09a 50%, ...)` 模拟金属质感
- 圆轴端盖：`radial-gradient(circle at 40% 35%, #e8d09a, #8b6914)` + border-radius 50%
- 内部文字色深褐(#4a3a2a)，保持宣纸上的可读性

---

## 3. 印章按钮 (Seal Button)

暗红底+金边+金字的传统印章风格按钮。

### 样式要点

- 背景：`#8b0000`（暗红），悬停渐亮至 `#a00000`
- 边框：`2px solid #c9a84c`
- 字体：楷体/STKaiti + letter-spacing 加大
- 四角装饰点：`position:absolute; width:4px; height:4px; background:#c9a84c; border-radius:50%`
- 外圈：`.seal-ring` — `position:absolute; inset:-4px; border:1px solid rgba(201,168,76,0.2)`
- 悬停效果：box-shadow 向外扩展 + 颜色提亮 + translateY(-1px)
- 按下效果：`transform:scale(0.96)` 模拟印章按压

### 动效

```css
.btn-seal:hover {
  box-shadow:
    0 0 0 4px rgba(201,168,76,0.08),
    0 0 30px rgba(201,168,76,0.15),
    inset 0 0 30px rgba(201,168,76,0.08);
}
```

---

## 4. 烛光火焰装饰 (Candle Flame)

页面两侧的跳动烛火装饰元素。

### DOM

```html
<div class="candle-deco left"><div class="candle-flame"></div></div>
<div class="candle-deco right"><div class="candle-flame"></div></div>
```

### 样式要点

- 火焰形状：`border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%`（上宽下窄）
- 渐变：`linear-gradient(to top, #ff6600, #ffcc00, #fff5e0)`（底部橙红→顶部白黄）
- 跳动动画：交替缩放X/Y + 微幅上下位移
- 光晕：`box-shadow: 0 0 8px rgba(255,102,0,0.4), ...`
- 左右侧使用不同 `animation-delay` 产生错落感

---

## 5. 全局氛围叠层

### 烛光闪烁 (Candle Flicker Overlay)

```css
.candle-glow {
  background: radial-gradient(ellipse at 50% 80%, 
    rgba(200,100,30,0.06) 0%, 
    rgba(200,60,10,0.03) 30%, 
    transparent 70%);
  animation: candleFlicker 3s ease-in-out infinite alternate;
}
```

### 古风边角装饰

```css
/* 四角金角 */
.corner { position:absolute; width:40px; height:40px; border-color:#c9a84c; border-style:solid; opacity:0.25; }
.corner.tl { top:10px; left:10px; border-width:2px 0 0 2px; }

/* 几何纹样装饰条 */
.pattern-band {
  background: repeating-linear-gradient(90deg,
    transparent 0px, transparent 4px,
    #c9a84c 4px, #c9a84c 5px,
    ...);
}
```

---

## 颜色体系（玄学主题）

| 角色 | 色值 | 用途 |
|------|------|------|
| 背景 | `#0a0005` | 极深黑红基调 |
| 主色 | `#c9a84c` | 古金文字/边框/装饰 |
| 辅色 | `#8b0000` | 暗红按钮/重装饰 |
| 宣纸 | `#f5e6c8` ~ `#e8d4a8` | 卡片背景 |
| 文字(深色) | `#4a3a2a` | 卡片内文 |
| 文字(浅色) | `#d4c5a9` | 页面常规文字 |
