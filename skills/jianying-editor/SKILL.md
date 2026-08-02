---
name: jianying-editor
description: 剪映 (JianYing) AI自动化剪辑的高级封装 API (JyWrapper)，提供开箱即用的 Python 接口，支持录屏、素材导入、字幕生成、Web 动效合成及项目导出。全面适配 MacOS (Apple Silicon/Intel) 与 Windows，支持 v5.9+ (draft_info.json) 架构、工程自修复、智能配音字幕及录屏变焦。
---

# JianYing Editor Skill

Use this skill when the user wants to automate video editing, generate drafts, or manipulate media assets in JianYing Pro.

Agent execution playbook: [docs/agent-playbook.md](docs/agent-playbook.md)
Minimal command SOP: [docs/minimal-command-sop.md](docs/minimal-command-sop.md)
Natural language usage guide: [usage.md](usage.md)
Draft inspector CLI:
`python <SKILL_ROOT>/scripts/draft_inspector.py list --limit 20`
`python <SKILL_ROOT>/scripts/draft_inspector.py summary --name "DraftName"`
`python <SKILL_ROOT>/scripts/draft_inspector.py show --name "DraftName" --kind content --json`
For generic editing requests, always follow the "Quick Edit Runtime Template" and "Acceptance Checklist" in that playbook.

## 🚨 重要开发原则 (CRITICAL DEVELOPER RULES)
1.  **脚本位置**：**禁止在 Skill 内部目录创建剪辑脚本**。所有的剪辑逻辑实现代码（`.py` 脚本）必须存放在用户当前项目的**根目录**（或子目录，如 `scripts/`），以保持 Skill 库的纯净和可移植性。
2.  **版本与架构**：
    - **双平台适配**：已全面支持 MacOS (路径探测/录屏) 与 Windows。
    - **Auto-healing**：支持 v5.9+ (`draft_info.json`)。若草稿损坏或版本冲突，使用 `overwrite=True` 初始化 `JyProject` 可触发自动修复。
3.  **配乐选择**：
    - **简单演示使用默认音乐**。实际项目，应优先检索并推荐 `data/cloud_music_library.csv` 中的相关曲目，或根据视频主题（如“科技”、“温暖”）进行关键词过滤。
    - 询问用户：“我发现了几首符合主题的云端音乐，要不要试试？（如：`Illuminate` - 科技感）”。

##  规则指南 (Rules)

Read the individual rule files for specific tasks and constraints:

- [rules/setup.md](rules/setup.md) - **Mandatory** initialization code for all scripts.
- [rules/core.md](rules/core.md) - Core operations: Saving, Exporting, and Draft management.
- [rules/cli.md](rules/cli.md) - CLI contracts and machine-readable output conventions.
- [rules/media.md](rules/media.md) - Importing assets & **AI Video Analysis Optimization (30m/360p)**.
- [rules/text.md](rules/text.md) - Adding Subtitles, Text, and Captions.
- [rules/keyframes.md](rules/keyframes.md) - **Advanced**: Adding Keyframe animations.
- [rules/effects.md](rules/effects.md) - Searching for and applying Filters, Effects, and Transitions.
- [rules/recording.md](rules/recording.md) - **New**: Screen Recording & Smart Zoom automation.
- [rules/web-vfx.md](rules/web-vfx.md) - Advanced: Web-to-Video generation.
- [rules/generative.md](rules/generative.md) - Chain of Thought for generative editing.
- [rules/audio-voice.md](rules/audio-voice.md) - **New**: TTS Voiceover & BGM sourcing.

## 🎯 Agent Quick Routing

### 批量剪辑 config.json 格式（合并自 jianying-batch-editor）

`~/Desktop/hermes/jianying_batch.py`（模板复制+JSON修改+meta同步一体）的配置格式：

```json
{
  "drafts": [
    {
      "name": "草稿名称", "width": 832, "height": 1108, "fps": 24,
      "videos": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
      "transitions": ["叠化", "模糊"],        // 逐段转场，可选
      "transition": "叠化",                    // 统一转场（transitions为空时用）
      "transition_duration": 0.5,
      "bgm": "/path/to/bgm.mp3", "bgm_volume": 0.25,
      "subtitle": "底部字幕文字", "subtitle_duration": 3
    }
  ]
}
```

