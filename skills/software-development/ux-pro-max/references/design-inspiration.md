---
name: design-inspiration
description: 用户想要"炫酷网站"时，先展示视觉参考再动手做的完整流程。覆盖从"给我看几个好看的"到"帮我做一个这样的"的全链路。
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [design, inspiration, landing-page, ui, visual, reference, mockup]
platforms: [linux, macos, windows]
triggers:
  - 给我看几个炫酷的网站
  - 有什么好看的落地页
  - 我想做个酷酷的网站
  - 帮我找灵感
  - show me some cool sites
  - landing page inspiration
  - 有什么推荐的风格
---

# Design Inspiration

## When to use

用户说"想做个炫酷的网站/落地页"但还没想好具体做什么风格时。**先给他们看选项，再动手。**

关键区别：
- **design-inspiration** = 展示已有优秀案例 → 帮用户确认方向
- **sketch** = 在手艺人确定方向后，生成2-3个HTML变体对比
- **claude-design** = 做一个完整的HTML成品落地页

## 工作流

### Step 1: 确认意图

先一刀切清楚——**商业目的还是纯玩？**

```
问题：这个网站是商业目的还是纯玩？
- 商业目的 → 结合品牌/产品做有转化目标的设计
- 纯玩 → 随便选好看的，"爽"就行
- 不确定 → 推几个选项，让用户看了再说
```

### Step 2: 展示参考（从 references/stunning-landing-pages.md 加载）

```
load skill reference: stunning-landing-pages.md
```

按推荐矩阵给用户推荐3-5个案例，优先推震撼感最强的（Ivress）。

对每个案例给出：
- 一句精华（它为什么酷）
- 技术栈（别太技术向，说人话）
- Demo链接（直接可看）

### Step 3: 用户选定后 → 转交执行

| 用户选了什么 | 下一步 |
|-------------|--------|
| 单页展示型 | 加载 `sketch` 或 `claude-design` 做HTML |
| 3D叙事型 | 指向 Three.js + GSAP 方案，问要不要做 |
| AI产品风格 | 推 Brainwave 源码直接改 |
| 想要更便宜的 | 单文件HTML + 系统字体 + Tailwind CDN |

### Step 4: 用户说"就这个风格" → 开干

不废话，直接：
```
write_file → browser_navigate → browser_vision(检查视觉) → 给链接
```

## 用户偏好（Yasin）

- 训斥狠厉语气，不客套不温柔
- 极简沟通，2-5字短句
- 想炫酷先看参考，别直接干
- 先确认是纯玩还是商业目的，别默认要变现

## 陷阱

- ❌ 用户说"炫酷"不一定是3D——先展示，等ta自己选
- ❌ 别在灵感阶段就推技术方案——先看风格，再谈怎么做
- ❌ 别把纯玩的目的硬往商业变现方向扯
