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
