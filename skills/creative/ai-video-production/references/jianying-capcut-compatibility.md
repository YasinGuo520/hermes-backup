# 剪映/CapCut 草稿路径兼容性说明

## 四个版本四种路径

| 版本 | 安装名 | 草稿根目录 | skill兼容性 |
|------|--------|-----------|------------|
| **剪映专业版 5.9** (skill推荐版) | 剪映专业版.app | `~/Movies/JianyingPro Drafts/` | ✅ 完全兼容，自动导出可用 |
| **剪映专业版 7.x** (中文新版) | VideoFusion-macOS.app | `~/Library/Containers/com.lemon.lvpro/Data/…/JianyingPro/User Data/Projects/com.lveditor.draft/` | ⚠️ 核心API可用，自动导出不可用 |
| **剪映专业版 10.x+** (最新中文版) | VideoFusion-macOS.app | `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/` | ❌ **完全不兼容。draft_info.json已加密（二进制/非JSON），pyJianYingDraft无法解析** |
| **CapCut 7.x** (国际版) | CapCut.app | `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/` | ❌ 草稿格式与中文版不兼容 |

## 关键发现

1. **剪映≥10.x 加密了 draft_info.json**。不再是明文JSON，无法被pyJianYingDraft读取。
   - 实测 10.7.0 版：`draft_info.json` 内容为纯二进制乱码，JSON解析直接报错。
   - **任何剪映版本≥10.x都无法使用 jianying-editor-skill。** 只能降级到5.9或更早版本。
2. **CapCut国际版 的草稿格式与 剪映中文版 不兼容。** skill生成的草稿在CapCut国际版中打开异常。
3. **剪映中文版 7.4.0** 核心API可用（创建项目、导入素材、加文字）。自动导出功能需要5.9或更低。
4. **pyJianYingDraft库** 在7.4.0上可以正常工作。需要设置 `JY_SKILL_ROOT` 环境变量。

## 测试命令

```python
import os, sys
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/jianying-editor/scripts"))
os.environ["JY_SKILL_ROOT"] = os.path.expanduser("~/.hermes/skills/jianying-editor")

from jy_wrapper import JyProject

# 剪映中文版7.x沙箱路径
drafts_root = os.path.expanduser(
    "~/Library/Containers/com.lemon.lvpro/Data/Documents/Users/mac/"
    "Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
)

proj = JyProject(project_name="test_draft", width=832, height=1108,
    drafts_root=drafts_root, overwrite=True)
proj.add_media_safe(video_path, start_time="0s", duration="3s", track_name="VideoTrack")
proj.add_text_simple("标题文字\n副标题", start_time="0.5s", duration="2.5s", anim_in="淡入")
proj.save()
```

## 何时用哪个

- **快速出片（≤30条/天）** → ffmpeg两段法（CRF18，5500kbps，¥0.18/条）
- **需要花字/特效/专业转场** → 剪映中文版5.9 + jianying-editor-skill
- **手上只有剪映10.x+** → 放弃skill，走ffmpeg管线。找5.9旧版覆盖安装可恢复兼容。
