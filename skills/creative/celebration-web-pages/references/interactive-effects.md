# Interactive Effects Code — 庆祝页特效速查

> 本文件的完整代码片段可直接复制使用。
> 对应 `celebration-web-pages` 技能的各个交互模块。

---

## 1. 星点粒子场（80-130粒子 + 连线）

```html
<canvas id="starfield"></canvas>
```

```javascript
(function(){
  const c=document.getElementById('starfield'),ctx=c.getContext('2d');
  let w=c.width=window.innerWidth,h=c.height=window.innerHeight;
  const stars=[];
  const cols=['#a78bfa','#f472b6','#fbbf24','#67e8f9','#e2e8f0'];
  for(let i=0;i<100;i++)stars.push({
    x:Math.random()*w,y:Math.random()*h,
    r:Math.random()*1.8+0.3,dx:(Math.random()-0.5)*0.2,dy:(Math.random()-0.5)*0.2,
    col:cols[i%5],o:Math.random()*0.8+0.2
  });
  function draw(){
    ctx.clearRect(0,0,w,h);
    for(const s of stars){
      ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(129,140,248,${s.o})`;ctx.fill();
      s.x+=s.dx;s.y+=s.dy;
      if(s.x<0)s.x=w;if(s.x>w)s.x=0;if(s.y<0)s.y=h;if(s.y>h)s.y=0;
    }
    for(let i=0;i<stars.length;i++)
      for(let j=i+1;j<stars.length;j++){
        const dx=stars[i].x-stars[j].x,dy=stars[i].y-stars[j].y;
        const dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<150){
          ctx.beginPath();ctx.moveTo(stars[i].x,stars[i].y);ctx.lineTo(stars[j].x,stars[j].y);
          ctx.strokeStyle=`rgba(99,102,241,${0.08*(1-dist/150)})`;
          ctx.lineWidth=0.5;ctx.stroke();
        }
      }
    requestAnimationFrame(draw);
  }
  draw();
  window.addEventListener('resize',()=>{w=c.width=window.innerWidth;h=c.height=window.innerHeight;});
})();
```

---

## 2. 流动星光拖尾

```javascript
const stars=[],cols=['#a78bfa','#f472b6','#fbbf24','#67e8f9','#e2e8f0'];
for(let i=0;i<130;i++)stars.push({
  x:Math.random()*w,y:Math.random()*h,
  s:Math.random()*2.2+0.4,dx:(Math.random()-0.5)*0.35,dy:Math.random()*0.25+0.08,
  col:cols[Math.floor(Math.random()*cols.length)],
  a:Math.random()*0.5+0.15,ph:Math.random()*Math.PI*2,ps:Math.random()*0.02+0.005,
  tr:[]
});
function draw(){
  ctx.clearRect(0,0,w,h);
  for(const s of stars){
    s.tr.push({x:s.x,y:s.y});if(s.tr.length>10)s.tr.shift();
    for(let t=0;t<s.tr.length;t++){
      const al=(t/s.tr.length)*s.a*0.35,r=s.s*(t/s.tr.length);
      ctx.beginPath();ctx.arc(s.tr[t].x,s.tr[t].y,r,0,Math.PI*2);
      const rgb=hexToRgb(s.col);
      ctx.fillStyle=`rgba(${rgb.r},${rgb.g},${rgb.b},${al})`;ctx.fill();
    }
    ctx.beginPath();ctx.arc(s.x,s.y,s.s,0,Math.PI*2);
    ctx.fillStyle=s.col;ctx.globalAlpha=s.a;ctx.fill();ctx.globalAlpha=1;
    s.x+=s.dx;s.y-=s.dy;
    if(s.y<-20){s.y=h+10;s.x=Math.random()*w;}
    if(s.x<-20)s.x=w+10;if(s.x>w+20)s.x=-10;
  }
  requestAnimationFrame(draw);
}
function hexToRgb(h){return{r:parseInt(h.slice(1,3),16),g:parseInt(h.slice(3,5),16),b:parseInt(h.slice(5,7),16)};}
draw();
```

---

## 3. 彩花爆炸

```javascript
(function(){
  const canvas=document.getElementById('confetti-c'),ctx=canvas.getContext('2d');
  let w=canvas.width=window.innerWidth,h=canvas.height=window.innerHeight;
  let pieces=[],aid=null;
  const cs=['#f472b6','#818cf8','#fbbf24','#34d399','#f87171','#c084fc','#fde68a','#67e8f9'];

  function burst(cx,cy){
    if(!cx||!cy){cx=w/2;cy=h/2;}
    for(let i=0;i<150;i++){
      const an=Math.random()*Math.PI*2,sp=Math.random()*16+5;
      pieces.push({
        x:cx+(Math.random()-0.5)*100,y:cy+(Math.random()-0.5)*80,
        vx:Math.cos(an)*sp,vy:Math.sin(an)*sp-7,
        r:Math.random()*5+2,color:cs[Math.floor(Math.random()*cs.length)],
        rot:Math.random()*360,rotSp:(Math.random()-0.5)*18,
        life:180+Math.random()*120,gravity:0.2+Math.random()*0.1,drag:0.97
      });
    }
    if(!aid)aid=requestAnimationFrame(anim);
  }

  function anim(){
    ctx.clearRect(0,0,w,h);let alive=false;
    for(const p of pieces){
      p.x+=p.vx;p.y+=p.vy;p.vy+=p.gravity;p.vx*=p.drag;
      p.rot+=p.rotSp;p.life--;
      if(p.life>0){
        alive=true;ctx.save();ctx.translate(p.x,p.y);
        ctx.rotate(p.rot*Math.PI/180);ctx.globalAlpha=Math.min(1,p.life/50);
        ctx.fillStyle=p.color;ctx.fillRect(-p.r/2,-p.r/2,p.r,p.r*1.5);ctx.restore();
      }
    }
    if(alive)requestAnimationFrame(anim);
    else{aid=null;pieces=[];ctx.clearRect(0,0,w,h);}
  }

  // 绑定点击
  document.getElementById('badgeClick').addEventListener('click',function(e){
    const r=this.getBoundingClientRect();
    burst(r.left+r.width/2,r.top+r.height/2);
  });

  window.addEventListener('resize',()=>{w=canvas.width=window.innerWidth;h=canvas.height=window.innerHeight;});
})();
```

---

## 4. 打字机效果

### 逐字
```css
.char{opacity:0;transform:translateY(40px) rotateX(-20deg);transition:all 0.6s cubic-bezier(0.34,1.56,0.64,1);}
.char.show{opacity:1;transform:translateY(0) rotateX(0);}
```
```javascript
const name='郭泽莹';
const el=document.getElementById('name');
name.split('').forEach((ch,i)=>{
  const span=document.createElement('span');span.textContent=ch;
  span.className='char';el.appendChild(span);
  setTimeout(()=>span.classList.add('show'),i*200);
});
```

### 逐行
```css
.line{opacity:0;transform:translateY(8px);transition:all 0.6s ease;}
.line.show{opacity:1;transform:translateY(0);}
```
```javascript
const lines=document.querySelectorAll('.message .line');
lines.forEach((l,i)=>setTimeout(()=>l.classList.add('show'),i*500+800));
```

---

## 5. 背景音乐（Web Audio API 简单旋律）

```javascript
(function(){
  const btn=document.getElementById('musicT');
  let playing=false,ac=null;
  btn.addEventListener('click',()=>{
    if(!playing){
      try{
        ac=new (window.AudioContext||window.webkitAudioContext)();
        const notes=[262,294,330,349,392,440,494,523];
        let idx=0;playing=true;btn.classList.add('playing');btn.textContent='♫';
        function playNote(){
          if(!playing||!ac)return;
          const o=ac.createOscillator(),g=ac.createGain();
          o.type='sine';o.frequency.value=notes[idx%notes.length];
          g.gain.setValueAtTime(0.035,ac.currentTime);
          g.gain.exponentialRampToValueAtTime(0.001,ac.currentTime+0.7);
          o.connect(g);g.connect(ac.destination);o.start();o.stop(ac.currentTime+0.7);
          idx++;setTimeout(playNote,550);
        }
        playNote();
      }catch(e){/* mobile safari may block */}
    }else{
      playing=false;if(ac){ac.close();ac=null;}
      btn.classList.remove('playing');btn.textContent='♪';
    }
  });
})();
```

---

## 6. 浮动气球

```javascript
(function(){
  const emojis=['🎈','🎈','🎈','🎈'];
  for(let i=0;i<5;i++){
    const b=document.createElement('div');b.className='balloon';
    b.textContent=emojis[i%emojis.length];
    b.style.left=(8+Math.random()*80)+'%';
    b.style.top=(8+Math.random()*75)+'%';
    b.style.animationDuration=(3+Math.random()*2)+'s';
    b.style.animationDelay=-Math.random()*3+'s';
    b.style.fontSize=(1.5+Math.random()*1)+'rem';
    b.addEventListener('click',function(){
      this.classList.add('popped');
      setTimeout(()=>{if(this.parentNode)this.parentNode.removeChild(this);},400);
    });
    document.body.appendChild(b);
  }
})();
```
```css
.balloon{position:fixed;z-index:3;cursor:pointer;user-select:none;
  animation:balFloat linear infinite;transition:all 0.2s ease;}
