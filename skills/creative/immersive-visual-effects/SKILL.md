---
name: immersive-visual-effects
description: 全屏沉浸式页面视觉特效 — Canvas粒子星空/叙事动画序列/交互式庆祝元素，适用于大气/科幻/创意/庆祝类页面
---

# 沉浸式视觉特效（Canvas + CSS）

> 当 Yasin 要求「大气」「全屏」「科幻」「庆祝」「沉浸感」风格时使用。
> 与 UX Pro Max 互补：那个管UI规范，这个管视觉特效。

## 一、适用场景判断

| 关键词 | 模式 |
|--------|------|
| 「大气」「科幻」「炫酷」 | 深空全屏模式 |
| 「庆祝」「生日」「节日」 | 叙事庆祝模式 |
| 「飘逸」「梦幻」「星空」 | 粒子星空模式 |
| 「交互」「点击」「互动」 | 加交互层 |

## 二、深空全屏模式（大气/科幻）

### 层级结构（z-index）
```
z:0  Canvas粒子星空     — 流动星光拖尾
z:1  环境光晕渐变        — radial-gradient环境光
z:1  浮动装饰物          — 六边形/菱形水晶 (clip-path)
z:2  主内容             — Hero/标题/核心元素
z:3  交互装饰           — 气球/漂浮物
z:5  音乐开关           — 右上角固定
z:10 礼物盒/浮窗        — 右下角 + 弹出层
z:999 Confetti canvas   — 最顶层
```

### 深色系配色

除 UX Pro Max 标准配色外，深空模式专用：

```
背景底色:  #0a0a12 或 #0b0c12
主色:      #a78bfa / #818cf8（紫系）
强调色:    #fbbf24（金） + #f472b6（粉） + #67e8f9（青）
文字:      #e2e8f0 / #94a3b8
卡片:      rgba(15,15,30,0.5) + backdrop-filter:blur(20px)
卡片边框:  rgba(139,92,246,0.06)
粒子色:    同上主色/强调色
水晶:      polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%)
水晶渐变:  同上强调色组合
```

### CSS 水晶浮动装饰

```css
.crystal{
  position:absolute;
  clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
  opacity:0.07;
  animation:cryFloat 22s ease-in-out infinite;
}
@keyframes cryFloat{
  0%,100%{transform:translateY(0)rotate(0deg)scale(1);opacity:0.07;}
  33%{transform:translateY(-18px)rotate(8deg)scale(1.08);opacity:0.13;}
  66%{transform:translateY(12px)rotate(-6deg)scale(0.93);opacity:0.05;}
}
```

## 三、叙事庆祝模式（生日/节日）

### 多阶段入场序列

```
阶段1 (0s):   背景 + Canvas粒子就位
阶段2 (0.5s): 名字逐字弹出 (每个字间隔150-250ms)
阶段3 (2-3s): 核心元素旋转出现 (badge/徽章)
阶段4 (4-5s): 祝福文字逐行显现 (每行间隔500-800ms)
阶段5 (6s+):  交互元素就绪 (音乐/气球/礼物盒)
```

### 名字逐字弹出

```html
<div id="name"></div>
<script>
const name = '郭泽莹';
nameEl.innerHTML = '';
for(const ch of name){
  const span = document.createElement('span');
  span.className = 'char';
  span.textContent = ch;
  nameEl.appendChild(span);
}
// CSS: .char{opacity:0;transform:translateY(40px);transition:all 0.6s cubic-bezier(0.34,1.56,0.64,1);}
// JS: chars.forEach((ch,i)=>setTimeout(()=>ch.classList.add('show'),i*200));
</script>
```

### 打字机式祝福语

```html
<div class="message">
  <div class="line">第一行 🌟</div>
  <div class="line">第二行 ✨</div>
</div>
```
```css
.message .line{opacity:0;transform:translateY(10px);transition:all 0.6s ease;}
.message .line.show{opacity:1;transform:translateY(0);}
```
```javascript
document.querySelectorAll('.message .line')
  .forEach((l,i)=>setTimeout(()=>l.classList.add('show'),i*600+300));
```

## 四、交互元素集

### 4.1 点击彩花粒子（Confetti）

```javascript
// Canvas confetti engine
const pieces=[], colors=[/* 10种彩色 */];
function burst(cx,cy){
  for(let i=0;i<150;i++){
    const angle=Math.random()*Math.PI*2,speed=Math.random()*16+5;
    pieces.push({
      x:cx+(Math.random()-0.5)*100,y:cy+(Math.random()-0.5)*80,
      vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed-7,
      r:Math.random()*5+2,color,rot:Math.random()*360,
      rotSp:(Math.random()-0.5)*18,
      life:180+Math.random()*120,gravity:0.2+Math.random()*0.1,drag:0.97
    });
  }
  // requestAnimationFrame loop: 每帧位移+旋转+衰减
}
```

### 4.2 轨道旋转光环（吧唧/徽章）

