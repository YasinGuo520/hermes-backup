---
name: course-sop-distillation
description: 课程PPTX蒸馏成可执行SOP：Markdown+Excalidraw+HTML三件套，入库Obsidian注册项目集。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [course, sop, distillation, pptx, training, obsidian]
    related_skills: [research-report-viz, excalidraw, obsidian, markitdown, document-text-extraction]
---

# 课程蒸馏成 SOP

把用户的培训课程材料（PPTX/PDF/视频转录）蒸馏成**可执行的SOP**，而不是复述原文。用户的核心诉求是"能照着执行"，不是"看懂课件"。

Triggers: "这个也总结蒸馏出来" + 课程文件、"把这个课做成SOP"、"提炼成方法论"。

## Workflow

### 1. 提取文本

1. 先试 `python3 -m markitdown <file.pptx>`（见 markitdown skill）。
2. 不可用时用 unzip + stdlib XML：`unzip -o file.pptx -d /tmp/pptx_raw`，然后解析 `ppt/slides/slideN.xml` 中 `{http://schemas.openxmlformats.org/drawingml/2006/main}` 命名空间的 `<a:t>` 标签，按幻灯片序号输出纯文本。

### 2. 蒸馏成框架（核心步骤）

- **绝不逐页复述**。把内容重组为用户执行时真正关心的结构，典型框架：
  - 心法/原则（一句话点透）
  - 分阶段SOP（Phase 0 准备 / Phase 1 起号 / Phase 2 打标签 / Phase 3 放大）
  - 每个阶段配：检查清单、节奏表（如7天放单表）、参数表
  - 复盘模板 + 常见踩坑自查表
- 每页幻灯片先判断属于哪个模块，再合并去重，再输出。
- 用户要的是数据说话、能打勾、能照做。不含方法论空话。

### 3. 三件套交付

| 交付物 | 说明 |
|--------|------|
| Markdown 手册 | 分阶段 + 勾选清单 + 表格，路径 `~/Desktop/hermes/<名称>SOP.md` |
| Excalidraw 作战地图 | 用 excalidraw skill 画阶段流程图（准备→起号→标签→放大→复盘循环），上传分享链接 |
| 交互 HTML 网页 | 用 research-report-viz 的暗色粒子模板：阶段导航pills + 可勾选清单(localStorage持久化) + 进度条 + 复盘模板 |

### 4. 入库与注册（用户强约定）

- 所有交付物放到 `~/Desktop/hermes/`（不是桌面根目录）。
- Obsidian Vault 同步一份（`~/Documents/Obsidian Vault/`）。
- 在 `~/Desktop/hermes/Yasin项目集.html`（及Obsidian副本）注册新HTML项目卡片。
- 命名禁用"海纳"（用户明确要求去掉），用通用名（如 抖音起号SOP）。

## Pitfalls

- Excalidraw 上传失败报 "cryptography package is required" 时，系统 python3 缺包但 Hermes venv 有 —— 用 `/Users/mac/.hermes/hermes-agent/venv/bin/python3 /Users/mac/.hermes/skills/creative/excalidraw/scripts/upload.py <file>` 跑。
- 交互HTML如果带粒子背景，在 Hermes 预览窗格开着会烧一整个CPU核（WebKit.WebContent ~97%）—— 预览完就关掉。
- 页面风格一律用暗色粒子（research-report-viz 模板），用户明确比较过：暗色 > 浅色卡片。
- PPTX提取纯文本即可，图表样式不保留，别浪费时间处理布局。

## 参考

- `research-report-viz` skill 的 "Delivery conventions (Yasin)" 章节持有通用的HTML交付约定（保存位置/项目集注册/命名/风格）。
- 抖音课程材料目录：`~/Downloads/同步空间/抖音/直播项目/总计划1/抖音资料/`