**常用转场名**：`叠化`（通用柔和）/ `模糊`（产品展示）/ `闪白` `闪黑`（快节奏）/ `向左` `向右` `向上` `向下`（方向滑动）/ `旋转模糊` `缩放`（动感）/ `故障` `信号故障`（科技感）。完整列表见 pyJianYingDraft TransitionType 枚举。

**工作原理**：① 复制 TEMPLATE 目录（含剪映加密 meta）→ ② 视频素材复制到草稿内 `Resources/materials/` 解决沙盒权限 → ③ 写 draft_info.json（视频轨道+转场+BGM+字幕）→ ④ 同步 draft_meta_info.json + draft_info.json.bak → ⑤ 删 .locked 解锁 → 剪映内直接打开。

**常见问题**：「暂无访问权限/链接媒体」→ 脚本已自动复制视频到草稿内部目录，仍不行查文件路径；「草稿打开为空白」→ 检查 TEMPLATE 是否最新创建的空白草稿。

- 批量剪辑/多段拼接：用 `~/Desktop/hermes/jianying_batch.py`（模板复制+JSON修改，见 [references/direct-json-manipulation.md](references/direct-json-manipulation.md)）

- 云端视频 + 云端音乐：`rules/media.md` + `rules/audio-voice.md` -> `examples/cloud_video_music_tts_demo.py`
- 智能配音与字幕 (Script-to-Video)：`rules/text.md` + `rules/audio-voice.md` -> 核心 API `add_narrated_subtitles`
- 旁白与字幕对齐：`rules/text.md` + `rules/audio-voice.md` -> `examples/cloud_video_music_tts_demo.py`
- 录屏与智能变焦：`rules/recording.md` -> `tools/recording/recorder.py`
- 批量导出/无头导出：`rules/core.md` + `rules/cli.md` -> `examples/robust_auto_export.py`
- 影视解说生成：`rules/generative.md` -> `scripts/movie_commentary_builder.py`

## 📖 经典示例 (Examples)

Refer to these for complete workflows:
- [examples/my_first_vlog.py](examples/my_first_vlog.py) - A complete vlog creation demo with background music and animated text.
- [examples/simple_clip_demo.py](examples/simple_clip_demo.py) - Quick-start tutorial for basic cutting and track management.
- [examples/compound_clip_demo.py](examples/compound_clip_demo.py) - **New**: Professional nested project (Compound Clip) automation.
- [examples/cloud_video_music_tts_demo.py](examples/cloud_video_music_tts_demo.py) - Cloud video + cloud BGM + TTS/subtitle alignment.
- [examples/web_to_video_intro_demo.py](examples/web_to_video_intro_demo.py) - Web-to-Video intro demo (HTML animation -> timeline clip).
- [examples/robust_auto_export.py](examples/robust_auto_export.py) - Stable export workflow and failure handling.
- [examples/auto_exposure_align_demo.py](examples/auto_exposure_align_demo.py) - CV-assisted exposure alignment workflow.
- [examples/video_transcribe_and_match.py](examples/video_transcribe_and_match.py) - **Advanced**: AI-driven workflow (Transcribe Video -> Match B-Roll via AI semantics -> Assemble Draft).

## 🧠 提示词与集成工具 (Prompts & Integrated Tools)

Use these templates and scripts for complex tasks:
- **Asset Search**: Find filters, transitions, and animations by Chinese/English name:
  ```bash
  python <SKILL_ROOT>/scripts/asset_search.py "复古" -c filters
  ```
- **Movie Commentary Builder**: Generate 60s commentary videos from a storyboard JSON:
  ```bash
  python <SKILL_ROOT>/scripts/movie_commentary_builder.py --video "video.mp4" --json "storyboard.json"
  ```
- **Sync Native Assets**: Import your favorited/played BGM/Styles from JianYing App to the Skill:
  ```bash
  python <SKILL_ROOT>/scripts/sync_jy_assets.py
  # Index cloud materials from your existing drafts
  python <SKILL_ROOT>/scripts/build_cloud_music_library.py
  python <SKILL_ROOT>/scripts/build_cloud_text_styles_library.py
  ```
- **README to Tutorial**: Convert a project's README.md into a full installation tutorial video script:
  - Read prompt: `prompts/readme_to_tutorial.md`
  - Inject content into `{{README_CONTENT}}` variable
