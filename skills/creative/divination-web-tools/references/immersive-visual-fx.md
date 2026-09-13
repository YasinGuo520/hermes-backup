# 沉浸式视觉特效（背景层注入配方）

> 吸收自 `xuanxue-ai-tools`（curator 合并）。玄学线四页（塔罗/八字/面相/抽签）实测配方；架构/排盘/合规/Hub 部分见父技能 SKILL.md。

## 铁律：只加层，不动功能 JS

- 特效**全部独立注入**：一个 `position:fixed;inset:0` 的背景层 + 自包含 IIFE canvas，**不碰原功能代码**——四页实测零破坏。
- 背景层：`position:fixed;inset:0;z-index:0;pointer-events:none`。
- 内容容器 `.wrap` 必须 `position:relative;z-index:1`——原静态内容会被 fixed 层盖住，这是「加了背景后内容点不到」的最常见坑，别先去改控件实现。
- canvas JS 开头 guard：`const cv=document.getElementById('fx'); if(!cv) return;`，用独立 IIFE 命名避免与页面已有变量冲突。

## 风格库（每站一主题，用户要「各自神秘玄幻」）

| 站点 | 主题 |
|------|------|
| 塔罗 | 星空薄雾 + 旋转三层法阵环（SVG/canvas 环，gold 描边） |
| 八字 | 太极☯慢转 + 五行五色灵光按方位呼吸 |
| 面相 | 顶部月华呼吸 + 月白星光 + 上传框 hover 光晕 |
| 抽签 | 红金庙宇 + 香火烟雾（自带） |

## 两个已验证的 CSS/动画坑

1. **环动画 transform 冲突**：父环用 `transform:translate(-50%,-50%)` 居中时，动画会覆盖该 translate；子伪元素环若复用同一 keyframes 会被 translate 带偏 → **拆两个 keyframes**（带 translate 的父 / 纯 rotate 的子）。
2. **字体辉光**：标题辉光用 `-webkit-text-fill-color:transparent` + `drop-shadow` 做动画时，`filter` 会被 animation 覆盖 → keyframes 里必须**重复完整 filter 值**。

## 交付验收

每页加载后：背景层可见、内容可点（点一次上传/切换）、无 console 报错（服务器无浏览器时用 `scripts/check_html_js_syntax.py` 至少保住 JS 语法），再挂 hub。
