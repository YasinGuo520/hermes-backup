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

## 参考/引用

CRT/8bit 视觉效果的完整实现在会话 `pixel-gallery-crt-redesign` 中：
- Canvas 降噪算法：downscale 4x → ImageData → upscale 回原尺寸，15fps 刷新
- 卡通盒卡片三段结构：`cartridge-top` (渐变蓝标签条) + `pixel-canvas` + `cartridge-bottom` (绿黑条纹)
- 像素光标 SVG 结构：24x24 绿框，中心 12x12 绿方聚焦点，热区 (12,12)
- 手机响应式：标题缩至 0.85rem，卡片像素画缩至 96x96

## 用户偏好

- 个人主页/简历页 → **单页沉浸式布局**（全屏hero+滚动区块）
- 庆祝/生日页 → **全屏沉浸 + 多交互元素**（气球/礼物/彩花）
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