- **Screen Recorder & Smart Zoom**: Record your screen and auto-apply zoom keyframes:
  ```bash
  python <SKILL_ROOT>/tools/recording/recorder.py
  # Web preview capture (high performance)
  python <SKILL_ROOT>/scripts/web_recorder.py --url "http://localhost:3000" --duration 5
  # Or apply zoom to existing video:
  python <SKILL_ROOT>/scripts/jy_wrapper.py apply-zoom --name "Project" --video "v.mp4" --json "e.json"
  ```
- **Draft Inspector**: Examine draft structure and metadata (v5.9+ support):
  ```bash
  python <SKILL_ROOT>/scripts/draft_inspector.py list --limit 20
  python <SKILL_ROOT>/scripts/draft_inspector.py summary --name "DraftName"
  ```
- **Auto Exporter**: Headless export of a draft to MP4/SRT:
  ```bash
  python <SKILL_ROOT>/scripts/auto_exporter.py "DraftName" "output.mp4" --res 1080 --fps 60
  # For SRT only:
  python <SKILL_ROOT>/scripts/jy_wrapper.py export-srt --name "DraftName"
  ```
- **Template Clone & Replacer**: 安全克隆模板并批量替换物料 (防止损坏原模板):
  ```bash
  # 克隆模板生成新项目
  python <SKILL_ROOT>/scripts/jy_wrapper.py clone --template "酒店模板" --name "客户A_副本"
  ```
- **API Validator**: Run a quick diagnostic of your environment:
  ```bash
  python <SKILL_ROOT>/scripts/api_validator.py
  ```

## 🚀 快速开始示例

```python
import os
import sys

# 1. 环境初始化 (必须同步到脚本开头，支持 Win/Mac)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_root = os.getenv("JY_SKILL_ROOT", "").strip()
# 探测 Skill 路径 (支持 Antigravity, Trae, Claude 等)
skill_root = next((p for p in [
    env_root,
    os.path.join(current_dir, ".agent", "skills", "jianying-editor"),
    os.path.join(current_dir, ".trae", "skills", "jianying-editor"),
    os.path.join(current_dir, ".claude", "skills", "jianying-editor"),
    os.path.join(current_dir, "skills", "jianying-editor"),
    os.path.abspath(".agent/skills/jianying-editor"),
    os.path.abspath(".trae/skills/jianying-editor"),
    os.path.abspath(".claude/skills/jianying-editor"),
    os.path.abspath("skills/jianying-editor"),
    os.path.dirname(current_dir)
] if p and os.path.exists(os.path.join(p, "scripts", "jy_wrapper.py"))), None)

if not skill_root: raise ImportError("Could not find jianying-editor skill root.")
sys.path.insert(0, os.path.join(skill_root, "scripts"))
from jy_wrapper import JyProject

if __name__ == "__main__":
    # 2. 初始化工程 (支持 v5.9+ 及自修复)
    project = JyProject("New AI Video", overwrite=True)
    assets_dir = os.path.join(skill_root, "assets")

    # 3. 智能配音与字幕 (One-click Script-to-Video)
    project.add_narrated_subtitles(
        text="欢迎使用剪映自动化 Skill。这是一个全面适配 MacOS 的进阶版本。",
        speaker="zh_female_xiaopengyou"
    )

    # 4. 导入额外素材
    project.add_media_safe(os.path.join(assets_dir, "video.mp4"), "0s")
    project.add_media_safe(os.path.join(assets_dir, "audio.mp3"), "0s", track_name="Audio")

    # 5. 添加带动画的标题
    project.add_text_simple("剪映自动化开启", start_time="1s", duration="3s", anim_in="复古打字机")

    project.save()
```

## 🛠️ 初始化与项目规范 (Initialization & Project Rules)

在初始化 `JyProject` 时，请务必根据主视频素材的比例设置分辨率。**默认值为横屏 (1920x1080)**。

### 🚨 脚本存放位置规范
**禁止在 Skill 安装目录下创建你的业务剪辑脚本**。
- **正确做法**：将你的剪辑 Python 脚本放在项目的根目录（如 `~/Desktop/hermes/`）。
- **原因**：Skill 目录应该只包含工具集源码，便于后续 `git pull` 升级。业务代码混入会导致版本管理混乱。

### 📱 竖屏视频工作流（抖音带货/产品展示）
参考 [references/portrait-video-workflow.md](references/portrait-video-workflow.md) 中的完整示例。关键点：
- 初始化时显式指定 `width=832, height=1108`（或其他竖屏分辨率）
- 交叉淡化用 `add_transition_simple("crossfade", ...)`，不能靠 track 重叠
- 竖屏项目源文件放在 `~/Desktop/hermes/` 下

