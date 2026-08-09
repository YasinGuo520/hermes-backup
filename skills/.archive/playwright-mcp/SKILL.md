---
name: playwright-mcp
description: 浏览器自动化——Playwright安装、反检测配置、手动登录流程、多选择器降级爬取的完整实践。
---

# Playwright MCP（浏览器自动化 + 数据采集）

使用Playwright进行浏览器自动化操作：测试、爬取、验收。本技能覆盖标准用法和中国网络环境下的爬取场景。

---

## 安装（标准 + 中国镜像）

### 标准安装
```bash
pip install playwright
playwright install chromium
```

### 中国网络（墙内）安装
```bash
# 使用清华镜像安装包
pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用淘宝镜像下载Chromium
PLAYWRIGHT_DOWNLOAD_HOST=https://npm.taobao.org/mirrors python3 -m playwright install chromium
```

### uv 环境问题排查
- uv 管理的 Python 环境可能拒绝 `pip install`（报 externally-managed-environment）
- 解决：`pip3 install <pkg> --break-system-packages` 或 `uv pip install <pkg>`
- 包可能装到 `/usr/local/lib/python3.x/site-packages` 但不在默认 sys.path 中
- 运行前加 `sys.path.insert(0, '/usr/local/lib/python3.11/site-packages')`

---

## 反检测配置（对抗反爬）

```python
browser = playwright.chromium.launch(
    headless=False,  # 非无头 = 用户可见，适用于需要手动登录的场景
    args=[
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-web-security',
    ]
)
context = browser.new_context(
    viewport={'width': 1440, 'height': 900},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ..."
)
```

---

## 核心模式：等待用户手动登录

对付需要登录的国内平台（百应工作台、抖音电商后台等），最佳实践是：

1. 以非无头模式打开浏览器
2. 导航到登录页面，打印引导提示
3. 轮询检测 URL 变化（/login 路径消失视为登录成功）
4. 保存 cookies 供后续复用

```python
page.goto(LOGIN_URL, wait_until='networkidle')
start = time.time()
while time.time() - start < timeout:
    if '/login' not in page.url:
        cookies = context.cookies()
        return True
    time.sleep(2)
```

---

## 数据采集：多选择器降级策略

动态页面的元素选择器经常变化。使用多选择器降级：

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

翻页按钮同样：`.ant-pagination-next` / `.el-pagination .btn-next` / `aria-label="下一页"`。

---

## 坑 & 注意事项

- **抖音反爬极强**：无登录状态下直接访问抖音搜索页会跳验证码。必须用已登录的浏览器 session。
- **百应工作台需达人权限**：普通抖音账号无精选联盟爆款榜访问权限。
- **非无头模式不能用于 cron**：需要手动登录的场景必须 headless=False。解决方案：首次手动登录保存 cookies，后续复用。
- **`input()` 交互**：脚本在终端运行（非 execute_code）才能使用 input() 接收用户输入。

---

## 参考脚本

本技能目录下的 `references/douyin-scraper.md` 记录了一个完整的抖音精选联盟选品采集脚本（Playwright + openpyxl 输出 Excel），可用作自定义采集的模板。
