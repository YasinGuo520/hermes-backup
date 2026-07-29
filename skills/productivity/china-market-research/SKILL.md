---
name: china-market-research
description: 中国市场调研——搜索中文互联网获取商业情报、产品案例、市场规模数据。覆盖百度/搜狗/360 反爬绕过、中文信息源、Python 提取技术、产品发现方法论。
---

# 中国市场调研 Skill

当用户要求调研**中国市场**的某一商业方向（SaaS/APP/小程序/创业机会/市场规模/竞品），且需要从中文互联网获取信息时，使用本 Skill。

## 核心原则

1. **搜索引擎反爬极其严重**：百度（桌面+mobile）、搜狗、360、知乎均已 captcha 封锁 curl/非浏览器访问。Baidu Mobile UA curl 方案已基本失效（返回 30 字符空白或 captcha 页面）。不要依赖 curl 直接搜索。
2. **Bing 国内版 (cn.bing.com) 不可用**：中文/英文搜索均只返回搜索框+导航栏，无搜索结果。域名策略导致国际版也被重定向回国内版。不要在此浪费轮次。
3. **36氪搜索 → 文章详情提取 是唯一可靠主路径**：36氪对创业/SaaS/消费/科技/AI 类内容覆盖极好。但搜索接口不稳定，部分长关键词+空格组合搜索返回空页面。
4. **"36氪搜索页→提取文章URL→直接访问文章页"是已验证的成功链路**。推荐使用浏览器工具（browser_navigate + browser_console）但需注意：36氪搜索页 URL `36kr.com/search/articles/关键词` 有时返回空，即使看似正确的关键词也会不给结果。此时可尝试不同关键词组合或简化。
5. **浏览器工具 (browser_navigate + browser_console JS) 优于 curl 直搜**：浏览器可处理部分 captcha 验证，且浏览器控制台（browser_console with expression）可提取动态加载的页面元素、文章链接等。
6. **多次短查询优于单次长查询**：2-4 个关键词一组的短查询返回最相关结果。关键词中含空格或 `+` 号往往返回空。
7. **用 Python urllib + 浏览器 User-Agent 提取 36氪文章**：`<p>` 标签中的纯文本可直接提取，`__NUXT__` 变量中也可能包含完整文章内容。
8. **直接访问产品官网**往往比搜索更有效。

## 调研步骤

### 第一步：确定搜索关键词

生成 8-12 个短关键词（每组 2-4 个词），覆盖：
- **产品类关键词**：产品名 + APP/小程序/SaaS/平台
- **行业类关键词**：方向 + 市场/规模/报告/用户数
- **商业模式类**：产品 + 营收/融资/付费/商业模式
- **竞品类**：方向 + 头部/排名/对比

### 第二步：[弃用] 百度搜索（Mobile UA）

> ⚠️ **2025-2026 年起此方案已基本失效**。百度所有域名均已部署严格 captcha，curl 返回空内容（约 30 字符）或 captcha 页面。保留以下代码供历史参考，但不应作为主方案。

```bash
# 历史方案：curl + Android UA（目前已不可用）
curl -s -L --max-time 10 \
  -H "User-Agent: Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36" \
  "https://www.baidu.com/s?wd=<URL编码关键词>&rn=5"
```

**替代方案**：直接跳到第五步，使用 36氪浏览器调研工作流。

### 第三步：解析结果

```python
import re
html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
text = re.sub(r'<[^>]+>', ' ', html_clean)
text = re.sub(r'\s+', ' ', text)
# 提取含数字的句子（潜在数据点）
data_points = re.findall(r'[^。]*?(?:亿|万|千万|%|元|用户|营收|收入|融资)[^。]*[。]', text)
```

### 第四步：备选信息源