### 🚨 关键陷阱：JyWrapper 新建草稿可能打不开

**问题**：部分剪映 5.9.0 版本（VideoFusion-macOS）对 JyWrapper 用 `create_draft()` 生成的新草稿打开时报"暂无访问权限"。

**原因**：
- JyWrapper 的 `create_draft()` 从模板 JSON 生成纯结构，缺少剪映自己写入的元数据（如 `last_modified_platform` 中的设备ID、`draft_meta_info.json` 的专有字段）
- 这个版本的剪映能解析 JSON 但拒绝打开来源不明的草稿
- `.locked` 文件存在也会阻止打开

**推荐工作流（模板复制 + JSON 修改）**：
1. **一次性准备**：让用户在剪映 UI 中创建一个空白草稿，命名为 `TEMPLATE`（点"开始创作"→Ctrl+S→返回首页）
2. **后续全自动**：Agent 复制 TEMPLATE 目录 → 修改 `draft_info.json` 和 `draft_meta_info.json` → 同步 `.bak` → 删除 `.locked`
3. 用户打开同名草稿即可看到效果

**坑（已验证）**：
- 只改 `draft_info.json` 不更新 `draft_meta_info.json` → 剪映报"暂无访问权限" ❌
- 必须同步 `draft_id`、`draft_name`、`draft_fold_path`、`draft_materials`、`draft_timeline_materials_size_`、`draft_segment_extra_info`、`tm_duration`、`tm_draft_modified`
- `draft_info.json.bak` 也必须同步更新
- `.locked` 文件必须删除

**批量操作**：
可直接使用 `~/Desktop/hermes/jianying_batch.py`（模板复制+JSON修改+meta同步一体）：
```bash
# 一次配置，永久自动
python3 ~/Desktop/hermes/jianying_batch.py config.json
```
要求：剪映中存在 `TEMPLATE` 空白草稿。

具体实现参考：[references/direct-json-manipulation.md](references/direct-json-manipulation.md)

### 🔄 降级方案：JyWrapper 不可用时的 ffmpeg 直出

当剪映草稿方案不奏效时（格式不兼容、权限问题、路径错误），直接切换到 ffmpeg 管线：
- 使用 `xfade=transition=fade:duration=0.5:offset=X` 实现交叉淡化
- 多段拼接需要精确计算 offset = 前一段起点 + 前一段完整时长 - 重叠时长
- 参考 [references/ffmpeg-concat-workflow.md](../../content-creation/video-production-workflow/references/ffmpeg-concat-workflow.md)

**判断标准**：如果 JyProject 初始化成功、save() 成功，但剪映打开草稿报错（任何错误），直接切 ffmpeg 方案，不要反复调试 JyWrapper。

## ⚠️ macOS 兼容性：5.9 中文版 / CapCut 国际版

此 skill 主要为 **剪映专业版中文版（JianYingPro 5.9.0）** 设计。

### 剪映专业版 5.9.0（中文）
- App 路径: `/Applications/VideoFusion-macOS.app`
- Bundle: `com.lemon.lvpro`
- 草稿目录: `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/`
- 升级框架: 自研 HTTP 检查（无 Sparkle）
- **升级阻止**: 将以下域名写入 `/etc/hosts` 指向 `127.0.0.1`:
  - `lv-pc-api.bytedance.net`, `starling.bytedance.net`
  - `logvcapi.capcut.com`, `update-api.capcut.com`
- **完整兼容性参考**: [references/macos-capcut-compat.md](references/macos-capcut-compat.md)

### CapCut 国际版

| 问题 | 原因 | 解决 |
|------|------|------|
| 草稿路径不匹配 | skill 找 `~/Movies/JianyingPro Drafts/` | 手动指定路径或创建符号链接 |
| 自动导出可能失败 | auto-export 依赖剪映 5.9 或更低 | CapCut 手动打开草稿导出 |
| 草稿格式差异 | 国际版与中文版草稿 JSON 可能有字段差异 | 核心 API 通常可用，需实测 |

**在 CapCut 7.4.0 上：** `JyWrapper` 和 `pyJianYingDraft` 的导入验证通过，但未做完整端到端测试。
