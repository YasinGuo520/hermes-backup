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