| 来源 | URL | 状态 | 绕过方式 |
|:---|:---|:---:|:---|
| 百度（桌面） | baidu.com | ❌ captcha | 不可用，各种 UA 均 captcha |
| 百度 Mobile | m.baidu.com | ❌ 已失效 | curl + Android UA 返回 30 字符空白；浏览器访问也 captcha |
| 搜狗 | sogou.com | ❌ captcha | 不推荐 |
| 360 | so.com | ❌ captcha | 不推荐 |
| **Bing 中国** | cn.bing.com | ❌ **完全不可用** | 同时报 blocked 或无搜索结果；国际版被重定向回国内版 |
| **36氪搜索页** | 36kr.com/search/articles/关键词 | ✅ 推荐入口（有坑） | 浏览器直接访问；部分关键词返回空，需尝试不同组合 |
| **36氪文章详情** | 36kr.com/p/文章ID | ✅ **最佳信源** | curl/浏览器均可；`<p>` 标签可提取正文 |
| **AI工具集** | ai-bot.cn | ✅ 可用 | AI 产品导航，可发现新锐产品 |
| 人人都是产品经理 | woshipm.com | ⚠️ 动态渲染 | 需浏览器/无头模式 |
| 知乎 | zhihu.com | ❌ captcha | 不推荐，几乎必触发 |
| 直接访问官网 | 产品.com | ✅ 可靠 | curl 直接访问 |

### 第五步：直接访问产品官网

对已知产品，跳过搜索直接访问官网获取产品信息：

```python
import requests
headers = {'User-Agent': 'Mozilla/5.0 ...'}
r = requests.get('https://www.产品名.com/', headers=headers, timeout=10)
```

### 第五步延伸：36氪浏览器调研工作流（推荐，已验证可靠）

当 curl 搜索全部失效时，使用浏览器工具按以下步骤操作：

```python
# 1. 用 browser_navigate 访问 36氪搜索页
# URL = https://www.36kr.com/search/articles/关键词
# 注意：关键词需 URL 编码，不要用空格

# 2. 获取搜索结果中的文章 URL
# 用 browser_console 执行 JS 提取链接：
"""javascript
let links = document.querySelectorAll('a[href*="/p/"]');
let result = [];
links.forEach(a => {
  if (a.href && a.href.includes('/p/') && a.textContent.trim()) {
    result.push(a.textContent.trim().substring(0,80) + ' | ' + a.href);
  }
});
result.slice(0,15).join('\\n');
"""

# 3. 用 browser_navigate 直接访问文章详情页
# URL = https://www.36kr.com/p/文章ID

# 4. 使用 browser_snapshot(full=true) 读取文章全文
# 36氪文章详情页对浏览器友好，内容直接渲染在页面中
```

**注意**：36氪搜索页有时返回空页面（即使关键词看似正确）。此时要么尝试不同关键词组合，要么直接从已知热门文章开始。36氪文章详情页（/p/文章ID）从不会返回空。

### 第六步：Bing 已不可用时的替代方案

如果确实需要竞品发现，除 36氪外还可尝试：
- **AI工具集** (ai-bot.cn) — AI 产品导航网站，可按类别浏览 AI 产品
- **抖音/小红书**搜索 — 输入产品名查看用户反馈和投放情况
- **天眼查/企查查** — 查看公司融资和竞品信息（需登录）
- **Product Hunt** (producthunt.com) — 发现全球新产品（需要会上网）

### 第六步：已知中文产品参考

#### 情感/约会方向
- 他趣 (taqu.com) — 兴趣交友陪聊，2亿+用户
- 爱聊 (ailiao) — 情感社交，2亿+注册
- 探探 (tantanapp.com) — 滑动匹配交友，3亿+注册
- Soul (soulapp.cn) — AI+兴趣社交，1亿+MAU，已上市
- 珍爱网 (zhenai.com) — 传统婚恋
- 世纪佳缘 (jiayuan.com) — 传统婚恋
- 闪恋教育（暖山文化）— 男性恋爱培训
- 阿尔法恋爱学校 — 约会技巧培训

#### 女性爱美/医美方向
- 睿美云 (36氪报道) — 医美SaaS，超千万元A轮融资，市占率5%+，续费率90%+
- 领健 (36氪报道) — 消费医疗SaaS（口腔+医美），D轮+D+轮超1亿美元
- 有赞/微盟 — 通用电商SaaS，美业门店大量使用
- 码云数智 — 小程序SaaS，基础版年费1998元，适合中小门店

