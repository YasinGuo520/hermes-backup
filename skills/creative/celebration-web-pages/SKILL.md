---
name: celebration-web-pages
description: 生日/庆祝/节日交互式网页全流程制作 — 多阶段叙事入场、粒子系统、彩花爆炸、打字机效果、音效、浮动装饰
---

# Celebration Web Pages — 庆祝交互页

> 当用户说「给我做一个生日/庆祝页面」，或需要氛围感、互动性强的单页体验时使用。
> 配套视觉规范见 `ux-pro-max` 技能的主题变体B（生日/庆祝主题）。

---

## 触发条件

- 用户要求「生日页面」「庆祝」「惊喜页面」「节日氛围」
- 用户需要氛围感强、有交互、多阶段的单页体验
- 特别针对 13 岁左右青少年、女性、卡通梦幻偏好

---

## 工作流

### 第1步：收集需求（必须问）

| 问题 | 影响设计 |
|------|---------|
| 给谁？名字？ | 确定视觉焦点文字 |
| 几岁？ | 决定设计风格（7-12卡通/13-16梦幻/17+优雅） |
| 喜欢什么？ | 主题元素（动画角色/颜色/装饰风格） |
| 性格？ | 影响语气和动效风格（活泼/安静/大大咧咧） |

### 第2步：选视觉主题（参考 ux-pro-max 主题变体B）

- **深空底 + 紫粉金渐变**：通用梦幻
- **粉蓝白底 + 明亮**：小公主风
- **白紫渐变 + 玻璃卡片**：现代简约

### 第3步：搭建交互层

按优先级添加：

1. **星点粒子背景** — 基础氛围感（必加）
2. **主视觉徽章/头像** — 圆形，轨道光环环绕（必加）
3. **多阶段入场** — 名字逐字→视觉弹出→祝福语打字机（推荐）
4. **彩花爆炸** — 点击触发，150+物理粒子（推荐）
5. **浮动装饰** — 气球（可点击爆炸）/ 晶体旋转 / 星星旋转（按需）
6. **礼物盒/隐藏彩蛋** — 点击弹出overlay卡片（按需）
7. **背景音乐** — Web Audio API 简单旋律（按需）
8. **即时AI头像** — 有照片时用SVG滤镜做近似动漫化（用户有AI图最好）

### 第4步：Yasin的迭代模式（关键）

Yasin对视觉设计会多次提意见，迭代节奏：

| 轮次 | 典型反馈 | 应对 |
|------|---------|------|
| 1 | 太平淡/太简单 | 加交互+特效+动画 |
| 2 | 不够大气 | 改全屏沉浸+深色+粒子背景 |
| 3 | 布局不对 | 退回到上一版布局风格重做 |
| 4 | 图片不对 | 用户自己出图后替换 |

**教训：** 不要一开始就往炫酷方向做满。先做干净的版本，等他提需求再加。他更喜欢**告诉你哪里不够好→你改→再反馈**的迭代节奏。

---

## 技术实现速查

具体代码实现见 `references/interactive-effects.md`（在 `ux-pro-max` skill目录下，被保护无法直接写入时，在本次技能内联即可）。

### 页面结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🎂 名字 · 生日快乐</title>
  <style>
    /* 深空背景 + 渐变ambient + 玻璃卡片 + 响应式 */
  </style>
</head>
<body>
  <!-- 粒子画布 canvas#starfield -->
  <!-- 环境光 div.ambient -->
  <!-- 彩花画布 canvas#confetti-c -->

  <!-- 阶段1: 名字逐字 -->
  <!-- 阶段2: 徽章+轨道光环 -->
  <!-- 阶段3: 祝福语+蛋糕 -->

  <!-- 礼物盒 (右下角固定) -->
  <!-- 音乐按钮 (右上角固定) -->
  <!-- 浮动气球 (JS生成) -->

  <script>
    // 粒子系统
    // 打字机入场
    // 彩花点击
    // 礼物盒弹窗
    // 音乐
  </script>
</body>
</html>
```

### 核心代码片段（必须随时可用）

#### 星点粒子场（80-130粒子，带连线）

```javascript
const c=document.getElementById('starfield'),ctx=c.getContext('2d');
let w=c.width=window.innerWidth,h=c.height=window.innerHeight;
const stars=[],colors=['#a78bfa','#f472b6','#fbbf24','#67e8f9'];
for(let i=0;i<100;i++)stars.push({
  x:Math.random()*w,y:Math.random()*h,
  r:Math.random()*2+0.3,dx:(Math.random()-0.5)*0.2,dy:(Math.random()-0.5)*0.2,
  col:colors[i%4],o:Math.random()*0.6+0.2
});
function draw(){
  ctx.clearRect(0,0,w,h);
  for(const s of stars){/* draw + move + wrap */}
  for(let i=0;i<stars.length;i++)for(let j=i+1;j<stars.length;j++){/* draw line if dist<150 */}
  requestAnimationFrame(draw);
}
draw();
```

#### 名字逐字弹出

```javascript
const name='郭泽莹',el=document.getElementById('name');
name.split('').forEach((ch,i)=>{
  const span=document.createElement('span');
  span.textContent=ch;span.style.transitionDelay=(i*200)+'ms';
  span.className='char';el.appendChild(span);
});
// CSS: .char{opacity:0;transform:translateY(40px);transition:0.6s cubic-bezier(0.34,1.56,0.64,1)}
// JS trigger: setTimeout(()=>span.classList.add('show'),i*200)
```

#### 彩花爆炸（150粒子）

```javascript
// 核心参数: 150粒子, angle随机, speed 5-21, gravity 0.2-0.3, drag 0.97, life 180-300
// 触发: 点击徽章/按钮 → burst(clickX, clickY)
```

#### 气球（点击消失）

```javascript
// JS生成5个🎈, random位置+动画时长, click→classList.add('popped')→remove
```

#### 多阶段叙事时序

```javascript
// t=0: 名字逐字每200ms
// t=name_len*200+1200: subline显示
// t=name_len*200+2800: stage1消失+stage2出现
// t=name_len*200+5000: stage3出现+message逐行每600ms
```

---

## 常见陷阱

1. **Yasin会对头像动漫化要求很高。** SVG滤镜只能做近似，真正动漫化需要他用即梦AI/可灵/妙鸭生成后再替换。第一次迭代用他给的图即可，不要过度加工。
2. **布局争议时退回上一版。** 如果他说「没第二版好」，立即退回第二版的layout风格，不做第三轮新构图。
3. **不要一次性做满。** 第一版先出干净的基础版本，他提意见再加。他喜欢「你做了→我挑毛病→你改」的节奏。
4. **音乐用Web Audio API振荡器。** 不要引入MP3/外部音频依赖，纯浏览器生成简单旋律即可。
5. **所有页面文件存 ~/Desktop/hermes/[项目名]/。** 服务器用python3 http.server，端口从8898开始分配。
