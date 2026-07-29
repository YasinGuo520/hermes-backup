---
name: jianying-batch-editor
description: 剪映批量剪辑工具——从 TEMPLATE 草稿克隆，自动拼接视频、转场、BGM、字幕，解决沙盒权限问题。
---

# 剪映批量剪辑工具 (jianying-batch-editor)

## 适用场景

批量制作带货短视频、产品展示视频等重复性剪辑工作。

## 前置条件

1. 剪映专业版 5.9.0 已安装
2. 已创建名为 `TEMPLATE` 的空白草稿（点"开始创作"→直接保存→返回首页）
3. 视频素材文件路径正确

## 脚本位置

`~/Desktop/hermes/jianying_batch.py`

## Config 格式

```json
{
  "drafts": [
    {
      "name": "草稿名称",
      "width": 832,
      "height": 1108,
      "fps": 24,
      "videos": [
        "/path/to/video1.mp4",
        "/path/to/video2.mp4",
        "/path/to/video3.mp4"
      ],
      "transitions": ["叠化", "模糊"],        // 逐段转场，可选
      "transition": "叠化",                    // 统一转场（transitions为空时用）
      "transition_duration": 0.5,
      "bgm": "/path/to/bgm.mp3",              // 可选BGM
      "bgm_volume": 0.25,
      "subtitle": "底部字幕文字",
      "subtitle_duration": 3
    }
  ]
}
```

## 支持的转场名称

支持剪映全部转场，常用推荐：
- `叠化` — 通用柔和过渡
- `模糊` — 产品展示
- `闪白` / `闪黑` — 快节奏
- `向左` / `向右` / `向上` / `向下` — 方向滑动
- `旋转模糊` / `缩放` — 动感
- `故障` / `信号故障` — 科技感

完整列表见 pyJianYingDraft TransitionType 枚举。

## 使用

```bash
# 跑示例
python3 ~/Desktop/hermes/jianying_batch.py --demo

# 批量生产
python3 ~/Desktop/hermes/jianying_batch.py config.json
```

## 工作原理

1. 复制 `TEMPLATE` 目录（含剪映加密的 meta 文件）
2. 视频素材复制到草稿内 `Resources/materials/` 解决沙盒权限
3. 写 `draft_info.json`（视频轨道 + 转场 + BGM + 字幕）
4. 同步更新 `draft_meta_info.json` + `draft_info.json.bak`
5. 删除 `.locked` 解锁
6. ✅ 剪映内直接打开

## 常见问题

**"暂无访问权限" / "链接媒体"**
→ 脚本已自动将视频复制到草稿内部目录，如仍有问题需检查文件路径是否存在。

**草稿打开为空白**
→ 检查 `TEMPLATE` 是否是最新创建的空白草稿。
