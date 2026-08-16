---
name: ux-pro-max
description: 前端视觉设计蒸馏规则集 — 配色/间距/阴影/质感/动效/设计流程 + 组件模式库/沉浸式页面/数据看板/灵感参考。
---

# UX Pro Max — 视觉设计速查

> 蒸馏自160+行业规则，只留对「好看」有用的部分。
> 当我生成前端页面（landing/后台/小程序H5）时，自动套这套规范。

## 一、配色体系

```
主色:      #6366F1  (indigo-500)  — 按钮/链接/品牌色
主色悬停:   #4F46E5  (indigo-600)
主色浅底:   #EEF2FF  (indigo-50)  — 背景card/badge
强调色:    #F59E0B  (amber-500)  — CTA/提示/价格
强调悬停:   #D97706  (amber-600)
成功:      #10B981  (emerald-500)
错误:      #EF4444  (red-500)
背景:      #F8FAFC  (slate-50)
背景浅:    #FFFFFF  (white)
背景深:    #0F172A  (slate-900)  — dark mode用
正文:      #1E293B  (slate-800)
次级文字:   #64748B  (slate-500)
占位文字:   #94A3B8  (slate-400)
边框:      #E2E8F0  (slate-200)
分割线:    #F1F5F9  (slate-100)
```

**规则：** 一页不要超过3种主色。品牌色indigo+强调amber+状态色。灰阶用slate。

### 1a. 财务/金融页颜色特例（中国标准）

中国股市/金融页面的涨跌颜色与国际标准相反：

```
涨(up):   #ef4444 (red-500)   — 中国红色代表上涨
跌(down): #22c55e (green-500) — 绿色代表下跌
```

创建任何含涨跌数据的页面（K线、持仓、股票列表）时，**必须**用红涨绿跌，CSS变量名保持`--rise`/`--fall`但值互换。同时注意：
- K线蜡烛：阳线（收盘≥开盘）用红色填充，阴线用绿色
- 涨跌幅数字：正数红色，负数绿色
- 热力图板块：涨幅用红色色阶，跌幅用绿色色阶
- 背景高亮行：涨用rgba(239,68,68,0.10)，跌用rgba(34,197,94,0.10)
- 这个细节容易忽略，检查Canvas绘制的热力图和sidebar列表的背景色

## 二、间距系统（8px基准）

```
间距尺:   4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96
内边距:
  - 卡片: 16-24px
  - 容器: 24-48px（移动端收窄）
  - 按钮: 12-24px 水平，8-16px 垂直
外边距:
  - 区块间距: 48-64px
  - 组件间距: 16-24px
  - 文字间距: 8-12px
```

**规则：** 间距始终偶数，不用3/5/7这种奇数。卡片不要紧贴屏幕边。

## 三、字号阶梯

```
尺寸 | px  | 使用场景
-----|------|---------
xs   | 12  | 辅助文字/脚注
sm   | 14  | 正文/描述
base | 16  | 默认正文
lg   | 18  | 正文强调
xl   | 20  | 小标题
2xl  | 24  | 区块标题
3xl  | 30  | 大标题/首屏
4xl  | 36  | Hero标题（移动端少用）
5xl  | 48  | Hero标题（桌面）

行高: 1.5（正文）/ 1.25（标题）
字重: 400（正文）/ 500（标题）/ 600（CTA按钮）/ 700（大标题）
```

**规则：** 一页不超过4档字号。不猜字重，用上面固定值。

## 四、圆角体系

```
none:  0px    — 图片/背景/容器角
sm:    4px    — 标签/小徽章
md:    6px    — 按钮/输入框/小卡片
lg:    8px    — 普通卡片/弹窗
xl:    12px   — 大卡片/模块容器
2xl:   16px   — 首页Banner/大模块
full:  9999px — 圆形头像/胶囊按钮
```

**规则：** 圆角不混用两级以上（比如卡片12px就不要搞6px按钮）。

## 五、阴影层级

```
sm:     0 1px 2px  rgba(0,0,0,0.05)
md:     0 1px 3px  rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)
lg:     0 4px 6px  rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)
xl:     0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)
2xl:    0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04)
card:   0 1px 3px  rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)
hover:  0 10px 25px rgba(99,102,241,0.10), 0 4px 10px rgba(0,0,0,0.05)
```

