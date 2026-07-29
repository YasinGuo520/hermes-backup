# 竖屏视频编辑工作流

## 适用场景
抖音带货短视频、内衣/时尚产品展示、竖屏商品详情视频

## 典型工作流

```python
import os, sys
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/jianying-editor/scripts"))
from jy_wrapper import JyProject

PROJECT_NAME = "项目名"
VIDEOS = [
    "/Users/mac/Desktop/hermes/chaoke_bra_video.mp4",
    "/Users/mac/Desktop/hermes/chaoke_bra_v2_pan_up.mp4",
    "/Users/mac/Desktop/hermes/chaoke_bra_v3_turn.mp4",
]

# 竖屏必须显式指定分辨率
project = JyProject(PROJECT_NAME, width=832, height=1108, overwrite=True)

# 逐个添加视频
segments = []
for vpath in VIDEOS:
    seg = project.add_media_safe(vpath, track_name="VideoTrack")
    if seg:
        segments.append(seg)

# 添加交叉淡化转场
if len(segments) >= 2:
    project.add_transition_simple("crossfade", video_segment=segments[0], duration="0.5s")
    project.add_transition_simple("crossfade", video_segment=segments[1], duration="0.5s")

result = project.save()
print(f"草稿已保存: {result['draft_path']}")
```

## API 速查

| 操作 | 代码 | 说明 |
|------|------|------|
| 初始化 | `JyProject("name", width=832, height=1108, overwrite=True)` | 竖屏必须设分辨率 |
| 加视频 | `add_media_safe(path, track_name="VideoTrack")` | 返回 segment 对象 |
| 加音频 | `add_media_safe(path, track_name="Audio")` | 自动识别音频文件 |
| 加文字 | `add_text_simple("文字", start="0s", duration="3s")` | 默认进入轨道末尾 |
| 交叉淡化 | `add_transition_simple("crossfade", video_segment=seg, duration="0.5s")` | 附着在 segment 上 |
| 保存 | `save()` | 返回 `{"draft_path": "..."}` |

## 注意事项

1. **视频 track 不能重叠**，交叉淡化用 transition API，不能靠叠放
2. **文字 track 也不能重叠**，同一时间多条文字用 `\n` 换行
3. **脚本必须放在项目目录**（如 `~/Desktop/hermes/`），不能放 skill 目录
4. **剪映要刷新才能看到新草稿**：切到其他草稿再回来，或重启
5. **自动导出仅支持 Windows**，Mac 上用剪映手动导出
