---
name: agent-reach
description: 联网信息检索与社交平台内容采集——从抖音/小红书/微博/知乎/B站等平台搜索和提取公开信息，用于市场调研、选品分析和竞品监控。
---

# Agent Reach（联网信息检索）

用于从互联网搜索和提取信息，做市场调研、选品分析、竞品监控。

## 能力范围

| 平台 | 能力 | 方式 | 限制 |
|------|------|------|------|
| 🌐 全网搜索 | 关键词搜索 + 网页内容提取 | web_search + web_extract | — |
| 📺 抖音 | 搜索视频/用户/话题 + 浏览器访问视频页 | web_search定向搜索 / browser_navigate（需Camoufox） | ⚠️ 文本搜索仅获摘要；但通过Camoufox可打开视频链接，从DOM读取完整标题/统计数据/章节要点/评论区。视频页可能弹CAPTCHA，如遇则停 |
| 📕 小红书 | 搜索笔记/商品 | web_search定向搜索 | — |
| 📖 知乎 | 搜索问答/文章 | web_search定向搜索 | — |
| 📦 GitHub | 仓库信息/README | web_search + web_extract | — |
| 📡 RSS | 订阅源内容 | web_extract | — |

## 限制说明

- **web_search + web_extract 无法处理 JS 渲染的页面**（如抖音商城、百应工作台等）。
- 抖音反爬极强：无登录时直接访问搜索页/商品页会跳验证码。但通过Camoufox浏览器直达视频详情页（`v.douyin.com/xxx`）可正常读取，包括标题、统计数据、章节要点、评论区。
- Camoufox访问抖音视频页**可能弹CAPTCHA**，此时诚实告知用户，不要反复重试或修工具。见 `references/douyin-video-analysis-via-camoufox.md`。
- **需要结构化商品数据的场景**（销量、价格、佣金率），建议使用 Playwright（skill: playwright-mcp）配合已登录的浏览器 session 来采集。
- 第三方数据平台（聚推客联盟、有米有数、蝉妈妈、飞瓜）的 API 均需注册/付费，无法通过简单 HTTP 请求免费获取。
- **⚠️ Douyin分享链接编码陷阱**：用户发的"1.23 :1pm JiP:/ 04/15 s@r.re"格式编码后无法提取视频ID。不要用搜到的近似视频代替原视频——搜到的可能是不同视频（内容/数量都不同）。详见 `references/douyin-inaccessible-video-reconstruction.md` → `关键陷阱` 章节。

## ⚠️ 使用前必读：用户分享了第三方平台链接

当用户分享**抖音/B站/小红书/微博等平台的链接**时，你必须先读对应参考文件再行动，不要先动手做任何事情：

1. **先读参考文件** — 立即用 `skill_view(name='agent-reach', file_path='references/<平台>-inaccessible-video-reconstruction.md')` 加载对应的重建指南
2. **确认Camoufox是否在运行** — `curl -s -o /dev/null -w '%{http_code}' http://localhost:9377/health`。200=可用，否则需先用 `CAMOFOX_DISABLE_DEFAULT_ADDONS=1 camofox-browser` 启动并等浏览器预热（~30s）
3. **试 `browser_navigate` 打开视频链接** — 如果弹出CAPTCHA或500错误，诚实告知用户打不开，要截图/描述
4. **只在访问成功时**才从页面提取数据。抖音章节要点已在DOM中，可用 `browser_snapshot` 读取
5. **铁律**：`browser_navigate` 返回CAPTCHA或500 = 停。直接问用户。不要换工具。不要绕路。

## 使用场景

- 竞品分析：搜"XX品牌 抖音 销量"了解对手
- 选品调研：搜"抖音 热销 收纳 2026"看趋势
- 口碑监控：搜"XX产品 测评 小红书"看用户评价
- 货源查找：搜"1688 XX品类 代发"找供应商
- 内容真实性鉴别：判断B站/小红书视频是真实分享还是推广引流/割韭菜内容（详见 ⭐ `references/bilibili-video-investigation.md`）
- **视频链接可达时的直接分析**：当Camoufox可用时，通过 `browser_navigate` 直接打开抖音视频链接提取完整数据（标题/统计/章节要点/评论区）。详见 ⭐ `references/douyin-video-analysis-via-camoufox.md`。
- **视频链接不可达时的内容重建**：当用户分享的抖音/B站/小红书链接因反爬/登录墙无法直接访问时，通过多源三角验证重建视频核心分析（详见 ⭐ `references/douyin-inaccessible-video-reconstruction.md`）

## AI Agent平台市场情报（Coze/Dify等围墙花园）

中国AI Agent开发平台（扣子Coze、Dify、百度秒哒等）的模板商店通常是 React SPA + 登录墙，web_extract抓不到完整数据，也没有公开的销量排行榜。

**策略：改为从二级来源反推市场热点**
- CSDN/火山引擎开发者社区 → 创作者分享的案例和销量数据
- B站教程 → 播放量反映模板方向的需求热度
- 淘宝/闲鱼 → 有人倒卖的模板反映真实市场需求

详见 ⭐ `references/ai-platform-market-intelligence.md`（完整方法论 + Coze模板市场关键发现）

## Python 抓取引擎选择

当需要写自定义爬虫脚本时，优先用 **scrapling**（已装 v0.4.11）而非 requests+bs4。

| 场景 | 推荐工具 | 理由 |
|:----|:--------|:----|
| 批量静态页面抓取 | `scrapling.StealthyFetcher` | 反检测指纹伪装，比 requests+bs4 省事 |
| 高并发批量抓取 | `scrapling.AsyncFetcher` | 异步并发，大批量快 |
| 需要 JS 渲染的单页 | `scrapling.DynamicFetcher`（或 Camoufox） | DynamicFetcher 轻量但不支持登录态；Camoufox 适合复杂登录场景 |
| DOM 解析/提取 | `scrapling.Selector` | 链式 CSS/XPath，比 bs4 简洁 |
| 社交平台（抖音/小红书等） | agent-reach 策略 + Camoufox | 平台有反爬策略和编码陷阱，有现成预案 |
| 登录后数据采集 | computer_use | 继承用户已登录浏览器 session |

**经验法则：** 无登录、无强反爬的任意网站 → scrapling。有反爬/编码陷阱的社交平台 → agent-reach 方法论 + Camoufox。需要登录态 → computer_use。

```python
# 典型搭配：agent-reach 策略定方向 → scrapling 执行
from scrapling import StealthyFetcher
f = StealthyFetcher()
page = f.fetch('https://example.com/items')
prices = [e.text for e in page.css('.price')]
```

## 进阶：登录后数据采集（computer_use）

对于需要登录的 JS 重型平台（如抖音百应工作台、蝉妈妈、飞瓜数据），可用 **computer_use** 操作用户已登录的浏览器直接提取数据：

1. 用户先在自己浏览器登录目标平台
2. 用 `computer_use(action='capture', app='Safari', mode='som')` 获取页面元素
3. 通过 SOM 索引点击导航到目标页面
4. 用 vision 或 SOM 解析提取结构化数据

详见 ⭐ `references/douyin-baiying-scraping.md` （抖音百应工作台精选联盟数据采集完整流程）

### 注意事项

- Playwright 不继承 Safari/Chrome 的登录 cookie，需要用户手动扫码
- 自定义 UI 控件（下拉箭头、筛选框等）可能不支持 AXPress，需改用 coordinate 点击
- 所有生成的 Excel 文件统一输出到 `~/Desktop/hermes/`
