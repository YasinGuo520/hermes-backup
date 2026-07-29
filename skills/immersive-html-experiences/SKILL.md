---
name: immersive-html-experiences
description: 沉浸式交互HTML页面设计模式 — 庆典页/全屏展示/粒子动效/互动装饰。纯原生HTML+CSS+JS，零依赖。
---

# Immersive HTML Experiences

当Yasin要求做「庆典/全屏/沉浸」类HTML页面时使用。包含深色系设计系统、粒子动画、交互元素、头像动漫化等完整模式。

## 触发条件

Yasin说：生日页面/庆祝页面/全屏展示/沉浸效果/科幻风格

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

## 预览工作流

```
1. 文件存 ~/Desktop/hermes/[项目]/index.html
2. python3 -m http.server 8899 --bind 0.0.0.0 (background)
3. browser_navigate(http://43.138.221.174:8899)
4. 改代码后 kill + 重启 + ?t=N 清缓存
5. browser_vision 验证视觉
```
