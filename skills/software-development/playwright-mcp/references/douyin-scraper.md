# 抖音精选联盟选品采集脚本参考

采集来源：百应达人工作台 → 精选联盟 → 选品广场 → 爆款榜
输出：桌面 / 抖音精选联盟选品表_YYYY-MM-DD.xlsx

## 核心逻辑

1. Playwright 非无头打开浏览器 → 用户手动扫码登录百应工作台
2. 登录后导航到选品广场爆款榜
3. 多选择器降级抓取商品卡片
4. 解析：标题、价格、销量、佣金率、店铺名
5. 筛选条件：30-80元、佣金率≥15%、排除非桌播品类
6. 按销量降序排列，输出 Excel（openpyxl）到桌面
7. Excel 含：选品清单 Sheet + 选品策略 Sheet

## 关键代码模式

### 价格解析（单位：分，保留精度）
```python
price = re.findall(r'(\d+\.?\d*)', text.replace(',', ''))
return int(float(price[0]) * 100) if price else None
```

### 翻页检测
```python
btn = page.query_selector('[aria-label="下一页"], .ant-pagination-next')
disabled = btn.get_attribute('disabled') or btn.get_attribute('aria-disabled')
if disabled in ('true', ''): break
btn.click()
time.sleep(2)
```

### 桌播适配度评分规则
- 基础分 3
- 加分词：收纳、厨房、神器、清洁、抹布、拖把、挂钩、置物架、多功能、懒人、折叠、便携（每个 +0.5）
- 减分词：电器、数码、充电、服装、鞋子、食品、生鲜（每个 -0.5）
- 最终分 1-5

### 推荐指数规则
- 价格 30-50 元 +3，50-80 元 +2
- 销量 ≥10000 +3，≥5000 +2
- 桌播分直接累加
- 佣金 ≥25% +3，≥20% +2
- ≥10 分 ⭐⭐⭐⭐⭐，≥8 ⭐⭐⭐⭐，≥6 ⭐⭐⭐

## 数据源

| 来源 | 方式 | 费用 | 说明 |
|------|------|------|------|
| 百应工作台 (buyin.douyinec.com) | Playwright 用户登录后采集 | 免费 | 最实时准确，需达人权限 |
| 聚推客联盟 (jutuike.com) | REST API | 注册免费（有 captcha） | 有商品搜索 API，需 pub_id |
| 有米有数 (youcloud.com) | SaaS 平台 | 付费试用 | 功能最全但收费 |
| 蝉妈妈/飞瓜 | SaaS 平台 | 付费 | 第三方数据平台 |
| 模板示例数据 | 内置 | 免费 | 基于公开趋势，非实时 |

## 安装依赖

```bash
pip3 install playwright openpyxl
playwright install chromium
# 中国镜像见 playwright-mcp 技能
```

## 注意事项

- 必须在终端（非 execute_code）运行，因为涉及 `input()` 交互和 Playwright 浏览器窗口
- 每次运行会打开 Chromium 窗口，用户需手动扫码登录
- 百应工作台页面结构可能变化——更新选择器策略即可
- 如需每日自动化：首次运行保存 cookies，后续可 headless 复用
