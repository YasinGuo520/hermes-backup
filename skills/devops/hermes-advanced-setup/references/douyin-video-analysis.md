# 抖音视频分析工作流

Yasin 经常发 Douyin 链接让分析。标准流程：

## 步骤

1. **browser_navigate** 打开 Douyin URL（短链会自动 redirect 到 `www.douyin.com/video/{id}`）
2. 从页面 snapshot 中找 **章节要点**（`StaticText` 内，标记了时间戳的段落）；同时可读 赞/评/转/藏 统计数据、作者名/粉丝数、合集名、发布时间
3. 如果没有章节要点，搜索关键词找该视频的转载/解读文章
4. 深度分析（用户要"分析一下这个视频"时）：
   - 视频通常是**二次解读**，先识别它引用的原始素材（演讲/访谈/发布会的谁、什么场合）
   - 用 anysearch 搜原始演讲/访谈 → 拿**完整转录**（Root Access、BigGo Finance 等常带全文）
   - 基于原始全文分析核心论点，再核验视频转述是否失真（对比剪辑结论 vs 原文）
   - 输出：观点表（观点|原话/逻辑|可信度）+ 数据打折提醒（数据来源、样本偏差）+ 对 Yasin 处境的启示 + 今天能做的动作
5. 对比视频说的工具/观点 vs Hermes 已有能力
6. 输出结构化表格对比

## 工具兜底（2026-08 实测）

- `web_search` / `web_extract` 会挂：DuckDuckGo 后端限流超时（30s timeout）或 web_extract 报 "search-only backend cannot extract URL content"
- **兜底链**：`mcp__anysearch__search` + `mcp__anysearch__extract`（clean markdown、≤50K 字符、支持全文转录）——实测稳定可用，搜原始演讲/拉全文都走它
- web_extract 挂了不代表抓不到：anysearch 的 extract 是独立通道

## 关键点

- Douyin 页面笨重，不要尝试播放视频（`Video "Unable to play media"` 是正常的）
- 章节要点是最可靠的信息源，比评论/标题更准
- 评论区的工具名（如 HyperFrames、Remotion）可以辅助确认视频指向的具体项目
- 发布时间偏旧的视频（1个月+）可能是旧信息累积
- 视频引用原始素材的识别：标题常带人名（"Stripe创始人""YC演讲"），直接搜该人+场合+主题拿原始转录
