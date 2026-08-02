---
name: short-drama-pipeline
description: "完整的短剧/网文自动化生产流水线：爆款调研→创意生成→反AI润色→分发，三阶段闭环"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
---

# 短剧/网文自动化生产流水线

> **外部工具参考**: `references/external-tools-comparison.md` — 收录5个外部短剧AI工具（aliang-skills / Micro-Drama-Skills / 橙星漫工厂 / 小云雀短剧Agent / welopc-opc-drama-agent）的对比、费用结构、集成方式与性价比分析，以及**与llm-video-maker/本地管线的三管线对比决策树**。用户问短剧/AI视频工具选型、成本评估、安装配置时先查该文件。aliang-skills已安装到Hermes（6个skill），bailian-cli已装但需配API Key。
>
> **视觉风格预设**: `references/visual-styles-presets.md` — 10种电影级视觉风格（电影质感/赛博朋克/水墨国风/港风复古/韩剧氛围等），含完整camera/film/filter/prompt_suffix参数。生成视频提示词时可指定风格ID或中文名。
>
> **分镜模板**: `references/storyboard-templates.md` — 9宫格分镜JSON模板、对话脚本模板、角色/场景/道具圣经模板、25集剧本大纲结构。适用于短剧分镜规划和AI视频提示词编写。

## 整体架构

```
阶段一：爆款研究系统
  采集 → 分析 → 建立特征库
    ↓
阶段二：创意生成系统  
  融合特征 → 大纲 → 逐集生成 → 创意注入
    ↓
阶段三：反AI检测 + 润色系统
  Humanizer去AI化 → 风格迁移 → 终审 → 输出
```

---

## 阶段一：爆款研究系统

### 1.1 数据采集

用 browser 工具访问以下平台采集爆款数据：

```yaml
采集目标:
  - 平台: ["番茄小说排行", "抖音短剧热搜", "快手短剧热门", "微博短剧话题"]
  采集内容:
    - 标题、简介、标签
    - 前3章/前3集内容
    - 读者评论/弹幕关键词
    - 数据指标（热度、评分、集数）
```

执行命令示例：

```bash
# 使用 browser 打开各平台采集数据
browser_navigate(url="https://fanqienovel.com/rank")
browser_snapshot(full=true)
# 提取排行数据
```

### 1.2 爆款特征提取

每次采集到内容后，Hermes 自动执行以下分析：

```
分析维度：
  1. 开头钩子模式   — 前3段/前30秒的冲突设计
  2. 章节节奏       — 多少字一个反转/高潮
  3. 情绪曲线       — 虐→爽的转换节奏
  4. 人物设定套路   — 常见人设组合
  5. 对话占比       — 叙述vs对话比例
  6. 常用冲突模式   — 打脸/误会/身份反转等
  7. 金句密度       — 爆款金句出现的频率和位置
```

### 1.3 爆款特征库

分析结果持久化存储到 `~/.hermes/skills/creative/short-drama-pipeline/scripts/trend_db.json`，格式如下：

```json
{
  "genre": "重生复仇",
  "trends": [
    {
      "hook_pattern": "开局直接冲突, 不留铺垫",
      "chapter_rhythm": "每800字一个小反转, 2000字一个大高潮",
      "emotion_curve": "先虐后爽, 3:7比例",
      "common_archetypes": ["被背叛女主", "隐藏大佬", "忠犬男二"],
      "dialogue_ratio": 0.6,
      "conflict_patterns": ["身份揭露打脸", "当众反转"],
      "catchphrase_density": "每章节2-3句"
    }
  ],
  "updated_at": "2026-07-02T13:37:00Z"
}
```

---

## 阶段二：创意生成系统

### 2.1 生成前配方（Formula Prompt）

每次生成前，构建结构化配方：

```
[爆款特征种子]  ← 来自阶段一
  + 
[用户创意输入]  ← 用户提供的核心创意
  +
[Hermes创意注入] ← 反套路设计、深度设定
  =
[最终生成指令]
```

### 2.2 创意注入层

以下是我设计的一些**反套路创意模块**，可随机组合：

| 模块 | 说明 | 例子 |
|:---|:---|:---|
| **人设反转** | 开局看似套路人设，第3集揭示隐藏身份 | "以为是傻白甜，其实是退役兵王" |
| **双线结构** | 明线+暗线同步推进，暗线第5集才暴露 | "表面争家产，暗里查真凶" |
| **视角切换** | 每集换一个配角视角叙述 | "第1集女主视角→第2集男主→第3集反派" |
| **时间错位** | 倒叙中套倒叙 | "开头是结局，然后倒回3天前" |
| **黑色幽默** | 在爽文中加入荒诞元素 | "反派每次装逼都被雷劈" |

### 2.3 生成流程

```
Step 1: 输入 → 生成大纲（3-5个方案供选择）
Step 2: 选定方案 → 生成分集细纲
Step 3: 逐集生成（每集独立调用，保证每集有独立高潮）
Step 4: 审核集与集之间的连贯性
Step 5: 输出结构化JSON剧本
```

---

## 阶段三：反AI检测系统

### 3.1 一键去AI化（Humanizer 技能）

每次生成完后，自动应用 `humanizer` 技能的29条规则：

**高频AI词汇替换表：**
```yaml
AI词 → 人类词
"然而" → "可", "但", "不过"
"此外" → "另外", "还有", "再说"
"值得注意的是" → 直接删掉
"突然" → 保留60%，其余用"猛地"/"冷不丁"/"一转眼"
"因此" → "这下", "得", "结果"
"表示" → "说", "开口", "丢下一句"
"仿佛" → 删掉70%，直接写事实
```

### 3.2 风格迁移引擎

