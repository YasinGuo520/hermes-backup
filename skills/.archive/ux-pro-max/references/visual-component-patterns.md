---
name: visual-component-patterns
description: 前端视觉组件模式库 — 流动星光/徽章光环/玻璃卡片/彩花粒子/打字机效果等可复用组件
---

# 前端视觉组件模式库

> 从个人品牌页和生日庆祝页项目中提炼的可复用视觉组件。
> 偏向科幻/梦幻风格，适合个人主页、庆祝页、展示页。

---

## 组件清单

| 组件 | 适用场景 | 技术要点 |
|------|---------|---------|
| 流动星光背景 | 深色主题背景 | Canvas粒子+拖尾轨迹 |
| 徽章光环系统 | 个人头像展示 | 多层旋转border + 光点公转 |
| 凹凸水晶浮块 | 太空/科幻装饰 | clip-path六边形+渐变+浮动 |
| 玻璃卡片 | 内容展示/弹窗 | backdrop-filter:blur + 透明背景 |
| 打字机效果 | 文案逐行出现 | CSS opacity过渡 + JS setTimeout |
| 彩花粒子引擎 | 庆祝/交互反馈 | Canvas物理模拟（重力/阻力/生命周期） |
| 礼物盒子弹窗 | 隐藏内容揭晓 | overlay + backdrop + scale入场 |
| 轻量音乐播放 | 氛围背景音 | Web Audio API 简单音阶循环 |
| CRT雪花噪点 | 复古/科幻深色背景 | Canvas ImageData 降分辨率缩放（性能优化） |
| CRT扫描线 | 复古全屏覆盖 | CSS repeating-linear-gradient 1px黑+2px透交替 |
| CRT边缘暗角 | 复古屏显效果 | 多层 inset box-shadow 叠加，从80px到240px |
| 游戏盒封面卡片 | 像素风内容展示 | 上标签条+中内容+下装饰条三段式，border:3px double 方块边框 |
| 像素十字光标 | 复古交互反馈 | 内联SVG data:image/svg+xml 自定义 cursor，绿黑方格 |
| 标题闪烁/变色 | 复古标题/Logo | 双动画：color+flicker（颜色渐变发光）+ blink（细微闪烁） |
| **烟雾粒子背景** | 焚香/玄学/古风氛围 | Canvas双层径向渐变+上升漂移+生命周期，详见 `references/mystical-components.md` |
| **古风卷轴卡片** | 签文/诏书/信函展示 | 伪元素卷轴杆+径向渐变圆轴端盖+宣纸渐变背景 |
| **印章按钮** | 确认/提交/仪式感交互 | 暗红底金边+四角装饰点+按压scale动效+外发光环 |
| **烛光火焰** | 页面两侧氛围装饰 | 非对称border-radius火焰形状+渐变+跳动动画 |
| **电路板背景动画** | 科技工具/深色科幻页面背景 | Canvas栅格PCB走线+脉冲节点+流动数据包信号，详见 `references/circuit-board-canvas.md` |
| **技术工具箱卡片** | 工具库/产品目录/技能展示页 | 直角卡片+薄边框+左侧悬停发光条(cyan glow)+等宽字体标题+深蓝底，搜索框和分类滤波配套 |
| **3D环形展厅** | 作品集/画廊/展示页（像素画展厅等） | CSS perspective + preserve-3d 环形排列 + 拖拽旋转 + 自动慢转 + 玻璃卡片 hover 弹出，详见 `references/3d-ring-gallery.md` |

## 参考/引用

CRT/8bit 视觉效果的完整实现在会话 `pixel-gallery-crt-redesign` 中：
- Canvas 降噪算法：downscale 4x → ImageData → upscale 回原尺寸，15fps 刷新
- 卡通盒卡片三段结构：`cartridge-top` (渐变蓝标签条) + `pixel-canvas` + `cartridge-bottom` (绿黑条纹)
- 像素光标 SVG 结构：24x24 绿框，中心 12x12 绿方聚焦点，热区 (12,12)
- 手机响应式：标题缩至 0.85rem，卡片像素画缩至 96x96