```css
.ring{
  position:absolute;border-radius:50%;border:2px solid rgba(...);
  animation:spin 20s linear infinite;
}
@keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
.ring2{border-style:dashed;animation:spin 30s linear infinite reverse;}
.ring3{...;animation:spin 40s linear infinite;}

/* 卫星粒子 */
.orbits span{
  position:absolute;top:50%;left:50%;width:5px;height:5px;border-radius:50%;
  animation:orbF 6s linear infinite;
  /* use CSS custom properties for orbit radius and initial angle:
     --r: 50px; --deg: 0deg;
     transform:rotate(var(--deg)) translateX(var(--r));
  */
}
@keyframes orbF{
  0%{transform:rotate(var(--deg))translateX(var(--r));opacity:1;}
  50%{opacity:0.2;}
  100%{transform:rotate(calc(var(--deg)+360deg))translateX(var(--r));opacity:1;}
}
```

### 4.3 礼物盒弹出层

```html
<div class="gift-area" id="giftBtn">🎁</div>
<div class="gift-overlay" id="giftOverlay">
  <div class="gift-card">
    <!-- 内容 -->
  </div>
</div>
```
```css
.gift-overlay{
  position:fixed;inset:0;z-index:20;
  background:rgba(0,0,0,0.55);backdrop-filter:blur(10px);
  opacity:0;pointer-events:none;transition:all 0.5s ease;
}
.gift-overlay.show{opacity:1;pointer-events:auto;}
.gift-card{
  transform:scale(0.85);transition:transform 0.5s cubic-bezier(0.34,1.56,0.64,1);
}
.gift-overlay.show .gift-card{transform:scale(1);}
```

### 4.4 浮动气球

```javascript
const emojis=['🎈','🎈','🎈'];
for(let i=0;i<5;i++){
  const b=document.createElement('div');
  b.className='balloon';
  b.textContent=emojis[i%emojis.length];
  b.style.left=(10+Math.random()*75)+'%';
  b.style.top=(10+Math.random()*70)+'%';
  b.style.animationDuration=(3+Math.random()*2)+'s';
  b.addEventListener('click',function(){this.classList.add('popped');});
  document.body.appendChild(b);
}
```
```css
.balloon{
  position:fixed;font-size:2rem;cursor:pointer;z-index:3;
  animation:balFloat linear infinite;
  transition:all 0.2s ease;
}
@keyframes balFloat{
  0%,100%{transform:translateY(0)rotate(-1deg);}
  50%{transform:translateY(-18px)rotate(1deg);}
}
.balloon.popped{
  transform:scale(2) !important;opacity:0 !important;
  transition:all 0.3s ease;pointer-events:none;
}
```

### 4.5 背景音乐（Web Audio API）

```javascript
const btn=document.getElementById('musicToggle');
let playing=false,audioCtx=null;
btn.addEventListener('click',()=>{
  if(!playing){
    audioCtx=new (window.AudioContext||window.webkitAudioContext)();
    const notes=[262,294,330,349,392,440,494,523]; // C4-C5
    let idx=0;
    function playNote(){
      if(!playing||!audioCtx)return;
      const o=audioCtx.createOscillator();
      const g=audioCtx.createGain();
      o.type='sine';
      o.frequency.value=notes[idx%notes.length];
      g.gain.setValueAtTime(0.035,audioCtx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.7);
      o.connect(g);g.connect(audioCtx.destination);
      o.start();o.stop(audioCtx.currentTime+0.7);
      idx++;setTimeout(playNote,550);
    }
    playing=true;playNote();
  }else{
    playing=false;audioCtx.close();
  }
});
```

## 五、五角星/凹凸星（clip-path）

```css
.star{
  width:34px;height:34px;
  clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);
  background:linear-gradient(135deg,#fbbf24,#f59e0b);
  animation:starSpin 3s ease-in-out infinite;
  filter:drop-shadow(0 0 8px rgba(251,191,36,0.3));
}
@keyframes starSpin{
  0%,100%{transform:rotate(0deg)scale(1);}
  50%{transform:rotate(180deg)scale(1.1);}
}
```

## 六、Hack: CSS/SVG动漫化滤镜

> 当只有真人照片没有动漫图时，用SVG filter模拟。

```html
<svg style="position:fixed;width:0;height:0;" aria-hidden="true">
  <filter id="animeFx">
    <!-- 色阶离散化（模拟色块） -->
    <feComponentTransfer in="SourceGraphic" result="poster">
      <feFuncR type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
      <feFuncG type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
      <feFuncB type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
    </feComponentTransfer>
    <!-- 边缘检测（轮廓线） -->
    <feConvolveMatrix order="3" kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1"
      preserveAlpha="true" result="edge"/>
    <feColorMatrix in="edge" type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 6 0"/>
    <!-- 叠加 -->
    <feBlend in="poster" in2="edge" mode="multiply"/>
  </filter>
</svg>
```
```css
img{filter:url(#animeFx);}
```

**效果有限，只作为没有真动漫图时的兜底方案。最佳方案是找用户提供即梦AI/可灵AI生成的动漫图。**

## 七、性能指南

- Canvas粒子: 130+10帧拖尾 ≈ 桌面流畅，移动端粒子≤60拖尾≤6
- CSS动画: 优先用 transform/opacity（GPU合成），避免 animating width/height/top/left
- backdrop-filter: 谨慎使用，只用在非滚动固定元素上
- 多层z-index不会影响性能（不触发重排）
- 使用 `requestAnimationFrame` 而非 `setInterval`