模仿人类网文作者的写作特征：

```
1. 句子长度变化：3-5字短句 + 20-30字长句交错
2. 段落节奏：不超过4行一段，3行最佳
3. 对话标签：少用"说"，多用动作+表情代替
   ❌ "你怎么来了？"她说。
   ✅ "你怎么来了？"她端着咖啡的手顿了顿。
4. 口语化插入：适当加入"啊"、"嘛"、"呢"、"吧"
5. 故意留一些"不完美"：偶尔用口语重复、倒装、断句
```

### 3.3 三审机制

```
一审（AI检测扫描）:
  - 用 Humanizer 的29个模式扫描，标红所有AI痕迹
  - 自动替换高频AI词
  
二审（风格匹配）:
  - 对比目标平台的语料风格
  - 调整句子节奏和段落长度
  
三审（终审输出）:
  - 读一遍全文，标记任何"像AI写的地方"
  - 人工感强化：加入语气词、情绪词
  - 输出最终版
```

### 3.4 持续性反检测策略

| 策略 | 说明 |
|:---|:---|
| **每集换风格** | 同一部剧不同集用不同的句式偏好 |
| **植入作者签名** | 每部作品设定一个排他性用词习惯 |
| **随机不完美** | 故意留1-2处 "手误"（错别字/标点不一致）|
| **情绪真实** | 加入作者的"情绪波动"，不完全理性叙述 |

---

## 完整执行流程（一条命令启动）

```bash
# 步骤1：调研 → 分析爆款趋势
hermes chat -q "调研当前番茄小说和抖音短剧的爆款趋势，提取2026年6月的热门元素，保存到特征库"

# 步骤2：生成剧本（带创意配方）
hermes chat -s short-drama-pipeline -q "用重生复仇题材，主角被闺蜜未婚夫双杀重生回到订婚宴，帮我生成10集短剧剧本，每集3分钟，加入反套路创意"

# 步骤3：去AI化润色
hermes chat -s humanizer -q "把我刚刚生成的剧本全文去AI化，逐句扫描并改写"
```

---

## 阶段四：视觉制作（百炼出图 + 图生视频成片，合并自 aliang-shortvideo）

当剧本/分镜定稿后要出**可播短剧成片**时，走百炼 bl CLI 五段流水线（**视频生成费钱：①~④可放心跑，⑤ i2v 默认只产命令不实跑，需用户显式确认付费**）：

```
① 剧情大纲 → ② 分集剧本(台词) → ③ 分镜表(枢纽) → ④ 批量出关键帧图 → ⑤ 图生视频成片
```

- **开工确认4件事**：一句话灵感（必问）+ 题材（8大题材爽点库见 `references/genres.md`，用 AskUserQuestion 给3-4项）+ 总时长（15s/30s/60s，**图片张数 ≈ 总时长÷5**，每5s一镜一张）+ 画风（22种预设见 `references/styles.md`，分写实/动漫/3D-CG/插画/风格化5类，**画风是画面质量头号变量必须开工就定**；用户甩参考图时用 `bl vision` 读成 style 串 + `bl image edit` 迁移画风）
- **分镜表 + storyboard.json 双产物**：给人看的分镜表格（镜号/时长/景别/运镜/画面/台词/情绪）+ 给脚本的 `storyboard.json`（全片统一 style、固定 `characters[].desc`、每镜 `image_prompt`，结构见 `references/storyboard.md`）。单镜时长可逐镜调（10s/15s 按5s拆子镜）
- **批量出图**：`python3 scripts/gen_images.py --storyboard <项目>/storyboard.json --outdir <项目>`（自动拼 style+角色desc）；**先验主角脸**（`--only 1,2` 只出前2镜确认长相再全量）；`--dry-run` 只看命令不烧额度；主角基准图设 `characters[].ref` 自动切 `bl image edit` 参考图模式
- **图生视频（💰 确认后逐段跑）**：每张关键帧 `bl video generate --image shot_NN.png --ratio 9:16 --duration 5`（运镜 prompt 取分镜表 camera+动作），ffmpeg 按镜号拼接成片
- **爽点抽取**：`python3 scripts/pick_beats.py --genre <题材>` 真随机抽8-12个爽点避免套路雷同（题材爽点库+结构模板+内容红线见 `references/genres.md`）
- 每阶段产出后**暂停等用户确认**再进下一阶段；项目目录：outline.md / script.md / storyboard.md / storyboard.json / images/shot_NN.png / video/shot_NN.mp4

## 自动化调度（Cron 批量任务）

```bash
# 每日自动生产5集并分发
hermes cron create "0 9 * * *" \
  --name "daily-drama-production" \
  --skills "short-drama-pipeline,humanizer" \
  --prompt "执行日常短剧生产流程：1) 先用browser调研当前爆款趋势更新特征库 2) 用设定的配方生成5集复仇短剧 3) 去AI化润色 4) 输出到~/output/drama/ 5) 汇总生产报告"
```

---

## 输出格式

```json
{
  "drama_title": "重生归来：总裁我不伺候了",
  "total_episodes": 10,
  "episode_length": "3分钟/集",
  "episodes": [
    {
      "episode": 1,
      "title": "订婚宴上的背叛",
      "hook": "穿上婚纱的那一刻，我看到了未婚夫手机里和闺蜜的聊天记录...",
      "script": "全文...",
      "duration": "180秒",
      "cliffhanger": "门被推开，一个意想不到的人走了进来"
    }
  ],
  "style_signature": "作者特征：短句密集、金句多、对话占比60%",
  "anti_ai_report": {
    "patterns_removed": 23,
    "style_matched": "番茄小说-重生分类",
    "human_score": "92%"
  }
}
```