## 用户偏好

- 个人主页/简历页 → **单页沉浸式布局**（全屏hero+滚动区块）
- 庆祝/生日页 → **全屏沉浸 + 多交互元素**（气球/礼物/彩花）
- 作品集/画廊/展示页 → **沉浸式3D**（3D环形展厅+星空粒子+玻璃卡片），不要平铺网格、不要"课件式逐幅动画"（用户原话：10个动画像课件演示，不够炫酷）
- 炫酷 > 逐个展示：用户选方案时优先「沉浸式3D页面」「展厅巡游大片」这类有气场的方向
- 交付节奏：用户说「直接生成就可以」= 一次做完渲染+页面+验证再交付，不要中途多轮预览确认打断
- ❌ 避免多阶段分屏过渡（用户反馈不如一层展示好）
- ✅ 头像直接放用户提供的图片，不用滤镜凑合

## 详细实现参考

详细代码实现在 ux-pro-max skill 的 SKILL.md 中已有标注，
实际在线案例：
- 个人主页：http://43.138.221.174:8898
- 生日页：http://43.138.221.174:8899
- 工具箱：http://43.138.221.174:8900

## 技术工具箱卡片（Tech-Toolbox Card）

用于工具库/方法论目录/技能展示页的可过滤卡片网格。

### 设计系统

| 属性 | 值 | 说明 |
|------|-----|------|
| 背景 | `#0a0e1a` | 深蓝科技底 |
| 主色 | `#00d4ff` | 青色 |
| 辅色 | `#0090ff` | 深蓝渐变 |
| 二级文字 | `#6a7a8a` | 灰色 |
| 卡片底 | `rgba(10,14,26,0.6)` | 半透明叠加 |
| 卡片边框 | `rgba(0,212,255,0.06)` | 细青边 |
| 标题字体 | `JetBrains Mono` | 等宽科技风 |

### CSS 关键片段

```css
/* 悬停左侧发光条 */
.card {
  position: relative;
  background: rgba(10,14,26,0.6);
  border: 1px solid rgba(0,212,255,0.06);
  border-radius: 0;  /* 直角 */
}
.card::before {
  content: '';
  position: absolute; top: 0; left: 0;
  width: 2px; height: 0;
  background: #00d4ff;
  transition: height 0.25s ease;
  box-shadow: 0 0 8px rgba(0,212,255,0.5);
}
.card:hover::before { height: 100%; }

/* 搜索框 - 直角+等宽+青色聚焦 */
.search-box input {
  background: rgba(10,14,26,0.8);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 0;
  font-family: 'JetBrains Mono', monospace;
}
.search-box input:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 24px rgba(0,212,255,0.08);
}

/* 分类标签 - 直角胶囊 */
.filter-tab {
  border-radius: 2px;
  background: rgba(10,14,26,0.8);
  border: 1px solid rgba(0,212,255,0.1);
  font-family: 'JetBrains Mono', monospace;
}
.filter-tab.active {
  background: rgba(0,212,255,0.1);
  border-color: #00d4ff;
  color: #00d4ff;
}

/* 统计数字青色发光 */
.header .stats span {
  color: #00d4ff;
  text-shadow: 0 0 12px rgba(0,212,255,0.4);
}
```

### HTML 布局结构

```
.header
  h1: "⚙ TOOLBOX" (gradient text)
  p: "METHODOLOGY_TOOLKIT // 子标题"
  .stats: "N TOOLS · M CATEGORIES · X ITEMS"
.controls
  .search-box: input + 前缀符号
  .filter-tabs: ALL | STARTUP | E-COMM | CONTENT ...
#toolbox
  .category
    .cat-title: 分类名 + .count 标签
    .card-grid
      .card[data-tags] (点击展开)
        .card-header: .card-icon + h3 + .expand-icon
        .card-body: p(description) + .card-meta > code(key)
.footer
```

### 功能要点

