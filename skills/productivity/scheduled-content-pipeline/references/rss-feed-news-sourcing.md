# RSS-First News Sourcing（2026-08-30 实战验证）

## 触发场景
- DDG web_search 超时；AnySearch MCP tool_call 链路连续报 "arguments is not valid JSON"（本次实测 9 次）
- 此时不要死磕搜索API / browser（Cloudflare直挡），**直接 curl RSS feeds 拿新鲜料**，10秒内有结果

## 已验证可直连的 RSS 端点（服务器 curl 无 UA 即可）
| 源 | URL | 备注 |
|----|-----|------|
| OpenAI 官方 | https://openai.com/news/rss.xml | **HTML页被Cloudflare挡，但RSS端点可直连**（2026-08-30推翻旧结论）|
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/feed/ | 标题+链接+pubDate+description 齐 |
| The Verge AI | https://www.theverge.com/rss/ai-artificial-intelligence/index.xml | Atom格式，entry标签 |
| Hacker News 首页 | https://hnrss.org/frontpage | 每天最早出新料，跨领域 |
| Bing RSS 兜底搜索 | https://www.bing.com/search?q=<query>&format=rss | 带UA，返回XML；中文query也行，但命中质量一般 |

## 解析（python 正则处理 CDATA，兼容 item/entry 两种 RSS）
```python
import sys, re, html
t = sys.stdin.read()
items = re.findall(r'<(item|entry)>(.*?)</\1>', t, flags=re.S)
for tag, it in items:
    title = re.search(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', it, flags=re.S)
    link = re.search(r'<(link[^>]*href="[^"]+|link)>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>', it, flags=re.S)
    pub = re.search(r'<(pubDate|published)[^>]*>(.*?)</\1>', it, flags=re.S)
    if title:
        print('-', html.unescape(title.group(1))[:130])
        if link: print('  ', link.group(1))
        if pub: print('  ', pub.group(2))
```

## 怎么用来写英语每日一练
1. 并行 curl 2-3 个 feed（OpenAI官方 + TechCrunch + HN），取 pubDate 最新的 2-3 条候选
2. RSS 的 title + description 已够判断主题是否新鲜（例：OpenAI "Our decision on Cursor following its acquisition by SpaceX"）
3. 重磅事件若有官方 RSS 描述即可作事实基础；需要更多细节再抓正文（paywall/CF挡就放弃正文，用多源拼）
4. 反 clickbait：只认权威媒体 + 官方 RSS 里出现的标题，LinkedIn/Medium 类一律丢弃

## 当日走通案例（2026-08-30）
- 主题：OpenAI cuts off Cursor after SpaceX acquisition（收购后终止模型供应合同）
- 来源：openai.com/news/rss.xml 官方公告（Fri, 28 Aug 2026），链接 https://openai.com/index/our-decision-on-cursor-following-its-acquisition-by-spacex
- Cloudflare 挡正文（curl 和 browser 均 "Just a moment..."），但官方 RSS description 已含核心事实，直接支撑英文介绍