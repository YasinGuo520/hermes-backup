# 9宫格分镜模板（整理自 Micro-Drama-Skills / zhaihao118）

详细的短剧分镜JSON结构模板，适用于分镜规划、AI视频生成提示词编写。

---

## 总览

每集短剧 = **30秒** = **2个Part**（各15秒）
每个Part = **9宫格分镜**（3×3布局，每格约1.67秒）

```
| 格1 (0.0-1.67s) | 格2 (1.67-3.33s) | 格3 (3.33-5.0s) |
| 格4 (5.0-6.67s)  | 格5 (6.67-8.33s)  | 格6 (8.33-10.0s) |
| 格7 (10.0-11.67s)| 格8 (11.67-13.33s)| 格9 (13.33-15.0s) |
```

---

## 编号规则

- 作品编号：`DM-XXX`（001开始递增）
- 视频编号：`{编号}-EP{集数}-{A|B}`
  - 上半部分：`DM-001-EP01-A`
  - 下半部分：`DM-001-EP01-B`
- 集数：`EP01` ~ `EP25`

---

## 故事板配置 JSON 模板

```json
{
  "video_id_prefix": "DM-001-EP01",
  "episode": 1,
  "episode_title": "第1集标题",
  "total_duration_seconds": 30,
  "fps": 24,
  "resolution": "1920x1080",
  "aspect_ratio": "16:9",
  "style": "short_drama",
  "visual_style": {
    "style_id": 1,
    "style_name": "Cinematic Film",
    "camera": "Panavision Sphero 65 and Hasselblad Lenses",
    "film_stock": "Vision3 500T 5219",
    "filter": "ND0.6, Diffusion Filter 1/4",
    "focal_length": "65mm",
    "aperture": "f/2.0",
    "prompt_suffix": "shot on Panavision Sphero 65 and Hasselblad Lenses, Vision3 500T 5219, ND0.6, Diffusion Filter 1/4, cinematic film grain, shallow depth of field"
  },
  "subtitle": false,
  "synopsis": "本集剧情概要（100字）",
  "emotion_tone": "情感基调",
  "connection": {
    "from_previous": "与上集的衔接",
    "to_next": "为下集的铺垫"
  },

  "part_a": {
    "video_id": "DM-001-EP01-A",
    "label": "上",
    "time_range": "00:00-00:15",
    "duration_seconds": 15,
    "scene_refs": ["scene_01"],
    "prop_refs": [],
    "atmosphere": {
      "overall_mood": "上半部分氛围总描述",
      "color_palette": ["#色值1", "#色值2", "#色值3"],
      "lighting": "光影描述",
      "weather": "天气/环境"
    },
    "video_prompt": "English prompt for AI video generation of Part A (15s), 16:9 aspect ratio. No subtitles.",
    "bgm": {
      "description": "背景音乐描述",
      "mood": "音乐情绪关键词"
    },
    "storyboard_9grid": [
      {
        "grid_number": 1,
        "time_start": 0.0,
        "time_end": 1.67,
        "scene_description": "画面描述（50字，含人物动作、表情、光影）",
        "camera": {
          "type": "远景|中景|近景|特写",
          "movement": "固定|推|拉|摇|移|跟",
          "angle": "平视|俯视|仰视"
        },
        "characters": [
          {
            "name": "角色名",
            "action": "动作描述",
            "expression": "表情",
            "position": "画面位置(左/中/右)"
          }
        ],
        "dialogue": {
          "speaker": "角色名（无对话则为null）",
          "text": "中文对话内容",
          "emotion": "语气/情感"
        },
        "atmosphere": "本格氛围描述",
        "sfx": "音效描述",
        "ai_image_prompt": "English prompt for this grid's image: character, composition, lighting, mood, 16:9 aspect ratio."
      },
      {
        "grid_number": 2,
        "time_start": 1.67,
        "time_end": 3.33,
        "scene_description": "...",
        "camera": {},
        "characters": [],
        "dialogue": {},
        "atmosphere": "...",
        "sfx": "...",
        "ai_image_prompt": "..."
      }
    ]
  },

  "part_b": {
    "video_id": "DM-001-EP01-B",
    "label": "下",
    "time_range": "00:15-00:30",
    "duration_seconds": 15,
    "scene_refs": ["scene_02"],
    "prop_refs": ["prop_01"],
    "atmosphere": {
      "overall_mood": "下半部分氛围总描述",
      "color_palette": ["#色值1", "#色值2", "#色值3"],
      "lighting": "光影描述",
      "weather": "天气/环境"
    },
    "video_prompt": "English prompt for AI video generation of Part B (15s), 16:9 aspect ratio. No subtitles.",
    "bgm": {},
    "storyboard_9grid": []
  }
}
```