**规则：** 卡片默认用sm或card级，hover时提到md-hover级。不要用xl以上，除非弹窗/下拉。

## 六、卡片质感

```
背景:     #FFFFFF 或 #F8FAFC
圆角:     8-12px
边框:     1px solid #E2E8F0（淡）
阴影:     card级
内边距:   16-24px
标题字体: 16-18px, weight 500
正文行高: 1.5
过渡:     all 0.2s ease（悬停效果）
```

### 6a. 深色版卡片高级质感

深色页面的卡片用半透明rgba+玻璃拟态：

```css
.card {
  background:rgba(255,255,255,0.02);
  border:1px solid rgba(255,255,255,0.05);
  position:relative; overflow:hidden;
  transition:all 0.3s cubic-bezier(0.2,0,0,1);
}
/* 左侧光条悬停发光 */
.card::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:2px;
  background:var(--accent);
  box-shadow:0 0 8px var(--accent), 0 0 20px color-mix(in srgb,var(--accent) 50%,transparent);
  opacity:0.3; transition:opacity 0.4s;
}
.card:hover::before{opacity:0.9}
.card:hover{
  border-color:color-mix(in srgb,var(--accent) 40%,rgba(255,255,255,0.08));
  transform:translateY(-2px);
  box-shadow:0 8px 32px color-mix(in srgb,var(--accent) 10%,transparent);
}
```

### 6b. 玻璃拟态

```css
.card {
  background:rgba(255,255,255,0.03);
  backdrop-filter:blur(12px);
  border:1px solid rgba(255,255,255,0.06);
  border-radius:12px;
}
```

## 七、动效/过渡

```
悬停:     all 0.2s ease
入场:     opacity 0→1 + translateY(8px→0), 0.3s ease
切换:     opacity 0→1, 0.2s ease
加载骨架:  shimmer 1.5s infinite linear
按钮点击:  scale(0.97) 瞬效
```

### 7a. 入场序列动画（卡片依次弹出）

```css
@keyframes fadeIn{
  0%{opacity:0;transform:translateY(16px)scale(0.98);filter:blur(4px)}
  100%{opacity:1;transform:translateY(0)scale(1);filter:blur(0)}
}
.card-grid .card{animation:fadeIn 0.5s ease backwards}
.card-grid .card:nth-child(1){animation-delay:0.02s}
.card-grid .card:nth-child(2){animation-delay:0.06s}
.card-grid .card:nth-child(3){animation-delay:0.10s}
.card-grid .card:nth-child(4){animation-delay:0.14s}
.card-grid .card:nth-child(5){animation-delay:0.18s}
.card-grid .card:nth-child(6){animation-delay:0.22s}
.card-grid .card:nth-child(7){animation-delay:0.26s}
.card-grid .card:nth-child(8){animation-delay:0.30s}
```

### 7b. 动态渐变标题

```css
.title {
  background:linear-gradient(135deg,#c4b5fd,#8b5cf6,#6366f1,#06b6d4);
  background-size:200% 200%;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:gradientShift 4s ease infinite;
}
@keyframes gradientShift{
  0%,100%{background-position:0% 50%}
  50%{background-position:100% 50%}
}
```

### 7c. 脉冲状态灯

```css
.status-dot{
  width:8px;height:8px;border-radius:50%;
  background:#34d399;
  box-shadow:0 0 6px #34d399,0 0 12px color-mix(in srgb,#34d399 40%,transparent);
  animation:pulse 2s ease-in-out infinite;
}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
```

## 八、布局栅格

```
容器宽:
  - 全文: max 1200px
  - 窄文: max 720px
栅格: 12栏，gap 24px
断点:
  - sm: 640px
  - md: 768px
  - lg: 1024px
  - xl: 1280px
移动端: 单栏流，pad边距16-24px
```

## 九、UI组件速查

```
按钮:
  - 主按钮: 主色背景, 白色文字, 6px圆角, 12-24px水平内边距, 14-16px
  - 次按钮: 白色背景, 主色边框1px, 主色文字
  - 文字按钮: 无背景, 主色文字
  - 高度: 36-48px
输入框:
  - 高度: 40-48px
  - 边框: 1px solid #E2E8F0, 焦点时主色border
  - 圆角: 6px
  - 内边距: 12px 16px
标签:
  - sm: 4px 8px, 12px
  - 背景: indigo-50, 文字: indigo-600
卡片列表:
  - gap: 24px
```

