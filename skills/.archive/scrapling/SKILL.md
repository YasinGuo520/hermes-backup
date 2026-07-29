---
name: scrapling
description: Scrapling Web Scraping 框架——自适应反爬绕过、元素选择器、蜘蛛框架、MCP集成。爬虫首选工具。
---

# Scrapling Web Scraping

Scrapling 是 Python 自适应爬虫框架（D4Vinci，70k+ stars）。
**默认爬虫工具**，替代纯 Playwright 方案。

## 什么时候用

| 场景 | 工具 | 理由 |
|------|------|------|
| 批量数据采集、竞品监控 | **Scrapling** ✅ 默认 | 开箱反爬、自适应选择器 |
| 需要登录的国内平台（抖音/百应） | Playwright（手动登录） | Scrapling 无手动登录流程 |
| 极度复杂的 JS SPA 交互 | Playwright | Scrapling fetcher 可能不够 |

## 安装

```bash
pip3 install scrapling
```

## 基础用法

### 快速 GET
```python
from scrapling.fetchers import Fetcher
page = Fetcher.fetch('https://example.com')
print(page.css('h1::text').get())
```

### 反爬模式（stealth）
```python
from scrapling.fetchers import StealthyFetcher
StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch(
    'https://target.com',
    headless=True,
    network_idle=True,
)
```

### 自适应选择器（核心功能）
```python
# 第一次爬：保存元素特征
products = page.css('.product', auto_save=True)

# 网站改版后：自动重定位
products = page.css('.product', adaptive=True)
# 或使用 auto_match=True
products = page.css('.product', auto_match=True)
```

### 完整爬虫（Spider 框架）
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

### MCP 集成（给 AI 工具调用）
Scrapling 自带 MCP Server，可以直接给 Claude/Cursor/Hermes 调用。
```bash
# 启动 MCP Server
python -m scrapling.mcp
```

## Fetcher 类型选择

| Fetcher | 速度 | 反爬能力 | 适用场景 |
|---------|------|---------|---------|
| `Fetcher` | ⚡⚡⚡ | 低 | 无反爬的公开API/静态站 |
| `StealthyFetcher` | ⚡⚡ | **高** ✅ 默认 | 有 Cloudflare/反爬的站 |
| `DynamicFetcher` | ⚡ | 中 | Playwright 兜底（JS渲染） |
| `AsyncFetcher` | ⚡⚡⚡ | 低 | 异步批量请求 |

> **默认选择：** `StealthyFetcher` — 开箱过 Cloudflare Turnstile，平衡速度和反爬。

## 性能

- 解析速度：比 lxml 快，远超 BeautifulSoup
- 内存：懒加载 + 优化数据结构
- JSON 序列化：orjson 驱动，10x 快于 stdlib

## 坑

- **中国服务器需要代理**：StealthyFetcher 默认走外网，可能被墙
- **First fetch 较慢**：StealthyFetcher 首次启动需要下载/配置 Camoufox 浏览器组件
- **MCP Server 需手动启动**：不是默认开启
- **adaptive 模式不是 100% 可靠**：网站结构大变后可能找不到，需要 fallback 到手动选择器
