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

#### ⚠️ 但很多后台根本没「下一页」按钮 —— 是懒加载滚动（先判形态，再动手）

字节系后台（抖店/百应/达人广场）的列表普遍是**无限滚动加载**。不知道这条会白折腾两轮：按文本找不到按钮 → 自动翻页逻辑直接失效。

**三秒判定**（页面里跑一次就知道）：

| 信号 | 含义 |
|---|---|
| `document.documentElement.scrollHeight == window.innerHeight` | **内部容器滚动**，滚 document 完全无效 |
| 找不到文本为「下一页/下页/Next」且可见可点的元素 | 无分页按钮 → 走滚动加载 |
| `[...document.querySelectorAll('*')].filter(e => e.scrollHeight > e.clientHeight + 150)` 有结果 | 那个元素就是真正的滚动容器（实测字节表格是 `.auxo-table-body`） |

**Playwright 正确触发**（实测每滚一次 = 加载一页 20 条）：

```python
page.mouse.move(840, 620)      # ★ 必须先把鼠标移进列表区域
page.mouse.wheel(0, 1500)      # wheel 作用于鼠标位置下的元素，默认停在 (0,0) 时列表不动
page.wait_for_timeout(3500)    # 等新一页数据回来
```

**自动翻页循环的安全写法**：每滚一次比对请求计数（`len(api_calls)`），没新增就记一次 stall，**连续 2 次无新请求即判定到底并停止** —— 页面改版也不会把脚本变成死循环。

> 一键探针（判定滚动加载 vs 分页按钮、列出可滚动容器、试滚并打印是否触发新 XHR）：`scripts/lazy-load-probe.py`

### ⭐ 首选不是抓 DOM，而是拦截 XHR

SPA 后台（抖店罗盘/百应/生意参谋）的 DOM 选择器**随改版必死**——写死选择器的脚本活不过一次发版（实测案例：7月写的百应脚本因写死路径+选择器整条链路失效，见 `references/china-platform-backend-monitoring.md` 第七节）。**改成拦截页面自己发出的 XHR，直接拿后端返回的 JSON**：

```python
captured = []
page.on("response", lambda r: captured.append(r) if "/api/" in r.url and r.status == 200 else None)
page.goto(target_url)
# 设筛选条件 / 翻页，数据随页面请求自动落进 captured
data = [r.json() for r in captured]   # 结构化字段，不依赖任何 CSS 选择器
```

为什么优先：①不依赖 UI 结构，改版不易失效 ②拿到的是源字段，比页面显示的更全 ③翻页只是改分页参数，**一次拿全量**——根治「全页复制为什么少了很多」（分页懒加载截断）这个经典痛点。

> 兜底顺序：拦 XHR → 读渲染后 DOM（带多选择器降级）→ 截图+视觉模型。**不要一上手就截图。**
> 可直接照用的采集器骨架：`templates/xhr-collector.py`

**拦 XHR 必踩的两个坑（2026-09 实测）**：

1. **URL 子串匹配会命中 CDN 上的埋点/配置文件** —— 实测 `lf3-cdn-tos.bytescm.com/obj/ecom-alliance-log/visual/buyin.json` 因 URL 含 `buyin` 被当数据抓走，而且**真的上报进库了**。过滤要用 **host 白名单**（如 `"jinritemai.com" in response.url`），不要用子串 hints；且「命中域名」≠「命中数据」，还要 `find_records()` 拿到非空 `list[dict]` 才上报。
2. **采集器必须「按间隔自动增量上报」，收尾不能靠按回车** —— 浏览器在用户机器上、脚本由我经 SSH 后台拉起时没有终端可交互，`input()` 收尾的上报逻辑等于永不执行。每 30s 把**新增**记录 POST 一次，中断/断线都不丢。
3. **同一个指标往往有好几组同名口径，不交叉核对就会选错** —— 实测达人接口里"销售额"至少三组：`sale_info.*_total_sales`（销售额）／`sale_info.*_total_sales_settle`（结算额，＝页面显示那一列）／`author_live.sale_low/high`（另一套，近似场均），同一达人三组能差 10 倍。选错口径＝整张表数字错，而且看着很合理不会报错。
   验证方法：把接口值跟你自己可从页面脚注/表格看到的那一列**逐列对一遍**；数值型的区间字段还常带 `status=2` 表示"该渠道无数据"，**不要当 0**（0 和「无」语义不同）。

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

### 持续采集强风控平台后台：必须跑用户本机，不能跑云服务器 ⚠️⚠️

做「定时/实时盯后台数据」这类**持续采集**（不是一次性抓取）时，载体选错会直接害用户：

| 载体 | 风险构成 | 判定 |
|------|---------|------|
| 云服务器（机房IP） | 机房IP + headless特征 + 平台风控 → 可能连累用户账号被封/告警 | ❌ 不做 |
| 逆向内部接口 | 需啃平台签名（字节系 Argus 等），触发风控概率高 | ❌ 不做 |
| **用户本机**（真IP + 真人浏览器profile） | 等同于用户自己在看后台，特征最干净 | ✅ 唯一可行 |

```
用户本机                          中心服务器                推送
├ 真实浏览器(用户已登录)
├ 采集器读渲染后DOM ──内网上报──► ├ 落地/趋势
└ 只读，不点任何按钮              ├ 分析引擎        ──► 飞书/TG
        ▲                        └ 历史对比
        └── Tailscale SSH：部署/排障/改频率（SSH是手，不是数据通道）
```

**三条红线**：
1. **只读不写** —— 绝不模拟登录流程、绝不点后台按钮；复用用户已登录的会话。
2. **用真人浏览器 profile**，不新建 headless 实例。
3. **采集频率 ≤ 数据源自身更新粒度** —— 后台 1 分钟才更新一次，抓更快只是招风控。