.balloon:active{transform:scale(1.5);opacity:0;}
.balloon.popped{transform:scale(2)!important;opacity:0!important;transition:all 0.3s ease;pointer-events:none;}
@keyframes balFloat{0%{transform:translateY(0)rotate(-1deg);}50%{transform:translateY(-18px)rotate(1deg);}100%{transform:translateY(0)rotate(-1deg);}}
```

---

## 7. 凹凸星（多边形旋转）

```css
.aotu-star{
  width:34px;height:34px;
  clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);
  animation:starSpin 3s ease-in-out infinite;
  filter:drop-shadow(0 0 6px rgba(251,191,36,0.2));
}
.aotu-star:nth-child(1){background:linear-gradient(135deg,#fbbf24,#f59e0b);}
.aotu-star:nth-child(2){background:linear-gradient(135deg,#a78bfa,#7c3aed);animation-delay:-0.6s;}
.aotu-star:nth-child(3){background:linear-gradient(135deg,#f472b6,#ec4899);animation-delay:-1.2s;}
.aotu-star:nth-child(4){background:linear-gradient(135deg,#67e8f9,#06b6d4);animation-delay:-1.8s;}
@keyframes starSpin{0%,100%{transform:rotate(0deg)scale(1);}50%{transform:rotate(180deg)scale(1.1);}}
```

---

## 8. 多阶段叙事入场

```css
.stage{position:fixed;inset:0;z-index:3;display:flex;align-items:center;justify-content:center;
  transition:opacity 1s ease,transform 1s ease;}
#stage1{/* 背景辐射渐变 */}
#stage2{opacity:0;transform:translateY(40px);pointer-events:none;}
#stage2.show{opacity:1;transform:translateY(0);pointer-events:auto;}
#stage3{opacity:0;transform:translateY(30px);pointer-events:none;z-index:4;flex-direction:column;}
#stage3.show{opacity:1;transform:translateY(0);}
```

```javascript
// 阶段1: 名字逐字
const name='郭泽莹';
const nameEl=document.getElementById('nameReveal');
name.split('').forEach((ch,i)=>{
  const span=document.createElement('span');span.textContent=ch;
  span.className='char';nameEl.appendChild(span);
  setTimeout(()=>span.classList.add('show'),i*200);
});

// 阶段2: subline (名字完+1.2s)
setTimeout(()=>{document.getElementById('subLine').classList.add('show');},name.length*200+1200);

// 阶段3: 切到stage2 (名字完+2.8s)
setTimeout(()=>{
  document.getElementById('stage1').style.opacity='0';
  setTimeout(()=>{
    document.getElementById('stage1').style.display='none';
    document.getElementById('stage2').classList.add('show');
  },1000);
},name.length*200+2800);

// 阶段4: 祝福语逐行 (名字完+5s)
setTimeout(()=>{
  document.getElementById('stage3').classList.add('show');
  document.querySelectorAll('.msg-text .line').forEach((l,i)=>{
    setTimeout(()=>l.classList.add('show'),i*600+300);
  });
},name.length*200+5000);
```

---

## 9. 礼物盒弹窗

```html
<div class="gift-area" id="giftBtn">
  <div class="gift-box">🎁</div>
</div>
<div class="gift-overlay" id="giftOver">
  <button class="g-close" id="gClose">✕</button>
  <div class="gift-card">
    <h2>标题</h2>
    <div class="gt">内容...</div>
  </div>
</div>
```

```css
.gift-area{position:fixed;bottom:2.5rem;right:2rem;z-index:10;cursor:pointer;}
.gift-overlay{position:fixed;inset:0;z-index:20;
  background:rgba(0,0,0,0.55);backdrop-filter:blur(10px);
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:all 0.5s ease;}
.gift-overlay.show{opacity:1;pointer-events:auto;}
.gift-card{transform:scale(0.85);transition:transform 0.5s cubic-bezier(0.34,1.56,0.64,1);}
.gift-overlay.show .gift-card{transform:scale(1);}
```

```javascript
document.getElementById('giftBtn').addEventListener('click',()=>giftOver.classList.add('show'));
document.getElementById('gClose').addEventListener('click',()=>giftOver.classList.remove('show'));
giftOver.addEventListener('click',(e)=>{if(e.target===giftOver)giftOver.classList.remove('show');});
```

---

## 10. 轨道光环（吧唧徽章装饰）

```css
.b-ring3{position:absolute;inset:-42px;border-radius:50%;border:1px solid rgba(167,139,250,0.06);animation:bSpin 40s linear infinite;}
.b-ring2{position:absolute;inset:-28px;border-radius:50%;border:1px dashed rgba(236,72,153,0.08);animation:bSpin 30s linear infinite reverse;}
.b-ring{position:absolute;inset:-16px;border-radius:50%;border:2px solid rgba(251,191,36,0.08);animation:bSpin 18s linear infinite;}
@keyframes bSpin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
```

卫星粒子:
```css
.b-orbits{position:absolute;inset:-52px;border-radius:50%;}
.b-orbits span{
  position:absolute;top:50%;left:50%;width:5px;height:5px;border-radius:50%;
  animation:orbF 6s linear infinite;
}
.b-orbits span:nth-child(1){background:#fbbf24;--r:48px;--deg:0deg;}
/* nth-child(2-5): 不同deg和颜色, animation-delay: -1.2s递增 */
@keyframes orbF{0%{transform:rotate(var(--deg))translateX(var(--r));opacity:1;}
  50%{opacity:0.2;}100%{transform:rotate(calc(var(--deg)+360deg))translateX(var(--r));opacity:1;}}
```

---

## 11. 暗色科幻主题（个人简历/品牌站配色）

```css
/* Hero */
.hero-avatar{
  background:linear-gradient(135deg,#6366f1,#a78bfa,#f472b6);
  box-shadow:0 0 60px rgba(99,102,241,0.3);
}
/* 按钮 */
.hero-cta .primary{background:linear-gradient(135deg,#6366f1,#818cf8);box-shadow:0 0 30px rgba(99,102,241,0.25);}
.hero-cta .secondary{border:1px solid rgba(99,102,241,0.3);background:rgba(99,102,241,0.05);backdrop-filter:blur(12px);}
/* 卡片 */
.agent-card{background:rgba(30,41,59,0.3);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border:1px solid rgba(99,102,241,0.06);border-radius:16px;}
.agent-card:hover{border-color:rgba(99,102,241,0.15);box-shadow:0 20px 40px rgba(0,0,0,0.3);}
/* 时间线 */
.timeline::before{background:linear-gradient(180deg,#6366f1,#a78bfa,transparent);}
.tl-item::before{background:#6366f1;box-shadow:0 0 15px rgba(99,102,241,0.5);}
/* 渐变文本 */
.gradient-text{background:linear-gradient(135deg,#e2e8f0,#818cf8,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
```

---

## 12. 动漫头像SVG滤镜

当用户只有真人照片且希望近似动漫化时使用（真正的动漫化建议即梦AI生成）：

```html
<svg style="position:fixed;width:0;height:0;" aria-hidden="true">
  <filter id="anime">
    <feComponentTransfer in="SourceGraphic" result="poster">
      <feFuncR type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
      <feFuncG type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
      <feFuncB type="discrete" tableValues="0 0.15 0.3 0.5 0.7 0.85 1"/>
    </feComponentTransfer>
    <feConvolveMatrix order="3" kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1" preserveAlpha="true" in="SourceGraphic" result="edge"/>
    <feColorMatrix in="edge" type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 6 0" result="edgeGlow"/>
    <feBlend in="poster" in2="edgeGlow" mode="multiply"/>
  </filter>
</svg>
```
```css
.avatar img{filter:url(#anime);}
```
