# 板块热点推荐系统

**脚本：** `~/Desktop/hermes/quant-skill/quant_sectors.py`
**创建：** 2026-07-27
**依赖：** `quant_ensemble.py` (复用 `compute_tech_score`)

## 数据流

```
baostock(行业分类+总股本+日K线) → 行业聚合 → 技术评分 → 市值过滤 → Top3板块×3股
```

## 关键步骤

### 1. 行业分类映射

```python
import baostock as bs
bs.login()
rs = bs.query_stock_industry()
ind_map = {}
while rs.next():
    row = rs.get_row_data()
    code_full = row[1]     # 'sh.600000'
    industry = row[3]      # 'J66货币金融服务'
    if industry and '.' in code_full:
        pure_code = code_full.split('.')[1]
        ind_map[pure_code] = industry
bs.logout()
```

- 字段索引: [1]code(含前缀), [2]code_name, [3]industry(带编号)
- 行业名含编号前缀如 `J66`，可用 `INDUSTRY_SHORT` 字典映射为短名

### 2. 行业名简化

预定义 `INDUSTRY_SHORT` 字典（40+映射），如 `J66货币金融服务` → `🏦银行`。
未映射的行业保留原名。

### 3. 总股本（市值过滤）

```python
rs = bs.query_profit_data(f"{prefix}.{code}", year=year, quarter=1)
if rs.next():
    total_share = float(row[9])    # 总股本(股)
    market_cap = total_share * price / 1e8  # 亿
```

- 过滤 market_cap < 100 亿

### 4. 技术评分

复用 `quant_ensemble.py` 的 `compute_tech_score(df)` 函数。
返回9维度综合分 + 各分量（供分解展示）。

### 5. 板块排序

每板块取Top5只的技术分均值作为板块分。跨板块按此排序。

## 已知坑

| 问题 | 表现 | 修复 |
|:----|:-----|:-----|
| 新浪行情批量>50只 | Connection reset | 按30只分批请求 |
| query_stock_basic 名称索引 | 显示IPO日期 | row[1]是名称, row[2]是IPO日期 |
| 行业分类查询慢 | 16s | 不可并行，baostock单线程 |
| 东方财富资金流API盘后 | 空响应 | 降级运行，不影响主体 |
