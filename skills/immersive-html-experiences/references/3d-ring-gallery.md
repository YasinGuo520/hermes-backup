# 3D 环形画廊（可拖拽旋转展厅）

CSS 3D 展厅模式：作品卡片环绕 3D 空间，鼠标/触屏拖拽旋转，松手自动慢速自转。实测于 pixel-gallery 8915 端口（深空粒子+科技网格+玻璃卡片）。

## 关键 CSS

```css
.stage{
  position:fixed;inset:0;z-index:3;
  perspective:1300px;
  display:flex;align-items:center;justify-content:center;
  cursor:grab;user-select:none;
}
.stage.dragging{cursor:grabbing;}
.ring{
  position:relative;transform-style:preserve-3d;
  width:0;height:0;
  transform:rotateX(10deg) rotateY(var(--ry,0deg));
}
.card{
  position:absolute;left:0;top:0;
  width:236px;height:318px;
  transform:rotateY(var(--a)) translateZ(680px) translate(-50%,-50%);
  cursor:pointer;
}
/* hover 弹出 + 扫光 */
.card:hover .inner{transform:translateZ(46px);}
.card .inner::after{  /* 金色扫光 */
  content:'';position:absolute;inset:0;border-radius:14px;
  background:linear-gradient(120deg,transparent 30%,rgba(240,200,96,0.28) 50%,transparent 70%);
  background-size:250% 250%;opacity:0;
}
.card:hover .inner::after{opacity:1;animation:sheen 1.6s linear infinite;}
```

每张卡片 `--a = (360/N)*i`。移动端：`translateZ(430px)` + 卡片缩到 176x240 + `perspective:900px`。

## 悬浮浮动动画（错峰）

```css
.card{animation:floatY var(--dur,6s) ease-in-out var(--delay,0s) infinite;}
@keyframes floatY{
  0%,100%{transform:rotateY(var(--a)) translateZ(680px) translate(-50%,-50%) translateY(0);}
  50%{transform:rotateY(var(--a)) translateZ(680px) translate(-50%,-50%) translateY(-16px);}
}
.card:hover{animation-play-state:paused;}
```

JS 里 `--dur = 5.5+(i%4)*0.9`、`--delay = i*0.45` 错峰。

## 拖拽旋转 + 自动自转

```js
let ry=-20, rx=10, dragging=false, startX=0, startY=0, baseRy=0, baseRx=0;
function applyTransform(){
  ring.style.setProperty('--ry',ry+'deg');
  ring.style.transform=`rotateX(${rx}deg) rotateY(${ry}deg)`;
}
stage.addEventListener('mousedown',e=>{
  dragging=true;stage.classList.add('dragging');
  startX=e.clientX;startY=e.clientY;baseRy=ry;baseRx=rx;
});
window.addEventListener('mousemove',e=>{
  if(!dragging)return;
  ry=baseRy+(e.clientX-startX)*0.35;
  rx=Math.max(-30,Math.min(40,baseRx-(e.clientY-startY)*0.2));
  applyTransform();
});
window.addEventListener('mouseup',()=>{dragging=false;stage.classList.remove('dragging');});
// 触屏: touchstart/touchmove/touchend，用 e.touches[0]，passive:true
// 自动慢速自转（弹窗打开时暂停）
setInterval(()=>{
  if(!dragging && !overlay.classList.contains('active')){ry+=0.06;applyTransform();}
},50);
```

## 背景三层

1. 透视网格地板：`transform:perspective(900px) rotateX(58deg) scale(1.6) translateY(34%)` + `mask-image:radial-gradient(...)` 径向渐隐
2. 极光光晕：多个 `radial-gradient` + `filter:blur(30px)`
3. Canvas 星空粒子：90 颗金色/紫色粒子漂移 + 闪烁（`Math.sin(tw)` 透明度）

## 弹窗播放视频（同一页面模式）

点卡片 → 深色遮罩 `rgba(5,6,12,0.88)` + `backdrop-filter:blur(14px)`，视频必须包 `.video-frame` 且按视口高度换算 max-width（见主 SKILL.md「嵌入渲染视频」——这是实测踩过的 16:9 溢出坑）。
