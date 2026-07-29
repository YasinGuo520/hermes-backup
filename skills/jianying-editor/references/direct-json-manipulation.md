# 直接修改剪映 `draft_info.json` 工作流

当 JyWrapper 的 `create_draft()` + `save()` 生成的草稿在剪映中打不开时（显示"暂无访问权限"），使用此方案。

## 原理

剪映 UI 创建的草稿包含 JyWrapper 模板生成时遗漏的元数据（设备ID、app版本、特定字段值）。直接复用剪映创建的空白草稿，只修改 materials / tracks / duration 等关键内容，保留剪映自己的元数据。

**关键发现**：`draft_meta_info.json` 也必须同步更新，否则剪映会拒绝打开草稿！

## 标准流程

### Step 1：创建 TEMPLATE 空白草稿（只需一次）
```
用户在剪映中：点"开始创作" → 什么都不做 → Ctrl+S 保存 → 返回首页
命名：TEMPLATE
```

### Step 2：复制模板 → 修改 draft_info.json
复制整个 TEMPLATE 目录到新名字，然后修改 `draft_info.json`：

核心修改字段：
- `canvas_config.width` / `canvas_config.height` — 改为素材分辨率
- `fps` — 帧率
- `materials.videos` — 添加视频素材数组
- `materials.transitions` — 添加转场数组（多段拼接时）
- `materials.audios` — 添加 BGM（可选）
- `materials.texts` — 添加字幕（可选）
- `tracks` — 视频/音频/字幕轨道
- `duration` — 总时长（微秒）
- `update_time` — `int(time.time() * 1000000)`
- `id` — 生成新的 UUID v4 格式

### Step 3：同步更新 draft_meta_info.json ⚠️ 必做

**必须同步的字段：**

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `draft_name` | 草稿名 | `"Bra_产品A"` |
| `draft_fold_path` | 草稿文件夹绝对路径 | `".../draft/Bra_产品A"` |
| `draft_id` | 必须与 `draft_info.json` 的 `id` 一致 | UUID |
| `tm_duration` | 总时长（微秒） | `14488001` |
| `tm_draft_modified` | 当前微秒时间戳 | `int(time.time() * 1_000_000)` |
| `draft_timeline_materials_size_` | = `os.path.getsize(draft_info.json)` |
| `draft_materials` | 素材路径列表，按 type 分类 | 见下方 |
| `draft_segment_extra_info` | 每段的 `{"segment_id": id, "type": "video"}` |

**draft_materials 格式（7 种 type）：**
```python
[
  {"type": 0, "value": ["/path/vid1.mp4", "/path/vid2.mp4"]},  # video
  {"type": 1, "value": ["/path/bgm.mp3"]},                     # audio
  {"type": 2, "value": []},                                    # text
  {"type": 3, "value": []},                                    # image
  {"type": 6, "value": []},                                    # effect
  {"type": 7, "value": []},                                    # transition
  {"type": 8, "value": []},                                    # filter
]
```

### Step 4：同步 draft_info.json.bak
```python
shutil.copy2(info_path, os.path.join(target_path, "draft_info.json.bak"))
```

### Step 5：解锁
删除 `.locked` 文件

### Step 6：用户打开查看
关闭剪映重开，新草稿会出现在列表中

## 多段视频 + 交叉淡化

三片段、两个 0.5s 交叉淡化：

| 片段 | 素材 | target_start | target_duration |
|------|------|-------------|-----------------|
| seg1 | video1.mp4 | 0 | 5042000 (全片) |
| seg2 | video2.mp4 | 4542000 (5042000-500000) | 5042000 |
| seg3 | video3.mp4 | 9084000 (4542000+5042000-500000) | 5042000 |

转场添加在 `materials.transitions` 中，每项含 `segment_ids` 指向需要加转场的片段。

总时长 = 5042000 + 5042000 + 5042000 - 2*500000 = 14126000 微秒 (14.13s)

## 批量操作脚本

推荐直接使用 `~/Desktop/hermes/jianying_batch.py`，它封装了整个流程：

```bash
# 创建配置文件 my_batch.json
{
  "drafts": [
    {
      "name": "产品A",
      "width": 832, "height": 1108, "fps": 24,
      "videos": ["/path/to/v1.mp4", "/path/to/v2.mp4"],
      "transition": "crossfade",
      "transition_duration": 0.5,
      "bgm": "/path/to/bgm.mp3",
      "subtitle": "底部文字",
      "subtitle_duration": 3
    }
  ]
}

# 执行
python3 ~/Desktop/hermes/jianying_batch.py my_batch.json
```

脚本要求：
- 必须存在名为 `TEMPLATE` 的空白草稿
- 视频路径必须是**绝对路径**
- ffprobe 必须可用（自动获取视频时长和分辨率）

## 验证清单

修改后用以下步骤验证：
1. `draft_name` 是否匹配
2. `draft_id` 两文件是否一致
3. `.locked` 是否已删除
4. `draft_info.json.bak` 内容与 `draft_info.json` 一致
5. `draft_timeline_materials_size_` = `draft_info.json` 文件大小

## 降级方案

若剪映草稿方案仍不奏效，直接切换到 ffmpeg 管线：
```bash
ffmpeg -i v1.mp4 -i v2.mp4 -i v3.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=4.66[t];
                   [t][2:v]xfade=transition=fade:duration=0.5:offset=9.32[out]" \
  -map "[out]" -c:v libx264 -crf 18 output.mp4
```