## 十、动态Canvas背景库

6种可复用Canvas动画背景模式：

### 10a. 星空粒子

80个粒子+120px连线，适合科幻背景。

### 10b. 极光光晕

3层径向渐变缓慢漂移，适用导航页/品牌页。

### 10c. 矩阵代码雨

黑客帝国风格绿色字符下坠。

### 10d. CRT雪花噪点

适合复古像素/Vaporwave风格。

### 10e. 烟雾粒子

神秘玄学风格，粒子从底部升起扩散消散。

### 10f. 泡泡粒子

可爱卡通风格，彩色泡泡升起破裂。

### 10g. 网络节点浮动

科技/神经网络风格，45个大节点+200px连线+外发光+白色核心亮点：

```js
const N=45,nodes=[];
for(let i=0;i<N;i++)nodes.push({x:Math.random()*c.width,y:Math.random()*c.height,
  vx:(Math.random()-0.5)*0.6,vy:(Math.random()-0.5)*0.6,r:Math.random()*2.5+1.5});
let t=0;
function draw(){
  ctx.clearRect(0,0,c.width,c.height);
  for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
    const d=Math.hypot(nodes[i].x-nodes[j].x,nodes[i].y-nodes[j].y);
    if(d<200){ctx.beginPath();ctx.moveTo(nodes[i].x,nodes[i].y);ctx.lineTo(nodes[j].x,nodes[j].y);
      ctx.strokeStyle='rgba(96,165,250,'+((1-d/200)*0.15+0.05)+')';ctx.lineWidth=0.8;ctx.stroke();}
  }
  for(const n of nodes){
    n.x+=n.vx;n.y+=n.vy;if(n.x<0||n.x>c.width)n.vx*=-1;if(n.y<0||n.y>c.height)n.vy*=-1;
    const g=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,n.r*4);
    g.addColorStop(0,'rgba(96,165,250,0.15)');g.addColorStop(1,'rgba(96,165,250,0)');
    ctx.fillStyle=g;ctx.beginPath();ctx.arc(n.x,n.y,n.r*4,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,Math.PI*2);
    ctx.fillStyle='rgba(96,165,250,'+(0.5+Math.sin(t+n.x*0.02)*0.2)+')';ctx.fill();
    ctx.beginPath();ctx.arc(n.x,n.y,n.r*0.4,0,Math.PI*2);
    ctx.fillStyle='rgba(200,220,255,0.6)';ctx.fill();
  }
  t+=0.015;requestAnimationFrame(draw);
} draw();
```

配套CSS网格：
```css
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;background:#060a18;
  background-image:linear-gradient(rgba(96,165,250,0.08)1px,transparent 1px),
    linear-gradient(90deg,rgba(96,165,250,0.08)1px,transparent 1px);background-size:50px 50px}
.bg::after{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 50% 40% at 25% 30%,rgba(96,165,250,0.12),transparent 70%),
    radial-gradient(ellipse 40% 40% at 75% 70%,rgba(167,139,250,0.08),transparent 70%)}
```

**关键要点：** 45节点，2.5+1.5半径，200px连线距离，0.8px线宽，外发光光晕，白色核心亮点。比星空粒子更大更亮更明显。

## 十一、背景三层叠加法

炫酷深色页面的核心是**三层叠加**：

1. CSS网格底纹 — `background-image: linear-gradient(...)`
2. CSS渐变光晕 — `radial-gradient` 或极光Canvas
3. Canvas粒子/节点动效

## 十二、如何复刻参考网站设计

当用户提供参考URL要求「做成这样」时：

### Step 1: 直接获取源码（最快最准）

如果URL可以访问，用浏览器打开后：
1. 查看页面源代码（view-source:URL 或 F12开发者工具）
2. 提取 `<link rel="stylesheet">` 中的CSS文件URL
3. 提取关键CSS变量、配色色值、字体栈、圆角值、间距值
4. 把提取到的值直接套用，不要凭感觉调

### Step 2: 下载模板文件

如果网站提供免费下载（如17sucai），告知用户下载后发源文件给我，我直接改内容。

### Step 3: 截图兜底方案

