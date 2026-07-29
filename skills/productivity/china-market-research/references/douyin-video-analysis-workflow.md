# 抖音/中文短视频内容提取与分析工作流

## 问题背景

抖音（Douyin）网页版对自动化/非浏览器访问有极强的 bot 检测机制：
- curl/web_extract → ❌ 拦截或空内容
- 浏览器 navigate → ⚠️ 页面加载但视频不播放，显示"视频数据加载中"
- 页面的 AX 树内容极有限，推荐内容淹没了核心信息

## 成功工作流（已验证 2026年7月）

### Phase 1: 多通道获取基础信息

```text
渠道1: 浏览器导航
  browser_navigate(url="https://v.douyin.com/短链/")
  → 自动重定向到 www.douyin.com/video/视频ID
  → 页面加载，但视频内容被 bot 检测拦截不播放

渠道2: 截图 + 视觉分析 (可靠主路径)
  browser_vision(question="视频标题、作者、数据等")
  → 即使视频不播放，页面的标题文本、作者信息、播放控件通常仍可读
  → 返回分析结果含：视频标题、作者名、粉丝数、时长、推荐列表

渠道3: browser_console 提取 HTML meta（vision 失败时的降级路径）
  browser_console(expression='document.title')
  → 直接返回页面标题（含话题标签）
  browser_console(expression='document.querySelector(\'meta[name="description"]\')?.content')
  → 返回 meta 描述，含作者名、发布时间、点赞数、完整话题标签
  优势：不依赖视觉模型，即使 browser_vision 报错也能获取核心信息
  PS：截图仍可使用（screenshot_path 可用 MEDIA: 发送给用户）

渠道4: AnySearch 搜索话题上下文（页面内容不可读时）
  mcp__anysearch__search(query="OpenClaw 小龙虾 AI agent")
  → 当视频页面被 bot 锁定（不播放、无内容），用视频的 hashtag/topic 做 AnySearch
  → 搜索结果会显示 OpenClaw 是什么、同类视频、行业背景
  → 让你即使没看到视频内容，也能从生态层面理解它在讲什么

渠道5: 批量多角度搜索
  batch_search([不同关键词组合])
  → 消除单一搜索的噪音
```

### Phase 2: 信息提取内容清单

从抖音页面试图提取以下信息：

| 信息 | 提取方式 | 成功率 |
|:---|:---|:---:|
| 视频标题 | browser_vision 截图分析 | ✅ 高 |
| 视频字幕/关键帧文字 | browser_vision 截图分析 | ✅ 高 |
| 作者名 + 头像 | browser_vision 截图分析 | ✅ 高 |
| 粉丝数/获赞数 | browser_vision 截图分析 | ✅ 中（有时被截断） |
| 视频时长 | 页面 AX 树可读 | ✅ 高 |
| 推荐视频列表 | browser_vision 或 browser_snapshot | ✅ 高 |
| 视频评论区 | ❌ bot 检测下通常不可用 | ❌ 低 |
| 搜索框当前关键词 | 页面 AX 树可读 | ✅ 高（页面复用状态） |

### Phase 3: 跨平台身份三角验证

抖音单一信源不足以确认创作者身份，需跨平台验证：

```text
1. 抖音 → 拿到创作者名 + 视频主题
2. Zcool(站酷) → 搜索设计师/3D创作者作品集
3. 个人网站(shi-weili.com 等) → 专业背景
4. B站 → 长内容深度分析
5. AnySearch + batch_search → 多维度搜索结果交叉验证
```

### Phase 4: 内容分析框架

对提取到的视频内容，结构化分析：

```
类别: 案例拆解 / 产品演示 / 教程 / 观点输出
核心叙事: 一句话概括视频要传达的信息
目标受众: 谁在看这个视频
变现模式: 引流私域/带货/知识付费/广告
可借鉴点: 他的方法对你有什么启发
风险提示: 哪些不能照搬
```

## 常见坑

1. **不要只用一个渠道** — 抖音 bot 检测随时变化，截图可能不完整或已被刷新成其他内容
2. **搜索框残留词不要信** — 浏览器可能保留了用户之前的搜索词，那不代表当前视频相关
3. **多次 navigate 可能触发更严检测** — 尽量一次加载后直接截图
4. **评论区内容极难获取** — 抖音对评论区做了强反爬，不用在此浪费轮次
5. **粉丝数可能显示不全** — 截图显示的是 "2895" 或 "1..."（截断），结合其他渠道补全
