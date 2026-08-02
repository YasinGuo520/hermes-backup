---
name: immersive-html-experiences
description: 沉浸式交互HTML页面设计模式 — 庆典页/全屏展示/粒子动效/互动装饰。纯原生HTML+CSS+JS，零依赖。
---

# Immersive HTML Experiences

当Yasin要求做「庆典/全屏/沉浸」类HTML页面时使用。包含深色系设计系统、粒子动画、交互元素、头像动漫化等完整模式。

## 触发条件

Yasin说：炫酷页面/全屏展示/沉浸效果/科幻风格/赛博朋克/黑客帝国/复古像素/占卜玄学/极简名片

也可以直接对具体项目指定风格，风格矩阵见 `references/style-matrix.md`

## 页面结构模板

```html
<canvas id="starfield"></canvas>     <!-- z0: 粒子背景 -->
<div class="ambient"></div>          <!-- z1: 环境光晕 -->
<div class="decorations"></div>      <!-- z1: 浮动装饰 -->
<section class="hero">               <!-- z2: 主内容 -->
  <!-- 吧唧/标题/祝福语 -->
</section>
<div class="interactives"></div>     <!-- z3: 互动元素 -->
<canvas id="confetti"></canvas>      <!-- z999: 彩花 -->
```

## 配色（深色庆典系）

| 角色 | 色值 | 用途 |
|------|------|------|
| 背景 | #0a0a12 / #0b0a14 | 深空底 |
| 主色 | #a78bfa (紫) | 吧唧光环/装饰 |
| 辅色 | #f472b6 (粉) | 点缀/渐变 |
| 强调 | #fbbf24 (金) | 年龄/星/按钮 |
| 科技 | #67e8f9 (青) | 凹凸水晶 |
| 正文 | #e2e8f0 | 主文字 |
| 次级 | #94a3b8 | 祝福语正文 |

## 核心技术切片

### 1. 星空粒子（流动拖尾）

详见 `references/starfield-canvas.md`

### 2. 吧唧（Badge）系统

- 圆形徽章 140-170px，三层旋转光环 + 卫星粒子
- 脉冲发光动画（box-shadow 三层扩展）
- 点击触发 150片 彩花粒子

### 3. 彩花粒子（Confetti）

- 物理引擎：gravity 0.2-0.3, drag 0.97, 旋转惯性
- 生命周期：180-300帧, 渐隐
- 颜色池：粉/紫/金/绿/红/青/白 10色

### 4. 头像动漫化（两段式）

**A. PIL 服务端处理：** `references/anime-avatar-pipeline.md`
**B. 浏览器 SVG CSS 滤镜：** 见SKILL.md配图

### 5. 互动元素

- 气球：浮动 + 点击爆炸
- 礼物盒：右下角浮动 + 点击弹出遮罩卡片
- 音乐：OscillatorNode 简单旋律循环

### 6. 打字机效果

CSS transition逐行显现，每行间隔500-600ms

## 用户偏好

- 全屏一页布局 > 多阶段切换
- 深色底+高饱和点缀 > 浅色温馨
- 每个元素要有交互反馈
- 先给全貌再逐步显现（打字机效果）
- **每个项目应有独特风格**，参考 `references/style-matrix.md` 选型

## 预览工作流

```bash
# 1. 创建项目目录和HTML文件
mkdir -p ~/Desktop/hermes/[项目名]
# 文件存 ~/Desktop/hermes/[项目名]/index.html

# 2. 分配端口（避免冲突，查已用端口）
# 老项目: 8894(简历) 8895(导航) 8899(生日) 8900(工具箱)
# 其他项目: 8910-8917(已分配) 再新项目从8920开始
# 服务类: 8000(服小助) 8001(中年人生) 8897(Hermes)

# 3. 启动HTTP服务器
python3 -m http.server [PORT] --bind 0.0.0.0  # 用terminal(background=true)

# 4. 验证+刷新
curl http://localhost:[PORT]/
browser_navigate(http://43.138.221.174:[PORT])
# 改代码后 kill + 重启 + ?t=N 清缓存

# 5. browser_vision 验证视觉
```

### 坑：端口冲突