网站不可访问时：
1. 用 `browser_vision` 详细询问每个CSS属性（色值、字号、圆角、间距、边框）
2. 先出布局骨架让用户确认，再完善细节
3. 不要一次性出整版

### 深色背景可见度

用户多次强调「背景太浅」——深色科技风的网格/粒子要**明显可见**：
- 网格线透明度至少 **0.08**（不要0.03）
- 粒子半径至少 **1.5-4.0**（不要0.5-1.8）
- 连线至少 **0.8px** 粗
- 用 `browser_vision` 确认"够不够明显"

## 十三、技术坑

### Python f-string 写JS模板字面量

```py
# 错误：Python会把${i}当成f-string变量
html = f'<script>grad.addColorStop(0,`rgba(${c[i]},0.04)`);</script>'
# → NameError: name 'i' is not defined

# 正确：用字符串拼接代替
html = f'<script>grad.addColorStop(0,"rgba("+c[i]+",0.04)");</script>'
```

## 选型速查

| 风格 | 背景模式 | 主色调 | 动态Canvas | 适用场景 |
|------|---------|--------|-----------|---------|
| 科幻/导航 | 网格+极光+粒子 | 紫+青 | 粒子+极光 | 导航Hub、品牌页 |
| 赛博朋克 | 网格+扫描线+HUD | 青+粉 | 网格扫描线 | 数据大屏、选品 |
| 黑客帝国 | 代码雨+扫描线 | 矩阵绿 | 代码雨(10c) | 终端、技术页 |
| 神秘玄学 | 烟雾粒子+烛光 | 暗红+金 | 烟雾(10e) | 占卜、运势 |
| 卡通可爱 | 泡泡粒子+彩虹 | 彩虹HSL | 泡泡(10f) | 儿童、游戏 |
| 华尔街金融 | 数字流(金色) | 金+黑 | 自定义数字雨 | K线、交易 |
| 画廊/画展 | 暖色墙面纹理 | 米白+金 | 织物质感CSS | 像素展厅、作品集 |
| 科技工具 | 电路板网格 | 青+深蓝 | PCB网格路径 | 工具箱、后台 |

## 规则执行

当Yasin说「给我一个前端页面」时：
1. 有参考URL → 先提取源码CSS再复刻（12章）
2. 配色用indigo为主色（深色系用#05050a底+#a78bfa主）
3. 套8px基准间距、字号阶梯
4. 深色卡片用半透明+玻璃拟态
5. 深色页默认叠加星空粒子或极光背景
6. 按项目类型匹配风格（选型速查）
7. 卡片用入场序列动画，标题用渐变呼吸
8. 含涨跌数据必须用中国标准：红涨#ef4444绿跌#22c55e
9. Python生成HTML时用字符串拼接避免f-string冲突

## 交付强制闭环（v2 新增，必守）

任何页面生成后**必须**走自检闭环，禁止写完直接交付：

```
write_file → browser_navigate(file://或本地端口) → browser_vision(自检) → 不合格迭代 → 合格才交付
```

自检清单（browser_vision 逐项问）：
1. 背景是否明显（网格线≥0.08透明度、粒子≥1.5px、连线≥0.8px）
2. 配色是否≤3种主色、对比度够不够
3. 布局是否错位/溢出/空白过多
4. 动效是否生效（入场动画/悬停效果）
5. 整体是否有「炫酷感」还是像默认模板

不合格 → 拿到具体问题 → patch → 重新截图，最多3轮，3轮后仍未达标要如实告诉Yasin当前状态而不是硬交付。

## 风格指纹沉淀（v2 新增）

每个成功定稿的页面，把设计系统蒸馏成「风格指纹」追加到本技能的组件模式库（`references/visual-component-patterns.md`）：
- 色值（背景/主色/强调/文字）
- 字体栈
- 关键间距/圆角值
- 动效参数（时长/缓动）
- 一句话风格描述 + 适用场景

下次做同风格页面直接引用指纹，不重新发明。

## 组件模式库（合并自 visual-component-patterns）

