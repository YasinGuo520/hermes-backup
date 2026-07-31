---
name: web-scraping
description: 数据采集首选方案——Scrapling 优先，Playwright 备选。覆盖反爬绕过、自适应选择器、定时爬虫配置。
---

# Web Scraping（数据采集）

**首选工具：Scrapling**（v0.4.11+，已安装）
**备选：** Playwright（见 `playwright-mcp` skill，用于需要手动登录的浏览器自动化场景）

## 选型决策

```
要爬的东西 → 需要登录/交互吗？
  ├── 否 → Scrapling（StealthyFetcher / Fetcher）
  └── 是 → 需要浏览器操作吗？
        ├── 否（仅 cookie 登录）→ Scrapling（FetcherSession）
        └── 是 → Playwright（见 playwright-mcp skill）
```

## Scrapling 安装（已就绪）

```bash
pip3 install scrapling --break-system-packages
```

当前版本：v0.4.11
依赖：lxml, cssselect, orjson, w3lib, tld, playwright（可选）

## 基本使用模式

### 1. 快速抓取（静态页面 / XHR 数据）

```python
from scrapling.fetchers import Fetcher

page = Fetcher.fetch('https://example.com/api/data')
print(page.status)  # 200
items = page.css('.item')
for item in items:
    print(item.text)
```

### 2. 绕过 Cloudflare / 反爬

```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch(
    'https://target.com',
    headless=True,
    network_idle=True
)
# 自动过 Turnstile 等反爬
```

### 3. 自适应选择器（网站改版后自动重定位）

```python
# 第一次爬：保存选择器模式
products = page.css('.product', auto_save=True)

# 网站改版后：自动匹配新结构
products = page.css('.product', adaptive=True)
```

### 4. 带 Session 的抓取

```python
from scrapling.fetchers import FetcherSession

session = FetcherSession()
page = session.get('https://example.com/login')
# 处理登录...
page = session.get('https://example.com/dashboard')
```

### 5. 完整爬虫（Spider 框架）

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}

MySpider().start()
```

## 定时爬虫部署（cron + Scrapling）

1. 写 Python 脚本（Scrapling 爬取 + 数据处理 + 输出）
2. 用 Hermes cron 调度（cronjob action=create）
3. 结果自动推送到用户

示例 cron prompt 结构：
```
用 Scrapling 爬取 [目标网站] 的 [数据]，格式化成 [表格/报告]，输出到 ~/Desktop/hermes/reports/
```

## 参考

- 官方文档：https://scrapling.readthedocs.io/en/latest/
- GitHub：https://github.com/D4Vinci/Scrapling（70k+ stars）
- 浏览器自动化（需登录/交互的场景）：见 `playwright-mcp` skill
- 抖音精选联盟选品脚本：`playwright-mcp` skill 的 `references/douyin-scraper.md`
- 抖音视频页内容提取（无需登录，拆解/分析视频用）：`references/douyin-page-extraction.md`