#### 母婴/育儿方向
- 宝宝树 — 母婴社区+电商（上市后衰退）
- 亲宝宝 — 宝宝成长记录APP
- 小步在家早教 — 亲子教育平台
- 年糕妈妈 — 母婴内容电商
- 妈妈网 — 孕期+育儿社区

#### 女性情感/心理方向
- 壹心理 — 专业心理咨询平台
- 简单心理 — 心理咨询师平台
- 松果倾诉 — 匿名情感倾诉
- Soul — AI+兴趣社交，1亿+MAU，已上市

#### 小红书生态工具
- 新红数据 — 小红书数据分析，年营收5000万+
- 千瓜数据 — 小红书数据分析，年营收5000万+
- 零克查词 — 笔记合规检测
- 小红书聚光平台 — 官方广告投放工具

#### 赚钱/投资方向
- 同花顺 (10jqka.com.cn) — 炒股工具，1亿+注册
- 东方财富 (eastmoney.com) — 综合金融
- 雪球 (xueqiu.com) — 投资社区
- 猪八戒网 (zbj.com) — 服务外包
- 知识星球 (zsxq.com) — 付费社群
- 小鹅通 (xiaoe-tech.com) — 知识付费SaaS

## 常见陷阱

1. **高级搜索词反而不出结果**：太长的中文搜索词常返回空结果（尤其是含 `+` 号的），用短词（2-3个）+逐步迭代。36氪搜索对含空格的复杂关键词尤为挑剔。
2. **Baidu mobile 已基本不可用**：curl + Android UA 曾是最可靠方案，但 2025-2026 年起所有百度的域名都部署了严格 captcha，curl 返回 30 字符空白内容，浏览器访问也直接跳转 captcha 页面。不要在此浪费时间。
3. **Bing 国内版 (cn.bing.com) 完全不可用**：不仅是内容过滤，而是根本返回不了搜索结果。域名策略强制国内用户使用受限版本，国际版搜索也被重定向。**Bing 不再是一个有效信息源。**
4. **36kr 搜索页不稳定**：只能覆盖科技/创业/消费/SaaS 类话题；母婴/情感/育儿/教育类关键词通常会返回"没有找到相关结果"。即使能搜索的话题，部分长关键词组合也返回空页面。需要不断试不同关键词。
5. **36氪文章详情页可靠**：只要知道文章ID（从搜索页或其他渠道获取），详情页（/p/文章ID）对浏览器和 curl 均友好，不会触发 captcha。
6. **浏览器 console JS 提取链接是关键词：** 在 36氪搜索结果页无法直接获取文章 URL 时，使用 `browser_console` 执行 `document.querySelectorAll('a[href*="/p/"]')` 可以提取所有文章链接。
7. **误判过滤结果**：中国搜索引擎对敏感内容（PUA/情感陪聊灰色地带）有过滤，搜索结果可能不完整。
8. **国际站点超时**：从中国服务器访问 Google/Wikipedia 经常会超时，不要依赖。

## 抖音/中文短视频内容提取

当调研对象的信息存在于抖音/小红书等中文短视频平台时，见 `references/douyin-video-analysis-workflow.md`。

核心思路：browser_vision 截图分析（绕过 bot 检测）+ browser_console 提取 HTML meta（vision 降级）+ AnySearch 跨平台搜索（Zcool/站酷/B站/话题上下文）→ 三角验证创作者身份 → 结构化分析。

## B站视频内容分析

当信息源是B站视频时，见 `references/bilibili-video-analysis.md`。

流程：
1. B站API获取元数据（title/desc/duration/stats）
2. 浏览器加载页面获取描述+标签+章节+热评
3. 交叉搜索补充信息
4. 结构化输出「可借鉴点 + 适配度判断」

核心技巧：API限频时走浏览器路线；描述太短时结合评论区补全；关注up主其他平台内容交叉验证。

## 输出格式

写完调研内容后，保存为结构化 Markdown 报告。建议包含：
- 执行摘要 / 核心结论（表格优先）
- 具体产品案例（名称+类型+规模+商业模式+收入估算）
- 市场规模数据及来源
- 竞争格局分析
- 风险提示
- 下一步行动建议