可复用视觉组件（流动星光/徽章光环/玻璃卡片/彩花粒子/打字机/CRT复古/玄学古风/电路板/3D环形展厅/AI立绘贴纸等），完整组件清单与实现要点见 `references/visual-component-patterns.md`：
- 组件索引表 + 适用场景：见该文件头部「组件清单」
- 玄学/古风四件套（烟雾粒子+卷轴卡片+印章按钮+烛光火焰）：`references/mystical-components.md`
- 3D环形展厅（perspective + preserve-3d + 拖拽旋转）：`references/3d-ring-gallery.md`
- 电路板背景动画（Canvas PCB走线+脉冲节点）：`references/circuit-board-canvas.md`

## 沉浸式HTML页面模式（合并自 immersive-html-experiences）

庆典/全屏/沉浸式页面（生日页、庆祝页、作品展厅）的完整设计模式见 `references/immersive-html-experiences.md`，要点：
- 触发：炫酷页面/全屏展示/沉浸效果/科幻/赛博朋克/复古像素/占卜玄学/极简名片
- 深色庆典配色（紫粉金 #a78bfa/#f472b6/#fbbf24）、星空粒子、吧唧系统、彩花物理引擎、头像动漫化、打字机效果
- 庆祝页禁忌：不要用本技能 indigo 主色（庆祝页用紫粉金）、不要分阶段屏幕切换、音乐用 Web Audio 振荡器不引 MP3
- 用户迭代四轮节奏（平淡→加交互→改全屏→退回布局）与「先调研再动手」硬规则
- 子文件：`references/immersive-style-matrix.md`（风格矩阵选型）、`references/immersive-starfield-canvas.md`（星空粒子）、`references/immersive-interactive-effects.md`（交互代码全集）、`references/immersive-canvas-particle-starfield.md`、`references/immersive-birthday-celebration-patterns.md`、`references/immersive-anime-avatar-pipeline.md`（头像动漫化两段式）、`references/immersive-data-bridge-pattern.md`（data.json 动态数据桥接）、`references/immersive-manim-video-integration.md`（Manim 视频嵌入）、`references/immersive-preview-workflow.md`（预览工作流）、`references/immersive-3d-ring-gallery.md`（3D 环形画廊实现）
- 批量部署多个 HTML 项目用 delegate_task 并行（最多3个一批，端口规划见 `references/immersive-preview-workflow.md`）

## 数据看板模式（合并自 data-dashboard）

单文件 HTML 数据看板（大屏/监控/分析页）见 `references/data-dashboard.md`，要点：
- Monitor 表面布局：顶部统计行 + 数据表 + 图表列 + 热力图，无 hero、无功能卡网格
- 科幻深色主题 token（bg #0a0e1a / 主色 #00d4ff / 金字 #ffd700）
- Canvas 环形图、CSS 条形/柱状图、热力图、动画计数器、可排序表格
- 数据同步模式：cron 采集脚本 → data.json → fetch 渲染（`references/douyin-worked-example.md` 完整案例）
- A股看板铁律：红涨 #ef4444 / 绿跌 #22c55e（中国标准，与西方相反）
- 坑：Canvas DPR 缩放、零值条 min-height:4px、表格溢出滚动、确定性 mock 数据

## 灵感参考流程（合并自 design-inspiration）

用户说「想做个炫酷网站/落地页」但没定风格时，**先展示参考再动手**：
1. 确认商业目的还是纯玩
2. 从 `references/stunning-landing-pages.md` 加载案例库，推荐 3-5 个（含精华/技术栈/Demo 链接）
3. 用户选定后转交执行（单页→sketch/claude-design；3D叙事→Three.js+GSAP；AI产品风格→Brainwave 源码）
4. 陷阱：别在灵感阶段推技术方案；「炫酷」不一定是 3D；别把纯玩往商业变现扯

### 红蓝品牌双色（Yasin个人主页 / 红蓝分析法IP 专用）

红蓝分析法是 Yasin 的 IP 方法论，品牌视觉语言 = 红蓝双色对立：
- **蓝 = 提案 / 理性 / 信任**（#3b82f6，浅 #93c5fd，底 rgba(59,130,246,.12)）
- **红 = 攻击 / 质疑 / 风险预警**（#ef4444，浅 #fca5a5，底 rgba(239,68,68,.12)）
- 背景 #05060a 深黑蓝 + 网格线(blue 5%) + 红蓝双色粒子Canvas（一半红一半蓝，130px连线）

**语义约定：** 页面里任何「正面/提案/推荐」用蓝，任何「攻击/质疑/风险/案例数据」用红。Hero 标题可做红蓝渐变（蓝→红），方法论流程条红蓝交替。案例卡 metric 数字红蓝随卡色。

