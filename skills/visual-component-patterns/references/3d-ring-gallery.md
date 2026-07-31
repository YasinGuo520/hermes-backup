# 3D 环形展厅组件（2026-07 沉淀）

> 来源：像素画展厅项目（~/Desktop/hermes/pixel-gallery/index.html，端口8915）。
> 用户拍板方向：沉浸式3D展示 > 平铺网格。适合作品集/画廊/产品展示页。

## 适用场景

- 作品集/画廊/展示页，用户要"炫酷"而不是"课件式逐幅展示"
- 深色科技风（星空粒子+玻璃卡片+渐变紫标题）是已确认的审美基线

## 核心结构

```
body
  .bg-grid        # 透视科技网格地板（rotateX 58deg + mask 径向渐隐）
  .bg-aurora      # 极光光晕（多层 radial-gradient + blur 30px）
  canvas#stars    # 星空粒子（金色70%+紫色30%，闪烁+漂移）
  header          # 渐变标题（金→白→紫）+ 操作提示
  .stage          # perspective:1300px；cursor:grab
    .ring         # preserve-3d；rotateX(10deg) rotateY(var(--ry))
      .card×10    # rotateY(var(--a)) translateZ(680px) translate(-50%,-50%)
  .overlay        # 视频/大图弹窗（毛玻璃+popIn入场）
```

## 关键实现

### 卡片环形定位

```css
.card{
  position:absolute;left:0;top:0;
  width:236px;height:318px;
  transform:rotateY(var(--a)) translateZ(680px) translate(-50%,-50%);
  transform-style:preserve-3d;
  animation:floatY var(--dur,6s) ease-in-out var(--delay,0s) infinite; /* 各自浮动 */
}
```
JS 生成：`const angle=(360/N)*i; card.style.setProperty('--a', angle+'deg');`
注意 floatY keyframes 里也要带上 `rotateY(var(--a)) translateZ(...) translate(-50%,-50%) translateY(...)`——**动画会覆盖静态 transform**，keyframes 必须完整复写否则卡片飞掉。

### 拖拽旋转

```js
let ry=-20, rx=10, dragging=false, autoRot=true;
stage.addEventListener('mousedown', e=>{dragging=true; startX=e.clientX; baseRy=ry;});
window.addEventListener('mousemove', e=>{ if(!dragging)return; ry=baseRy+(e.clientX-startX)*0.35; applyTransform(); });
window.addEventListener('mouseup', ()=>{dragging=false;});
// 自动慢转
setInterval(()=>{ if(!dragging && overlay未开) ry+=0.06; applyTransform(); }, 50);
```
- 拖拽时 `autoRot=false` 停自动转，松手后不恢复也行（用户已控制）
- 触摸事件 touchstart/touchmove/touchend 必须带 `{passive:true}`，否则滚动卡顿
- rx 限制 `Math.max(-30, Math.min(40, ...))` 防翻车

### 玻璃卡片 hover 弹出

```css
.card .inner{ background:linear-gradient(165deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02));
  border:1px solid rgba(240,200,96,0.28); backdrop-filter:blur(10px); }
.card:hover .inner{ transform:translateZ(46px); border-color:rgba(240,200,96,0.65);
  box-shadow:0 0 46px rgba(240,200,96,0.18); }
```
- 扫光：`.inner::after` 渐变 `background-size:250%` + `animation:sheen 1.6s linear infinite`（background-position 120%→-120%）
- 播放按钮：圆形渐变（金→紫）+ `::before` 三角，hover scale 1.15

### 渐变标题（金→白→紫）

```css
header h1{
  background:linear-gradient(100deg,var(--gold) 10%,#fff3d0 38%,var(--purple) 72%,var(--purple-2) 95%);
  -webkit-background-clip:text;background-clip:text;
  -webkit-text-fill-color:transparent;color:transparent;
  filter:drop-shadow(0 0 22px rgba(240,200,96,0.25));
}
```

### 星空粒子 Canvas（金色主调）

```js
const pts=Array.from({length:90},()=>({
  x:Math.random()*W,y:Math.random()*H, r:Math.random()*1.6+0.4,
  vx:(Math.random()-0.5)*0.25,vy:(Math.random()-0.5)*0.25,
  c:Math.random()<0.72?'240,200,96':'139,92,246',   // 金色72% 紫28%
  tw:Math.random()*Math.PI*2,                        // 闪烁相位
}));
// draw: p.tw+=0.02; a=0.25+Math.abs(Math.sin(p.tw))*0.6;
```

### 视频弹窗（复用现有视频）

- `video src='videos/<file>.mp4'` controls autoplay loop playsinline
- `popIn` 入场动画 `from{transform:scale(0.92);opacity:0}`
- 关闭：点击遮罩自身或按钮；Esc 键监听

## 响应式

- `@media(max-width:700px)`：卡片缩到 176x240，`translateZ(430px)`，perspective 900px，标题1.5rem
- **移动端必须改 translateZ**，否则环形半径过大卡片全在屏幕外

## 踩坑清单

1. floatY keyframes 完整复写 transform（含 rotateY/translateZ），否则 hover 悬浮后卡片位置错乱
2. 触摸事件 passive:true
3. 移动端 translateZ 半径要缩小
4. 拖拽只在 stage 上 mousedown，mousemove/mouseup 挂 window（否则拖出元素就停）
5. 自动旋转期间打开弹窗要暂停（检查 overlay class），否则背景还在转
6. 卡片 img 加 `draggable="false"` 防拖拽图片触发浏览器拖图
7. 渐变文字要同时设 `-webkit-text-fill-color:transparent` 和 `color:transparent`，否则 WebKit 显示黑字
8. 视觉验证时截全页 + 弹窗两个状态，别只截一个

## 在线案例

- 像素画展厅 3D 版：http://43.138.221.174:8915/
- 完整源码：~/Desktop/hermes/pixel-gallery/index.html（可直接复制改）
