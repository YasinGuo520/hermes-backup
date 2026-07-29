# Douyin / 抖音短视频内容提取

抖音网页版不提供公开字幕/转录 API，且视频页面强制登录弹窗。以下是在国内网络环境下提取抖音视频内容的已验证工作流。

## 流程

### 第一步：浏览器访问

```python
browser_navigate(url="https://v.douyin.com/xxx/")
```

Camofox 会自动解析短链接。页面加载后会弹出登录框。

### 第二步：截图提取元数据

```python
browser_vision(question="提取视频标题、作者、话题标签、时长、点赞数等可见信息")
```

从截图可获得：
- 视频标题和话题标签
- 作者名和粉丝数
- 点赞/评论/收藏/分享数据
- 时长和章节标记（如有）

### 第三步：搜索补充材料

当登录墙阻挡了完整视频内容时，用提取到的标题+作者名搜索：

```python
web_search(query="视频标题 关键词 作者")
```

目标：
- 找同主题的 GitHub 指南 / 知乎文章 / 博客（这些通常有完整文字版）
- 找作者在其他平台（B站/YouTube/知乎）的同一内容

### 第四步：合成摘要

将视频元数据（标题/标签/统计数据）与搜索到的文字内容合并，形成完整摘要。在 frontmatter 标注 `synthesized: true`。

### 第五步：关联思维导图

如果视频内容有清晰层次结构（如编号路径、难度排名、分类对比），调用 `mind-map` skill 生成 `.mm` 文件并存到 `raw/assets/`。

## 已知限制

- 无法获取逐字字幕/逐帧文本
- 搜索结果可能与视频原内容有偏差（不同平台版本不同）
- 需要提前启动 Camofox：`cd ~/.local/lib/node_modules/@askjo/camofox-browser && node server.js`

## 平台对比

| 平台 | 字幕可获取 | 替代方案 |
|------|-----------|---------|
| YouTube | ✅ 完整字幕（youtube-transcript-api） | 直接提取 |
| Bilibili | ✅ 有 API 可获取 CC 字幕 | bilibili-api |
| 抖音 | ❌ 无公开字幕 API | 上述合成法 |
| 小红书 | ❌ 无公开字幕 API | 类似合成法 |