**已落地：** 个人主页 ~/Desktop/hermes/portfolio/index.html（8894端口，Yasin 博主品牌页）。结构：Hero巨型渐变YASIN+短标语 → 方法论双卡(红蓝分析法/六分身) → 案例墙带metric → 数据背书4格 → 关于我成长线 → 联系CTA。完整指纹见 `references/yasin-personal-homepage.md`。

**Hero 首屏铁律（Yasin 2026-07 定稿纠正，必守）：**
- 首屏 = 巨型英文名 + 短标语 + 1个CTA区，**不要**塞副文案/meta标签/流程条——第一版塞满被否：「不够简约高端大气，废话太多，没有中英字体排版的大气感」
- 英文名不加装饰性标点（红点句号被否「不协调」）；名字本体用红蓝渐变字
- 标语要短、有观点：「决策，不靠感觉」（7字）✅；「帮创业者少踩坑的实战派」（11字长描述）❌
- 中英排版质感 = 粗重英文(weight 800) × 纤细中文(weight 300，letter-spacing .4em) 强对比
- 按钮文案砍到最少字：「方法论」「案例」（2字），不要箭头/动词前缀
- 顶部/底部用一行 mono 小字英文点缀层级（`E-COMMERCE × AI AGENT · EST. 2008` / `GUO YUEXING · 18 YEARS · SCUT CS`）

## 设计流程（合并自 frontend-design）

构建新 UI 或改造现有界面时，先走流程再套规范：

### 设计原则

1. **主题先行** — 用主题本身的世界观、材料、工具、文化语言驱动设计选择
2. **排版即个性** — 展示字体和正文字体刻意搭配，不用默认组合
3. **结构即信息** — 用编号、分割线、标签等结构元素编码真实信息，不只是装饰
4. **动效应服务内容** — 每次动效都要有目的
5. **复杂度要匹配** — 极简设计需要精确的间距/字体/细节；繁复设计需要完整执行

### 三轮流程

- **第一轮 头脑风暴**：创建紧凑设计标记系统——4-6 个命名色值调色板 + 2+ 个角色字体（展示/正文/工具）+ 一个布局概念（一句话+ASCII 线框）+ 一个签名元素。
- **第二轮 自我审查**：写代码前检查「换一个完全不相关的主题这个设计还成立吗？」成立 → 重做。
- **第三轮 构建+再审查**：写完截图自审，找出至少一个问题再宣布完成。

### 常用配色参考（非 indigo 场景）

| 主题 | 主色 | 辅助色 | 强调色 |
|------|------|--------|--------|
| 深海商务 | #1E2761 | #CADCFC | #FFFFFF |
| 森林绿 | #2C5F2D | #97BC62 | #F5F5F5 |
| 珊瑚活力 | #F96167 | #F9E795 | #2F3C7E |
| 暖陶土 | #B85042 | #E7E8D1 | #A7BEAE |
| 炭灰极简 | #36454F | #F2F2F2 | #212121 |

### 个人主页/个人品牌页（先定定位再动手）

| 类型 | 核心目的 | 页面重点 |
|------|---------|---------|
| 求职/作品集 | 证明能力 | 作品案例 > 自我介绍 |
| 个人品牌/博主 | 建立信任、导流 | 方法论、内容、联系方式 |
| 工具/产品官网 | 转化付费 | 产品演示、价格、CTA |
| 纯个人名片 | 让别人找到你 | 一句话+头像+链接 |

通用骨架：Hero区（3秒抓人：一句话定位+身份标签+主CTA）→ 信任区（数据/高光履历/Logo墙）→ 作品/方法论区（3-6个精选案例，图大字少）→ 关于我（3-5行，有人格不油腻）→ 收尾CTA。
简历→主页转化：保留全部真实素材（业绩/项目/学历），叙事从「求职证明」改「品牌展示价值」，删掉期望薪资/性别年龄标签。
Hero 区排版细节见上文「Hero 首屏铁律」。

### 避免的 AI 默认设计

- ❌ 暖白背景(#F4F1EA)+衬线字体+陶土色强调
- ❌ 纯黑背景+荧光绿/朱红强调
- ❌ 报纸式布局+细分割线+零圆角+密集列