旧进程没停掉就启动新服务器会报 `Address already in use`。必须先kill再启动：

```bash
# 检查端口占用
lsof -ti:[PORT]
# 杀掉旧进程
kill $(lsof -ti:[PORT]) 2>/dev/null; sleep 1
# 再启动新服务器（用background=true）
```

### 批量部署多个项目（并行子Agent）

当需要一次性创建/改造多个HTML项目（每个不同风格），用 delegate_task 分批并行：

1. **分批**：每次最多3个项目一批（delegate_task上限），按3-3-2分批
2. **每批指令模板**：给每个子Agent提供完全自包含的上下文：
   - 文件路径（到具体 index.html）
   - 风格要求（配色+动态背景类型+卡片样式）
   - 启动命令（精确的 cd + python3 -m http.server 命令）
   - 是创建新文件还是覆盖已有
3. **全部完成后再统一起服务**：子Agent启动的服务器可能因端口冲突失败，等全部完成后kill旧进程+统一重启
4. **端口规划**：一批内不要分配冲突端口

示例（3个项目并行）：
```python
delegate_task(tasks=[
  {goal: "创建XXX页面...", context: "文件保存到~/Desktop/hermes/proj-a/index.html\n完成后 terminal(background=true) 启动: cd ~/Desktop/hermes/proj-a && python3 -m http.server 8920 --bind 0.0.0.0"},
  {goal: "创建YYY页面...", context: "文件保存到~/Desktop/hermes/proj-b/index.html\n完成后 terminal(background=true) 启动: cd ~/Desktop/hermes/proj-b && python3 -m http.server 8921 --bind 0.0.0.0"},
  {goal: "创建ZZZ页面...", context: "文件保存到~/Desktop/hermes/proj-c/index.html\n完成后 terminal(background=true) 启动: cd ~/Desktop/hermes/proj-c && python3 -m http.server 8922 --bind 0.0.0.0"},
])
```

## 庆祝/生日页面专章（合并自 celebration-page-design / celebration-web-pages / creative-page-design / immersive-visual-effects）

### 需求收集（开工必问）
| 问题 | 影响设计 |
|------|---------|
| 给谁？名字？ | 确定视觉焦点文字 |
| 几岁？ | 决定设计风格（7-12卡通/13-16梦幻/17+优雅） |
| 喜欢什么？ | 主题元素（动画角色/颜色/装饰风格） |
| 性格？ | 影响语气和动效风格（活泼/安静/大大咧咧） |

### ⚠️ 先调研再动手（硬性规则，creative-page-design 沉淀）
不要直接写代码。先搜索 `best birthday website design inspiration` / `creative celebration page codepen` / `award winning personal website design`，提取 3-5 个核心设计模式再合成。调研来源：onepagelove.com (生日标签)、GitHub (birthday-bloom 等)、Awwwards 获奖页。Yasin 说「只有几个字」= 不满意停留在文字展示阶段。

### Yasin 的迭代模式（关键，四轮节奏）
| 轮次 | 典型反馈 | 应对 |
|------|---------|------|
| 1 | 太平淡/太简单 | 加交互+特效+动画 |
| 2 | 不够大气 | 改全屏沉浸+深色+粒子背景 |
| 3 | 布局不对 | 退回到上一版布局风格重做（「没第二版好」= 立即退回第二版 layout） |
| 4 | 图片不对 | 用户自己出图后替换 |

**教训**：不要一开始就往炫酷方向做满。先做干净的版本，等他提需求再加。参考案例：泽莹13岁生日页 v1 粉紫卡片居中→"不够大气"、v2 深空全屏+分阶段→"布局没有第二版好"、v3 深空全屏+打字机+交互→"这样就行"（`~/Desktop/hermes/birthday-zeying/index.html`，端口 8899）。

