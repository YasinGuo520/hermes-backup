# 抖音视频分析工作流

Yasin 经常发 Douyin 链接让分析。标准流程：

## 步骤

1. **browser_navigate** 打开 Douyin URL（短链会自动 redirect 到 `www.douyin.com/video/{id}`）
2. 从页面 snapshot 中找 **章节要点**（`StaticText` 内，标记了时间戳的段落）
3. 如果没有章节要点，搜索关键词找该视频的转载/解读文章
4. 对比视频说的工具/观点 vs Hermes 已有能力
5. 输出结构化表格对比

## 关键点

- Douyin 页面笨重，不要尝试播放视频（`Video "Unable to play media"` 是正常的）
- 章节要点是最可靠的信息源，比评论/标题更准
- 评论区的工具名（如 HyperFrames、Remotion）可以辅助确认视频指向的具体项目
- 发布时间偏旧的视频（1个月+）可能是旧信息累积