---

## 对话脚本模板

```markdown
# 第X集：标题 对话脚本

## 注意：本集视频不带字幕，对话通过配音传达

## 上半部分（Part A：00:00-00:15）
## 视频编号：DM-001-EP01-A

| 序号 | 时间 | 角色 | 对话内容（中文） | 语气/情感 | 备注 |
|------|------|------|----------------|----------|------|
| 1 | 00:02 | 角色A | 「对话内容」 | 坚定 | — |
| 2 | 00:06 | 角色B | 「对话内容」 | 惊讶 | — |
| 3 | 00:11 | 角色A | 「对话内容」 | 激动 | — |

## 下半部分（Part B：00:15-00:30）
## 视频编号：DM-001-EP01-B

| 序号 | 时间 | 角色 | 对话内容（中文） | 语气/情感 | 备注 |
|------|------|------|----------------|----------|------|
| 4 | 00:17 | 角色B | 「对话内容」 | 低沉 | — |
| 5 | 00:22 | 角色A | 「对话内容」 | 温柔 | — |
| 6 | 00:27 | 角色C | 「对话内容」 | 神秘 | — |
```

---

## 角色圣经模板

```markdown
# 角色设定集

## 主要角色

### 角色1：名字
- **全名**：
- **年龄**：
- **性别**：
- **身高/体重**：
- **外貌特征**：[详细描述，用于AI绘图提示词]
  - 发型/发色：
  - 瞳色：
  - 体型：
  - 标志性特征：
- **服装设计**：
  - 日常服装：
  - 特殊服装：
- **性格特点**：
- **口头禅**：
- **背景故事**：[100字]
- **角色弧光**：[在25集中的成长变化]
- **AI绘图关键词（英文）**：[用于角色一致性]
```

## 场景圣经模板

```markdown
# 场景设定集

### 场景1：场景名称
- **场景ID**：scene_01
- **场景描述**：[50-100字]
- **出现集数**：EP01, EP02, EP05...
- **关键视觉元素**：[标志性物件、色调、灯光]
- **AI绘图关键词（英文）**：[含空间布局、光影、陈设风格]
```

## 道具圣经模板

```markdown
# 道具设定集

### 道具1：道具名称
- **道具ID**：prop_01
- **道具描述**：[30-50字，外观、材质、尺寸]
- **出现集数**：EP10, EP12...
- **剧情意义**：[象征/功能意义]
- **AI绘图关键词（英文）**：[含材质、颜色、形状、细节]
```

---

## 剧本大纲结构（25集）

| 阶段 | 集数 | 内容 |
|:----|:----:|------|
| 第一幕 | 1-3集 | 世界观介绍、角色登场、引入冲突 |
| 第二幕 | 4-8集 | 冲突升级、角色关系建立 |
| 第三幕 | 9-15集 | 高潮前奏、多线叙事、伏笔布局 |
| 第四幕 | 16-20集 | 高潮阶段、转折、揭示 |
| 第五幕 | 21-24集 | 最终决战、情感爆发 |
| 结局 | 25集 | 结局、余韵 |

## 创作规范

- **对话**：全中文，每句不超过15字，每集3-6句（上下各1-3句）
- **画面**：不带字幕，对话通过配音传达
- **每集结尾**：留悬念或情感钩子
- **每格1.67秒**：9格之间需有视觉连续性和叙事逻辑