- 卡片默认折叠，点击展开详情（toggle 'expanded' class）
- 搜索实时过滤：`filterCards()` 匹配 data-tags（含key和name）
- 分类标签滤波：setFilter 匹配 category 标题文本
- 空白分类自动隐藏（display: none）
- 计数实时更新

## 玄学/古风组件

玄学风格的四件套（烟雾粒子背景 + 古风卷轴卡片 + 印章按钮 + 烛光火焰）实现在：
- `references/mystical-components.md` — 全部关键参数和样式要点

## 风格指纹：红蓝对决科技风（2026-07 沉淀）

源自「红蓝分析法方法论页」demo（~/Desktop/hermes/red-blue-method/index.html）。适合：方法论/对比/双派系/辩论主题页。

| 属性 | 值 |
|------|-----|
| 背景 | `#05050a` + 深蓝网格 `rgba(96,165,250,.08)` 50px + 网络节点Canvas(45节点,200px连线) |
| 标题渐变 | `#c4b5fd→#8b5cf6→#6366f1→#06b6d4` background-clip:text + 呼吸动画 5s |
| 蓝方 | 卡片 `linear-gradient(160deg,rgba(59,130,246,.10),rgba(59,130,246,.02))` + 边框 `rgba(59,130,246,.25)` |
| 红方 | 卡片 `linear-gradient(160deg,rgba(239,68,68,.10),rgba(239,68,68,.02))` + 边框 `rgba(239,68,68,.25)` |
| 卡片 | `rgba(255,255,255,.02)` + border `rgba(255,255,255,.08)` + 14px圆角 |
| 步骤号水印 | 伪元素 counter + 64px 大字 `rgba(139,92,246,.08)` 右上角 |
| CTA | 渐变紫按钮 `linear-gradient(135deg,#6366f1,#a78bfa)` + 发光阴影 |
| 入场 | IntersectionObserver 淡入上移 + 卡片 stagger 0.04s |
| 导航 | `rgba(5,5,10,.72)` + backdrop-blur(14px) + 底部细边框 |

复用要点：双阵营对立主题用红蓝卡片对打 + 裁决条收尾；步骤流程用 counter 水印编号卡片。

## 组件：动态表情贴纸角色（2026-07 沉淀）

CSS纯手绘卡通角色，无图片资源，可浮在任何深色页面上。实现在 ~/Desktop/hermes/red-blue-method/index.html。

### 角色种类（.face + 变体class）
| 变体 | 效果 |
|------|------|
| `.face`（默认） | 黄脸+圆眼眨眼(4.2s)+微笑，脸颊红晕`.blush l/r` |
| `.face.thinking` | 紫脸脉冲缩放，眼睛变眯眼，嘴变上弧 |
| `.face.happy` | 开口笑+头脉冲 |
| `.face.surprised` | 大眼带白高光+O型嘴 |
| `.face.angry` | 窄眼+平嘴 |
| `.face.bot` | 蓝方头+天线红点闪烁，配`.think-bubble` |

### 结构模板
```html
<div class="sticker s-hero-r" data-lines='["文案1","文案2"]'>
  <div class="face bot thinking">
    <span class="antenna"></span>
    <div class="think-bubble"><span class="think-dots"><span></span><span></span><span></span></span></div>
    <div class="head"><span class="eye"></span><span class="eye"></span></div>
    <div class="mouth"></div>
  </div>
</div>
```

### 关键机制
- `.sticker`: absolute + floaty浮动(6s) + hover放大旋转 + drop-shadow
- 点击互动：jump动画 + 随机换表情（moodFor按角色取moods池）+ 气泡文案轮换（data-lines循环）+ WebAudio叮一声
- `.think-bubble`: 白气泡+尾巴，thinkFade常显微动；`.think-dots`三点波
- `.sparkle`: 星星✨常显脉动（opacity .7→1，不要0→1否则截图不可见）
- 位置类: s-hero-r/s-hero-l/s-duel/s-steps/s-cta（section需position:relative）
- 移动端768px隐藏s-hero-l，防遮挡