**Windows 当采集机的坑（必读）**：
- Windows 上**通过 SSH 启动图形程序会跑在服务会话（session 0）**，没有可见桌面 → 有头浏览器起不来或被降级成无头，而 headless 恰是风控最容易识别的特征。
- 因此：**采集器不能由 SSH 启动**，要注册成**登录自启的计划任务**，跑在真实交互桌面会话里；SSH 只负责装、改、看，不负责跑。
- 不知道这条会撞上「SSH 里跑得好好的，一关会话就断」的诡异现象，并误判成脚本 bug。

**macOS 当采集机（与 Windows 相反，别混用策略）**：
- macOS 上**从 SSH 启动有头 Chrome 是可行的**——SSH 会话属于已登录 GUI 用户，实测 `launch_persistent_context(headless=False)` 启动成功且能读页面 → 首次扫码登录可由远端直接拉起窗口，用户只需在屏幕上扫一下。
- 但 SSH 断开可能给子进程发 SIGHUP → 必须 `nohup ... > log 2>&1 < /dev/null &` 起，并 `pgrep -fl` 确认还活着。
- Playwright 用**系统真实 Chrome**（`channel="chrome"`），别下 chromium：省 ~130MB，且 UA/指纹=真机；**别硬编码 Windows UA 拿去 Mac 上跑**（UA 与真机不符本身就是风控破绽）。
- 桌面数据可读性有硬边界（窗口标题需辅助功能授权、`knowledgeC.db` 直接 `authorization denied`）→ 清单见 `references/macos-collection-host.md`。

**判定页面挂了风控的快速信号**：
- HTML 里出现 `argus-csp-token`（字节 Argus，抖音/抖店系）等风控脚本 → 按高危处理
- 页面体积异常小（SPA 空壳，~15KB）→ 数据全走 XHR，curl/web_extract 拿不到，必须渲染后读 DOM

> 完整案例（抖店罗盘实测 URL/风控/官方API门槛/会话断流 + computer_use 的边界）：见 `references/china-platform-backend-monitoring.md`

### 跨机操控的路径优先级（不要承诺做不到的事）

`computer_use` / cua-driver **只驱动 Hermes 自身所在那台机器的桌面**，没有远程桌面选项：daemon 的 `serve` 监听**本地 UNIX socket**，MCP 走 **stdio**，不监听网络端口 → 无法被远程直连；Hermes 跑在无头 Linux 上时 `DISPLAY` 为空，连本机窗口都拿不到。

需要操控另一台机器时，按此优先级选：

| 优先级 | 路径 | 适用 |
|:---:|------|------|
| 1 | **浏览器自动化**（本技能） | 目标是网页 → 首选 |
| 2 | **SSH**（Tailscale 内网） | 部署/排障/读数据，即「手」 |
| 3 | 目标机装一个 Hermes 实例 | 需要驱动 GUI 软件时 |
| 4 | RDP/远程桌面 + 像素点击 | 最贵最脆，非必要不用 |

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
- 国内平台后台持续采集架构（本机vs云服务器/风控判定/官方API门槛/跨机操控路径/百应域名与路径复盘）：`references/china-platform-backend-monitoring.md`
- 本机采集器骨架（持久 profile + 拦 XHR + 上报，可拷贝修改）：`templates/xhr-collector.py`
- 跨机作业的 shell 传输与超时（zsh 坑 / 别用 inline 引号 → scp 脚本过去跑 / macOS 无 timeout / 后台化三件套 / 精确取 pid）：`references/cross-machine-shell-ops.md`
- macOS 当采集机（能力边界表 / 系统 Chrome / SSH 起有头浏览器 / 部署清单 / 换机迁移 / profile History 取证 / 远端采集会话设计 / 交付前必说的现实 / **目标机自带 agent 为何干不了这件事的排查表**）：`references/macos-collection-host.md`
- 懒加载/无限滚动探针（判定滚动加载 vs 分页按钮 / 找滚动容器 / 试滚验触发）：`scripts/lazy-load-probe.py`
- 被墙/付费墙/WAF 页面恢复（Wayback/archive.today/Jina/API pivot 梯子 + 假成功清单）：`references/blocked-page-recovery.md` + `scripts/recover_page.py`


## 被墙/付费墙/WAF 页面恢复（合并自 blocked-page-recovery）

当目标页面抓不到（403/429、Cloudflare "Just a moment..."、付费墙、反爬拦截页）时，不要放弃也不要死循环同一 URL——第三方往往存有副本。完整梯子、来源规范、手工路由与「假成功」清单见 `references/blocked-page-recovery.md`，一键脚本 `scripts/recover_page.py`：

```bash
python3 scripts/recover_page.py "https://example.com/blocked-article" --json
```

梯子速查：①Wayback Machine（archive.org available API，快照+时间戳，来源最好先试）→ ②archive.today（archive.ph/.md/.li/.is 轮换）→ ③Jina Reader（需 JINA_API_KEY，服务端渲染，能过 JS SPA）→ ④API-first pivot（同站 /api/、/graphql、.json、RSS、sitemap）→ ⑤真实浏览器兜底（最贵最后用）。

引用纪律：Wayback/archive.today 的副本必须标快照日期（"as archived 2026-08-06"），不能当活页引用；用户要当前数据（价格/库存/突发新闻）时快照只是上下文，要明说并标注时效。**假成功**：Google Cache 已死（2024年中起，返回的是搜索拦截页）；AMP cache 返回 meta-refresh 跳回原页；代理中转站是中间人，绝不传 cookie/Authorization。