### 庆祝页禁忌
- ❌ 不要用 ux-pro-max 的 indigo 主色（庆祝页用紫粉金：#a78bfa / #f472b6 / #fbbf24 / #67e8f9）
- ❌ 不要分阶段切换/屏幕切换（用户偏好一切同时可见）——注意与「多阶段叙事入场」的区别：入场有节奏，但最终所有内容同屏可见
- ❌ 不要只放文字没有交互；❌ 不要居中白色小卡片
- ❌ 头像不要用真人照片直接放；SVG/PIL 滤镜都不能真正动漫化 → 必须用外部 AI 工具（即梦AI/可灵/妙鸭）生成二次元头像，第一次迭代用他给的图即可
- ❌ 音乐用 Web Audio API 振荡器，不要引入 MP3/外部音频依赖
- ✅ 每个元素要有交互反馈；名字逐字弹出（200ms/字）+ 祝福语打字机（500-800ms/行）是标准节奏

### 完整可复制代码
庆祝页全套交互代码（星空粒子场/名字逐字/彩花爆炸150粒子/轨道光环/礼物盒overlay/浮动气球/Web Audio旋律/五角星clip-path/SVG动漫化滤镜/性能指南）见 `references/interactive-effects.md`、`references/canvas-particle-starfield.md`、`references/birthday-celebration-patterns.md`。

## 动态数据桥接

当项目需要展示每日更新的数据（量化推荐、日报、选品）时，用 `data.json` 桥接模式：Python同步脚本 → 输出data.json → HTML用fetch读取。

详见 `references/data-bridge-pattern.md`

## 嵌入渲染视频（Manim/Remotion 产物）

Yasin 会把「10个独立小动画」这种批量逐项动画视为**平淡课件感，会要求重做成整体沉浸式**（单支大片或 3D 页面）。当页面需要嵌入渲染好的视频（mp4）时：

- 视频文件放 `videos/`、海报帧放 `posters/`（ffmpeg 从 mp4 抽帧，路径用英文名避免中文 URL 问题）
- 弹窗播放用 `<video controls autoplay loop playsinline>`，**必须有 `.video-frame` 包裹层**
- **16:9 视频溢出修复（实测坑）**：给 `<video>` 直接设 `width:100% + max-height` 会先按容器宽算高再强压，比例崩成 2.4:1 元素溢出弹窗。正确姿势：
```css
.video-frame{
  width:auto;margin:0 auto;
  aspect-ratio:16/9;
  max-width:min(100%,880px,calc((100dvh - 210px)/0.5625)); /* 视口高度换算成16:9宽度 */
  max-height:calc(100dvh - 210px);
  border-radius:10px;overflow:hidden;background:#0c0d18;
}
.video-frame video{width:100%;height:100%;object-fit:contain;display:block;}
```
- 弹窗容器加 `max-height:100dvh;overflow-y:auto` 兜底，任何窗口尺寸不溢出
- Manim 渲染管线（像素画矩阵→动画→抽帧）见 `references/manim-video-integration.md`

## 3D 环形画廊（CSS 3D 展厅）

作品/卡片环绕 3D 空间、可拖拽旋转的展厅效果（`perspective` + `preserve-3d` + `rotateY(a) translateZ(R)`）：

- 每张卡片 `position:absolute; transform:rotateY(var(--a)) translateZ(680px) translate(-50%,-50%)`，`--a = (360/N)*i`
- 容器 `.ring{transform-style:preserve-3d; transform:rotateX(10deg) rotateY(var(--ry))}`
- 鼠标/触屏拖拽更新 `--ry`（`mousedown` 记录基线 + `mousemove` 增量），松手后 setInterval 每50ms 慢速自转（拖拽时暂停）
- 每卡片各自浮动动画（错峰 `--delay`），hover 时 `translateZ(46px)` 弹出 + 金色扫光 `::after` 线性扫过
- 背景三层：透视网格地板（`rotateX(58deg)` + mask 径向渐隐）+ 极光光晕 + Canvas 星空粒子
- 完整可复制实现见 `references/3d-ring-gallery.md`

## 用户偏好（动画/视频类）

- **批量逐项小动画 = 平淡课件感，会被否**。要做整体沉浸式：单支主视觉大片（展厅巡游/变形链/粒子汇聚）或 3D 交互页面
- 视频/动画类任务先给 2-4 个方向选项（A巡游大片 / B morph链 / C粒子汇聚 / D 3D页面）让 Yasin 拍板，他选完直接全量干，不要中途反复确认
- 弹窗/遮罩内视频必须实测尺寸，不要只靠代码逻辑判断
