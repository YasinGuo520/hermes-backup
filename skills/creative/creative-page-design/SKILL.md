---
name: creative-page-design
description: 情感化/庆祝类页面设计——多阶段叙事+交互元素+调研先行。UX Pro Max 的创意层补充。
---

# Creative Page Design — 创意页面设计

> 配套 UX Pro Max（视觉规范层），这个是 **创意/体验层**。
> Yasin 说「只有几个字」= 不满意我停留在文字展示阶段。
> **关键规则：先调研全球设计，再动手。不要凭经验硬写。**

## 什么时候触发

当 Yasin 要求设计的页面带有情感属性时：
- 生日/庆祝页
- 个人介绍/展示页
- 纪念日/活动页
- 任何他说「不够大气」「要设计感」的页面

## 第一步：先调研（硬性规则）

不要直接写代码。先搜索：
```
best birthday website design inspiration
creative celebration page codepen
award winning personal website design
```

提取 3-5 个核心设计模式后再合成。调研来源参考：
- onepagelove.com (生日标签)
- GitHub (birthday-bloom, Birthday-V4 等项目)
- Awwwards 获奖页面

## 多阶段叙事架构

不要一次显示所有内容。按时间线展开：

```
阶段1: 标题/名字逐个字符弹出（200-300ms/字）
  ↓ pause 1-2s
阶段2: 副标题/年龄/标签淡入
  ↓ pause 2s
阶段3: 主视觉元素（徽章/头像/标志物）从下方弹入
  ↓ 同时：轨道光环开始旋转
阶段4: 祝福/内容打字机效果逐行显现（500-800ms/行）
  ↓ 同时：浮动装饰开始出现
阶段5: 交互元素激活（礼物盒/气球/音乐开关）
```

### 代码模式

```javascript
// 名字逐字弹出
name.split('').forEach((ch, i) => {
  const span = document.createElement('span');
  span.textContent = ch;
  span.style.transitionDelay = `${i * 200}ms`;
  nameContainer.appendChild(span);
});

// 阶段切换用 timeline setTimeout, 不用 scroll
setTimeout(() => stage1.hide(), nameChars * 200 + 2800);
setTimeout(() => stage2.show(), nameChars * 200 + 3000);
```

## 交互元素清单

| 元素 | 代码复杂度 | 效果 | 实现 |
|------|-----------|------|------|
| Canvas流动星光 | ⭐⭐ | 底层动态感 | 120-150粒子+trail拖尾+间距连线 |
| 浮动气球(点击爆炸) | ⭐ | 轻松欢乐 | CSS动画+class切换 |
| 物理Confetti | ⭐⭐⭐ | 高潮反馈 | canvas粒子:重力0.2/阻力0.97/寿命150-300帧 |
| 打字机效果 | ⭐ | 情绪节奏 | 逐字符/逐行setTimeout显现 |
| 礼物盒弹出卡片 | ⭐⭐ | 隐藏惊喜 | overlay+缩放动画+关闭按钮 |
| Web Audio旋律 | ⭐⭐⭐ | 氛围感 | OscillatorNode+sine波+0.04增益 |
| 凹凸旋转星 | ⭐ | 二次元装饰 | clip-path星星+旋转动画+drop-shadow |

## 全屏沉浸设计规则

- **背景：** 深色 ( #0a0a12 / #0b0c12 ) + 环境光晕径向渐变
- **Z-index分层：** z0: Canvas粒子 → z1: 环境光晕 → z2: 浮动装饰 → z3: 内容层 → z4: 交互弹窗 → z999: Confetti
- **字体：** clamp(2.5rem, 8vw, 5rem) 大标题，梯度渐变文字
- **动效时长：** 入场0.6-1.5s，交互反馈0.2-0.4s
- **不要：** 居中白色小卡片、纯文字无交互、一次性全显示

## 吧唧（徽章）设计模式

适合作为页面视觉焦点：

```
外层: 3圈旋转圆环（40s/28s/18s 不同速度）
中层: 5个卫星粒子沿轨道飞旋（6s周期，72deg间隔）
内层: 渐变深紫背景 + 脉冲发光动画
核心: 圆形头像（130px），支持图片替换
```

## 避免

- ❌ 不做调研直接写代码
- ❌ 一次全显示完，没有展开节奏
- ❌ 只有文字没有交互元素
- ❌ 浅色背景+小尺寸卡片
- ❌ 动效超过1.5s（拖沓）

## 相关技能

- `ux-pro-max` — 视觉规范层（配色/间距/阴影/圆角等基础规则）
- 先加载 UX Pro Max 套基础规范，再加载本技能做创意设计
