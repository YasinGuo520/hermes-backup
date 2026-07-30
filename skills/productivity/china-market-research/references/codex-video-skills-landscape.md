# Codex 视频生态 Skills 与 Hermes 对标

## 背景

当用户看到中文互联网上关于「Codex 视频制作 Skills」的内容（抖音/知乎/公众号）时，需要快速对比 Hermes 的对应能力。

## 核心对比框架

所有 Codex Skills 本质上是 **SKILL.md 文件**——教 Codex（编程 Agent）怎么写代码来完成视频任务。
Hermes 的 Skill 则是 **直接干活**的——用户不需要写代码，直接下指令即可。

## 六个常见 Codex 视频 Skills

### ① HyperFrames（HeyGen 开源）
- **能力**：把文章/推文用 HTML+CSS+JS 写成动效场景，用浏览器引擎+FFmpeg 渲染成 MP4
- **GitHub**：HeyGen-Official/HyperFrames
- **Hermes 对标**：✅ `llm-video-maker` + `ai-video-full-pipeline`
- **优劣**：HyperFrames 动效酷炫；Hermes 更快（直接出片，不需要写 HTML）

### ② video-use（browser-use 出品）
- **能力**：真人素材自动剪辑——删停顿词、自动字幕、调色、30ms 淡入淡出
- **GitHub**：browser-use/video-use
- **Hermes 对标**：✅ `jianying-editor`
- **优劣**：video-use 纯 CLI；jianying-editor 利用剪映 GPU 渲染和中文生态

### ③ Remotion Skills（Remotion 官方）
- **能力**：用 React 写视频，代码即视频，支持批量/模板化生产
- **GitHub**：remotion-dev/skills（29 个 Agent Skill）
- **Hermes 对标**：⚠️ `ai-video-production`（Python+moviepy）
- **优劣**：Remotion 适合数据可视化/模板视频；moviepy 更适合口播/产品类

### ④ Generative Media Skills（SamurAIGPT）
- **能力**：封装调用 AI 模型（文生图、文生视频、文生音频）的操作规范
- **GitHub**：SamurAIGPT/Generative-Media-Skills
- **Hermes 对标**：⚠️ 有 `comfyui` skill 但未标准化封装
- **缺失**：一个「一句命令出高质量图/视频素材」的标准化 Skill

### ⑤ videocut-skills（Ceeon）
- **能力**：面向中文创作者的视频剪辑——中文字幕、竖屏短视频、口播精剪
- **GitHub**：Ceeon/videocut-skills
- **Hermes 对标**：✅ `jianying-editor`（更强——直接操控剪映桌面端）

### ⑥ seedance2-skill（dexhunter）
- **能力**：教 Codex 写即梦 Seedance 2.0 的专业视频提示词（镜头语言、运镜、分镜）
- **GitHub**：dexhunter/seedance2-skill
- **Hermes 对标**：❌ 没有
- **说明**：只负责提示词，不负责生成。如有需要可写一个类似 Skill。

## 推荐工作流（电商场景）

| 场景 | 推荐 Codex 组合 | Hermes 对标 |
|---|---|---|
| 文章/推文转视频 | HyperFrames | `llm-video-maker` |
| 真人口播精剪 | video-use + HyperFrames | `jianying-editor` |
| 数据视频/排行榜 | Remotion Skills | `ai-video-production` |
| AI 短剧/广告 | seedance2-skill + 即梦 + video-use | `jianying-editor` + `comfyui` |
| 批量测 AI 视频玩法 | Generative Media Skills | 缺标准化接口 |

## 检索关键词

用户问以下问题时关联此文档：
- "Codex Skills"、"Codex 视频"、"6个Skill"、"神级Skill"
- "HyperFrames"、"video-use"、"Remotion"、"Seedance"
- "videocut-skills"、"generative media"
- 任何「Codex 有什么 vs Hermes 能不能做」的问题
