---
name: web-scraping
description: 数据采集与浏览器自动化——Scrapling 优先，Playwright 备选（反检测/手动登录/多选择器降级）。
---

# Web Scraping（数据采集）

**首选工具：Scrapling**（v0.4.11+，已安装）
**备选：Playwright**（见下文「Playwright 浏览器自动化」章节，用于需要手动登录/浏览器交互的自动化场景）

## 选型决策

```
要爬的东西 → 需要登录/交互吗？
  ├── 否 → Scrapling（StealthyFetcher / Fetcher）
  └── 是 → 需要浏览器操作吗？
        ├── 否（仅 cookie 登录）→ Scrapling（FetcherSession）
        └── 是 → Playwright（见下文「Playwright 浏览器自动化」章节）
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

## Playwright 浏览器自动化（合并自 playwright-mcp）

需要真实浏览器操作（登录态、JS 渲染、交互验收）时用 Playwright。**非无头模式用于手动登录；无登录场景优先 Scrapling。**

### 安装（标准 + 中国镜像）

```bash
pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple
PLAYWRIGHT_DOWNLOAD_HOST=https://npm.taobao.org/mirrors python3 -m playwright install chromium
```

uv 环境坑：`pip install` 可能报 externally-managed-environment → `pip3 install <pkg> --break-system-packages` 或 `uv pip install <pkg>`；包装到 `/usr/local/lib/python3.x/site-packages` 但不在默认 sys.path 时，脚本头加 `sys.path.insert(0, '/usr/local/lib/python3.11/site-packages')`。

### 反检测配置

```python
browser = playwright.chromium.launch(
    headless=False,  # 非无头 = 用户可见，用于手动登录
    args=['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-web-security'],
)
context = browser.new_context(
    viewport={'width': 1440, 'height': 900},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ...",
)
```

### 手动登录模式（对付需要登录的国内平台：百应工作台、抖音电商后台）

1. 非无头打开浏览器 → 导航登录页，打印引导提示
2. 轮询 URL 变化（`/login` 路径消失 = 登录成功）
3. 保存 cookies 供后续复用

```python
page.goto(LOGIN_URL, wait_until='networkidle')
start = time.time()
while time.time() - start < timeout:
    if '/login' not in page.url:
        cookies = context.cookies()
        return True
    time.sleep(2)
```

### 多选择器降级策略（动态页面元素选择器经常变）

```python
def _get_product_cards(page):
    selectors = ['.product-card', '.goods-item', '.goods-card',
                 '[class*="product"]', '[class*="goods"]',
                 '.ant-table-row', '.el-table__row']
    for selector in selectors:
        cards = page.query_selector_all(selector)
        if cards and len(cards) > 1:
            return cards
    return []
```

翻页按钮同样多选器：`.ant-pagination-next` / `.el-pagination .btn-next` / `aria-label="下一页"`。

### 无头服务器模式（browser-harness 不可用时的替代）⚠️

服务器（无显示器、无 Chrome）上 browser-exec/harness 报 `chrome-not-running` 时，**绕开 harness 直接用 playwright Python**：

```bash
# 1. 已有 venv 时装 playwright（用国内源/已缓存 chromium）
source <project>/venv/bin/activate && pip install playwright

# 2. 关键：本机缓存的 chromium 版本可能和新装的 playwright 不匹配，
#    报 "Executable doesn't exist at .../chromium_headless_shell-1234/"
#    → 不要重新下载！直接 executable_path 指向缓存版本：
#    find ~/.cache/ms-playwright/ -name "chrome-headless-shell" -type f
browser = p.chromium.launch(
    executable_path="/home/ubuntu/.cache/ms-playwright/chromium_headless_shell-XXXX/.../chrome-headless-shell",
    args=["--no-sandbox", "--disable-dev-shm-usage"])
```

**坑点**：
- browser-harness 版本和本地 playwright 版本可能不匹配——`pip install playwright` 后先跑 `python -c "import playwright"` 验证，再测 launch
- 无头浏览器对字节系站点（Coze 扣子/抖音）**防不胜防**：一旦触发滑块验证码，别死磕反检测 JS（navigator.webdriver=undefined 之类），验证码 iframe 已经加载，绕不过。正确路径：抓登录后**让用户手机配合**（填手机号→用户把短信验证码给我）。
- 判定验证码发送是否成功：按钮变倒计时（"60s"）= 发出；按钮仍是"发送验证码"= 还没真正发出去。

### 坑 & 注意

- **抖音反爬极强**：无登录直接访问搜索页会跳验证码，必须用已登录 session。
- **百应工作台需达人权限**：普通抖音账号无精选联盟爆款榜访问权限。
- **非无头不能用于 cron**：手动登录场景 headless=False；首次手动登录存 cookies，后续复用。
- **`input()` 交互**：脚本在终端运行（非 execute_code）才能接收用户输入。

## 参考

- 官方文档：https://scrapling.readthedocs.io/en/latest/
- GitHub：https://github.com/D4Vinci/Scrapling（70k+ stars）
- 浏览器自动化（需登录/交互的场景）：见上文「Playwright 浏览器自动化」章节
- 抖音精选联盟选品脚本（Playwright + openpyxl 输出 Excel，可作模板）：`references/douyin-scraper.md`
- 抖音视频页内容提取（无需登录，拆解/分析视频用）：`references/douyin-page-extraction.md`
- 被墙/付费墙/WAF 页面恢复（Wayback/archive.today/Jina/API pivot 梯子 + 假成功清单）：`references/blocked-page-recovery.md` + `scripts/recover_page.py`


## 被墙/付费墙/WAF 页面恢复（合并自 blocked-page-recovery）

当目标页面抓不到（403/429、Cloudflare "Just a moment..."、付费墙、反爬拦截页）时，不要放弃也不要死循环同一 URL——第三方往往存有副本。完整梯子、来源规范、手工路由与「假成功」清单见 `references/blocked-page-recovery.md`，一键脚本 `scripts/recover_page.py`：

```bash
python3 scripts/recover_page.py "https://example.com/blocked-article" --json
```

梯子速查：①Wayback Machine（archive.org available API，快照+时间戳，来源最好先试）→ ②archive.today（archive.ph/.md/.li/.is 轮换）→ ③Jina Reader（需 JINA_API_KEY，服务端渲染，能过 JS SPA）→ ④API-first pivot（同站 /api/、/graphql、.json、RSS、sitemap）→ ⑤真实浏览器兜底（最贵最后用）。

引用纪律：Wayback/archive.today 的副本必须标快照日期（"as archived 2026-08-06"），不能当活页引用；用户要当前数据（价格/库存/突发新闻）时快照只是上下文，要明说并标注时效。**假成功**：Google Cache 已死（2024年中起，返回的是搜索拦截页）；AMP cache 返回 meta-refresh 跳回原页；代理中转站是中间人，绝不传 cookie/Authorization。