### 踩坑
- 动画opacity 0→1的周期元素（气泡/星星）截图时可能正好隐藏 → 改成常显微动（opacity .7~1）
- 贴纸用 absolute 定位，父容器必须有 position:relative，否则定位乱跑
- CSS手绘角色(face)已升级为AI立绘方案，见下节「AI立绘机器人贴纸」

## 组件：AI立绘机器人贴纸（方案C，2026-07 沉淀）

AI生成3D赛博机甲立绘 → 抠图 → 页面贴纸，替代CSS手绘。质量碾压手绘，成本1-2元/4张。

### 全流程
1. **生成**：SiliconFlow Qwen-Image，curl调用（**python urllib/requests直连会Connection reset，必须用curl**）
   - 提示词模板：`[角色描述], 3D render, sticker design, cyberpunk mecha style, glowing neon accents, dark navy blue solid background, clean white outline, cute mascot, centered, high quality, octane render`
   - 统一风格靠固定STYLE_TAIL，角色差异只改前缀
   - 注意：后台bash脚本里curl也失败（环境差异），**必须前台逐张跑**，失败重试3次
2. **抠图**：不用rembg（pip被腾讯云镜像代理坑），用 **ffmpeg + numpy 色键抠图**：
   - 每张图背景色不同，先采样四角像素取均值
   - RGB距离阈值(30) + feather(15) 生成alpha，ffmpeg只做PNG编解码
   - 脚本：`china-ai-platforms` 技能的 `scripts/chroma_cut.py`（可复用，支持自动采样背景色），会话内副本 `~/Desktop/hermes/images/robot/cut_bg.py`
3. **集成**：`<img class="robot-img">` 进.sticker，保留浮动/点击跳跃/气泡/音效互动
   - `botGlow` 动画：霓虹光晕呼吸（drop-shadow 两段）
   - 尺寸120px，角落贴纸用 sm(96px)
4. **验证**：browser_vision 逐区域检查（hero两角/对决区/流程区），确认无遮挡、无深蓝残留底块

### 角色库（已生成，可复用）
- robot_thinking（蓝+问号，hero右上）
- robot_happy（金+星星，hero左下）
- robot_attack（红+盾牌，对决区）
- robot_surprised（紫+感叹号，流程区）
- 源文件：~/Desktop/hermes/images/robot/*.png，页面版：red-blue-method/images/

### pip代理坑（腾讯云）
- pip默认index是mirrors.tencentyun.com，会ProxyError断连
- 临时绕过：`pip install --index-url https://pypi.org/simple --trusted-host pypi.org`
- 装不上的库优先找ffmpeg/numpy替代方案，别死磕pip

## 组件：AI立绘动态升级（v2，2026-07 沉淀）

在AI立绘贴纸基础上加两层动态：**表情帧序列** + **3D视差倾斜**。实现在 red-blue-method/index.html。

### 表情帧序列（说话/大笑）
- 同一角色生成2帧（闭口版/开口版），提示词保持主体一致只改 `mouth open speaking` / `laughing mouth wide open`
- 帧切换位置/大小对齐良好（验证过不跳），姿势小差异可接受
- HTML: `data-frames='["img_a.png","img_b.png"]'`，JS每3.8s切到第2帧0.65s再切回
- `document.hidden` guard 防后台切帧

### 3D视差倾斜
- `.sticker` 加 `perspective:600px`，`.robot-img` 加 `transform-style:preserve-3d` + `will-change:transform`
- JS: `mousemove` 全局监听 → `rotateY(nx*16deg) rotateX(-ny*12deg)`，requestAnimationFrame节流
- hover光晕跟随：img不能有::after → JS动态创建overlay div，mousemove更新radial-gradient位置

### 验证技巧
- browser_console 直接查 DOM 状态：frames数据、glow元素、transform值
- 手动 dispatchEvent MouseEvent 模拟鼠标位置验证视差
- 手动切 img.src 验证帧图可加载（onload + naturalWidth）
