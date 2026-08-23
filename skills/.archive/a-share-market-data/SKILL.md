---
name: a-share-market-data
description: A股（中国A股）实时行情、板块排名、个股查询 — 基于新浪财经免费API，零依赖，无需VPN。
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [A-shares, China, stocks, finance, 股票, A股]
    category: finance
    related_skills: [stocks, a-share-stock-selection-methodology]
---

# A股市场数据 (A-Share Market Data)

从中国大陆获取A股实时行情、板块排名、个股数据。**无需API密钥、无需安装包、不会翻墙**。
数据源：新浪财经免费接口（`hq.sinajs.cn`）。  
**2026-07-22 重要警告：东方财富批量报价API（push2.eastmoney.com/api/qt/ulist.np/get）在多个服务器环境下持续返回空数据，不可靠。不推荐作为行情主数据源。实时行情以 Sina Finance API 为首选。**

如需流通市值字段：通过个股池预设（手动维护各板块标的的市值信息）或东方财富单只K线API（push2his）间接获取。

## 何时使用

- 用户问 A股 实时股价（"寒武纪多少钱""查一下有研硅"）
- 用户想看 **板块涨幅排名**（"今天什么板块涨"）
- 用户在中国，Yahoo Finance 无法访问
- 需要快速获取A股个股的开盘价、最高价、成交量等实时数据
- 需要获取 **行业板块** 或 **概念板块** 的涨跌幅排名

## 前提条件

- `curl` 可用（macOS/Linux 自带）
- Python 3.8+ 即可（解析脚本只用 stdlib）

## 代码格式

| 交易所 | 前缀 | 示例 |
|--------|------|------|
| 上海主板 (`6`开头) | `sh` | `sh600519` 贵州茅台 |
| 科创板 (`688`开头) | `sh` | `sh688256` 寒武纪 |
| 深圳主板 (`00`开头) | `sz` | `sz002185` 华天科技 |
| 创业板 (`300`开头) | `sz` | `sz300043` 星辉娱乐 |

## 快速查询（curl）

```bash
# 单只股票
curl -s -H "Referer: https://finance.sina.com.cn" \
  "https://hq.sinajs.cn/list=sh688256"

# 多只股票（逗号分隔）
curl -s -H "Referer: https://finance.sina.com.cn" \
  "https://hq.sinajs.cn/list=sh688432,sz002185,sz002558,sz300043,sh688256,sh603019"
```

**⚠️ Referer 头必须加**，否则返回 HTTP 403 Forbidden。

如果返回乱码（GBK编码），加 `iconv` 转 UTF-8：
```bash
curl -s -H "Referer: https://finance.sina.com.cn" \
  "https://hq.sinajs.cn/list=sh688256" | iconv -f GBK -t UTF-8
```

## 响应格式解析

新浪返回 JavaScript 变量赋值：

```
var hq_str_sh688432="有研硅,38.980,38.450,46.140,46.140,38.130,46.140,0.000,76565979,3389040404.000,...,2026-07-07,15:20:34";
```

引号内逗号分隔的字段：

| 索引 | 字段 | 含义 |
|:----:|:----:|:----:|
| 0 | 名称 | 股票中文名 |
| 1 | 开盘价 | 今日开盘 |
| 2 | 昨收价 | 昨日收盘 |
| 3 | 当前价 | **最新成交价** |
| 4 | 最高价 | 今日最高 |
| 5 | 最低价 | 今日最低 |
| 6 | 竞买价 | 买一价 |
| 7 | 竞卖价 | 卖一价 |
| 8 | 成交量 | 手数 |
| 9 | 成交额 | 元 |
| ... | 买五~卖五 | 盘口明细 |
| -2 | 日期 | YYYY-MM-DD |
| -1 | 时间 | HH:MM:SS |

### 涨跌幅计算

```python
change_pct = (current_price - prev_close) / prev_close * 100
```

**科创板/创业板**：涨跌幅 20%（涨停=昨收×1.2，跌停=昨收×0.8）
**主板**：涨跌幅 10%（涨停=昨收×1.1，跌停=昨收×0.9）

## 使用脚本

技能自带 `scripts/sina_ashare.py` 脚本，封装了 curl + 解析逻辑：

```bash
# 批量查询个股
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/sina_ashare.py quote sh688432 sz002185 sz002558

# 获取行业板块涨幅排名
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/sina_ashare.py sectors

# 获取概念板块涨幅排名
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/sina_ashare.py concept
```

## K线（历史行情）数据

A股K线数据有以下可靠来源（按稳定性排序）：

### 来源 A：Baostock（最稳定 — 2026-07-25确认）

在腾讯云等国内服务器上，HTTP类API（akshare/163/东方财富）经常被远程关闭。baostock使用本地socket TLS协议，不走HTTP，**不会受API封锁影响**。

```bash
pip install baostock
```

```python
import baostock as bs, pandas as pd
bs.login()
rs = bs.query_history_k_data_plus("sz.000001", "date,open,high,low,close,volume,amount", "2026-01-01", "2026-07-24", "d", "2")
rows = []
while rs.next():
    rows.append(rs.get_row_data())
bs.logout()
df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume","amount"])
for c in ["open","high","low","close","volume","amount"]: df[c] = df[c].astype(float)
```

> 完整用法见 `references/baostock-data-guide.md`

### Baostock 行业分类

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

- `query_stock_industry()` 字段索引: [1]code(含sh./sz.前缀), [2]code_name, [3]industry(带编号)
- 代码需带 `sh.`/`sz.` 前缀查询，解析后剥离前缀匹配数字股票池

### Baostock 总股本（市值计算）

```python
rs = bs.query_profit_data('sz.300750', year=2026, quarter=1)
if rs.next():
    row = rs.get_row_data()
    total_share = float(row[9])    # 总股本(股)
    market_cap = total_share * price / 1e8  # 转为亿
```

字段: [9]totalShare(总股本), [10]liqaShare(流通股)

### Baostock 股票名称查询

```python
rs = bs.query_stock_basic('sh.600000')
if rs.next():
    row = rs.get_row_data()
    name = row[1]  # 索引1=名称, 索引2=IPO日期(不是名称!)
```

**常见错误：** 索引2取到的是IPO日期('2018')而非股票名。

### 来源 B：新浪财经 K线 API（推荐 — 最稳定的HTTP源）

无需 Referer 头，纯 JSON 格式，`urllib`/`requests`/`curl` 均正常工作。

```bash
# 日线（scale=240），最多约 300 条
curl -s "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002050&scale=240&ma=no&datalen=100"
# 60分钟线（scale=60）
curl -s "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh688256&scale=60&ma=no&datalen=40"
```

**参数说明：** `symbol`=sh/sz+代码, `scale`=240(日线)/60(60分钟), `datalen`=条数

**响应格式：** JSON数组，每项`{day, open, high, low, close, volume}`，价格字段是字符串

**注意事项：** 无Referer要求，无频率限制，不含成交额/换手率

### 来源 B：东方财富历史K线 API（含换手率和成交额）

```bash
# 日线（klt=101），secid规则：1.xxx=上证, 0.xxx=深证
curl -s "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.002050&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&end=20500101&lmt=100"
```

**参数说明：** `secid`=1.上证代码/0.深证代码, `klt`=101日线/102周线/60=60分钟, `lmt`=条数

**响应格式：** 逗号分隔：`日期,开盘,收盘,最高,最低,成交量(手),成交额(元),振幅(%),涨跌幅(%),涨跌额,换手率(%)`

**注意事项：** 偶有Python urllib SSL握手失败（curl通常正常），需清理JSONP括号包裹

### 多周期分析推荐

| 场景 | 周期 | 数据量 | 用途 |
|------|------|--------|------|
| 日线趋势 | 日线 | 60-100条 | 主趋势、MA/RSI/MACD |
| 短线入场 | 60分钟 | 40条 | 入场时机、支撑压力 |
| 大方向 | 周线 | 30条 | 周线方向判断 |
| 量价分析 | 日线 | 100条 | 量比、放量启动 |

> **推荐组合：** 新浪拉日线和60分钟线（稳定），东方财富拉周线（含换手率）。

### 东方财富个股资金流向（主力净流入）

东方财富 `push2.eastmoney.com/api/qt/ulist.np/get` 接口的 `f62` 字段返回**主力净流入**（元）。
**⚠️ 该接口盘后/非交易时段经常返回空响应（Connection reset），交易时段较稳。**

```python
import urllib.request, json
url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=1&fields=f2,f3,f12,f14,f62&secids=0.000338,1.601127&mpvc=1"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://quote.eastmoney.com/'
})
with urllib.request.urlopen(req, timeout=8) as resp:
    raw = resp.read().decode('utf-8')
```

**字段：** f2=现价(×100), f3=涨跌幅(×100), f12=代码, f14=名称, f62=主力净流入(元)

### 新浪行情批量请求限制

新浪 `hq.sinajs.cn` 单次URL请求超过 **~50只股票** 时，部分服务器环境会返回 `Connection reset by peer`。
**按批次≤30只分割请求**，失败自动降级。

```python
batches = [codes[i:i+30] for i in range(0, len(codes), 30)]
for batch in batches:
    sina_codes = [f"{'sh' if c.startswith('6') else 'sz'}{c}" for c in batch]
    url = f"https://hq.sinajs.cn/list={','.join(sina_codes)}"
    req = urllib.request.Request(url, headers={
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0'
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode('gbk')
```

## 板块数据

新浪不直接提供板块排行接口。要获取板块涨跌幅排名，用以下替代方案：

### 方案 A：东方财富网页抓取

```bash
curl -s "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&fields=f12,f14,f3,f62,f184,f66&fs=m:90+t:2" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); [print(f\"{i['f14']}: {i['f3']}%\") for i in d.get('data',{}).get('diff',[])]"
```

参数说明：
- `m:90+t:2` = 行业板块, `m:90+t:3` = 概念板块
- `f3` = 涨跌幅, `f14` = 板块名
- `po=1` = 降序（涨幅从高到低）

### 方案 B：Web搜索

当API不可用时，用 `web_search` 搜索当日热点板块：
> 搜索词: `A股 今日 板块涨幅排名`
> 来源: 东方财富、证券时报、同花顺

## 完整的 A股量化分析流程

当用户要求"量化分析A股板块""推荐股票""选股分析"时，**必须先加载 `a-share-stock-selection-methodology` skill**（选股方法论），本skill只负责数据获取。

执行顺序：
1. **加载选股方法论** → `skill_view(name='a-share-stock-selection-methodology')`
2. **获取板块排名** — 东方财富API或web_search
3. **确认热点板块** — 结合资金流向、涨停家数，验证板块资金是否连续3日流入
4. **板块内选股** — 选中龙头+弹性标的各一只，需同时验证多周期（日线+60分+周线）
5. **获取实时股价** — Sina Finance API验证
6. **获取成交量/技术指标** — 计算量比、MACD、布林带（使用execute_code + pandas_ta）
7. **交付结构化报告** — Markdown表格，包含：板块名、涨跌幅、推荐个股、RSI、MACD信号、量比信息、目标价位、止损位、逻辑、风险提示

## 量化推荐收盘验证

当用户要求验证早盘量化推荐（cron job `ea324446676f`）的收盘成绩时：

1. 读取当天 cron 输出文件：`~/.hermes/cron/output/ea324446676f/YYYY-MM-DD_HH-MM-SS.md`
2. 从输出表格提取股票代码（第2列）和早盘推荐价
3. 用 Sina API 批量查收盘价（规则见 `references/quant-recommendation-verification.md`）
4. 计算每只股票涨跌幅，与早盘推荐对比
5. 输出带涨跌幅颜色的成绩表

> 完整步骤和代码示例见 `references/quant-recommendation-verification.md`

## 每日收盘 cron（15:30自进化 + v2当日验证）— 两套独立系统

每日收盘 cron 分两步，注意这是**两套不同的系统，日志和权重互不相通**：

| 系统 | 脚本路径 | 日志 | 权重 |
|---|---|---|---|
| 旧因子权重系统（自进化） | `~/projects/quant_self_evolve.py` | `~/projects/quant_recommend_log.json` | 20+因子权重（rsi/macd/ma 等，`~/projects/quant_weights.json`） |
| v2糅合系统 | `~/Desktop/hermes/quant-skill/quant_ensemble.py` | `~/Desktop/hermes/quant-skill/logs/YYYY-MM-DD.json` | tech/kronos/flow (0.45/0.30/0.25) |

**第一步**：`python3 ~/projects/quant_self_evolve.py` = 完整复盘+调权；`--report-only` = 只看报告不调权。
⚠️ **该脚本不处理 `--help`**：传 `--help`（或任何未知参数）会直接跑完整流程并把 `quant_weights.json` 改写调权。想只看报告必须显式传 `--report-only`。

**第二步**：v2 当日验证。读 `logs/` 当日 JSON 的 `top_k`（8只），新浪 API 查收盘价，涨幅 = (当前价-昨收)/昨收。

⚠️ **今日无 v2 日志 ≠ 一定是非交易日**：先排查早盘 cron（`ea324446676f`）是否失败，再决定跳过。常见根因 = **全局模型配置漂移**触发 cron 安全守卫拦截（2026-08-12 实测）。快速诊断：
1. `ls -la ~/.hermes/cron/output/ea324446676f/` —— 当天输出文件异常小（正常 4-10KB，失败仅 ~1.7KB）
2. 读当天输出 md，若含 `RuntimeError: Skipped to prevent unintended spend: global inference config drifted (provider 'deepseek' -> 'openai-api'; model 'deepseek-v4-flash' -> 'gpt-5.5')` → 确认是配置漂移拦截，**不是非交易日**
3. 修复状态核对：`stat -c '%y' ~/.hermes/config.yaml`（应已改回 deepseek/deepseek-v4-flash）+ `~/.hermes/cron/jobs.json` 四字段（provider/model/provider_snapshot/model_snapshot 均为 deepseek）
4. 报告时明确写「cron 失败原因」而非「非交易日跳过」，并提示量化看板 08:50 同步同天缺数据会自动补齐

> 完整诊断+修复细节见 `references/quant-cron-drift-diagnosis.md`

**累计准确率口径（重要）**：cron 任务里的「累计N天准确率」是**推荐当日**口径 —— 推荐日收盘 vs 前一交易日收盘，不是 T+1。`backtest_quant_logs.py` 输出的是 1日后/2日后/3日后（T+1 口径），数值与当日口径不同（实测 8-06：当日 56.9% vs T+1 47%）。当日口径直接用脚本：

```bash
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/verify_v2_daily.py [日志目录] [--top 8]
```

脚本用新浪 K线 API（`CN_MarketData.getKLineData`）按推荐日期匹配当日收盘，输出每日命中数/平均涨幅 + 累计准确率。

**⚠️ 除权除息日口径差异（2026-08-13 实测）**：个股除权除息当天，`hq.sinajs.cn` 的「昨收」字段(索引2)是交易所**调整后参考价**，而 K线 API 的前一交易日收盘是**未调整原始价**，两者会差一个分红/送转幅度。例如潍柴动力(000338) 2026-08-13 除息：hq 昨收=30.94（调整后），K线 08-12 收盘=31.31（原始）→ 官方涨跌幅 -2.72% vs 原始口径 -3.87%。而 `verify_v2_daily.py` 用**原始K线收盘**对比，除息日会高估跌幅（忽略分红）。处理规则：① 日报表格涨幅按任务口径用 hq 昨收（官方口径）；② 累计准确率用脚本数字，但当日有除息股时报告需注明两口径差异；③ 快速识别法——同一批查询里只有个别股票 hq 昨收 ≠ K线前一日收盘、其余全部相等 → 该股当日除权除息。

## 量化模型多日回测与因子诊断

当用户反馈「量化模型不太行 / 推荐不准 / 要验证历史表现」时，不要只看单日成绩——跑**多日回测**并做**因子健康度诊断**：

```bash
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/backtest_quant_logs.py [日志目录] [--top 8] [--window 5]
```

脚本自动：
1. 读取量化日志 `~/Desktop/hermes/quant-skill/logs/*.json`（schema: `{date, weights, top_k:[{code, total, tech, kronos, flow, flow_amount, disagreement, ...}]}`）
2. 新浪K线API拉每只推荐股历史行情，算推荐后 1/2/3 个交易日实际涨跌
3. 输出命中率(>0%算赢) + 平均收益，并拉上证指数对比是否跑赢大盘
4. 检查因子健康度：Kronos 取值分布、flow 是否全 0

**因子失效红旗（一眼判断模型哪里坏了）：**

| 现象 | 含义 | 修复方向 |
|---|---|---|
| Kronos 连续全 1.0 或全 0.0 | 信号饱和/预测失败，因子失去区分度，权重形同虚设（常见根因：strength 放大系数过大如 `×10` 导致全部同分） | 放大系数降到 2~3 |
| flow 连续多天全 0 | 东财 `push2.eastmoney.com` ulist API 空响应（该接口在腾讯云等服务器不稳定），0.25 权重空转 | flow 全 0 时权重自动重分配 |
| top_k 反复出现同一批代码 | 只剩 MA 等技术因子在排序，在推「均线多头的大盘蓝筹」，短线无弹性 | 修好 Kronos/flow 或换信号源 |

**量化糅合系统 v2 现状**（Yasin 的本地系统）：`~/Desktop/hermes/quant-skill/quant_ensemble.py`，基础权重 tech=0.45 / kronos=0.30 / flow=0.25。**2026-08-04 已完成修复**：① Kronos `predict_kronos` 的 `strength = min(abs(pc/start_p-1)*10, 1.0)` 放大系数 10→2.5，并在 run() 里对 kronos_signal 做 z-score 归一化（`tanh(z*2)*0.5`），消除饱和；② 资金流覆盖率 <60% 时自动降权，空出权重按原比例分给 tech/kronos；③ 分歧度 >0.3 标「观望」、>0.5 直接排除，日志 top_k 增加 advice 字段。修复后五日回测：3日均值 +0.29%（旧 +0.10%）、3日命中 52%（旧 48%），提升有限——该模型本质是「均线多头蓝筹」选股器，50-60% 命中率是正常水平，跑一周真实数据再决定是否动权重。完整诊断+修复+回测方法见 `references/quant-ensemble-health-diagnostics.md`。

## 风险提示

- Sina Finance 接口是非官方的，可能在不通知的情况下变更
- 东方财富推送接口同样非官方
- 所有数据**延迟约 3-5 秒**（非Level-2行情）
- 仅供研究参考，**不构成投资建议**
- 国内市场有涨停板制度，追涨需谨慎

## 技能文件结构

```
finance/a-share-market-data/
├── SKILL.md                       # 本文件 — 综合使用指南
├── scripts/
│   ├── sina_ashare.py             # A股行情查询 + 板块排名脚本
│   └── backtest_quant_logs.py     # 量化推荐多日回测 + 因子健康度检查
├── references/
│   ├── sina-finance-api.md        # 新浪财经API格式详细文档（含字段表）
│   ├── quant-cron-drift-diagnosis.md  # v2日志缺失=配置漂移cron失败 诊断流程（2026-08-12）
│   └── ...
├── eastmoney-sector-api.md    # 东方财富板块排名API文档（含curl示例）
├── eastmoney-kline-api.md     # 东方财富历史K线API文档（含参数表、Python示例）
└── baostock-data-guide.md     # Baostock数据源指南（HTTP API被屏蔽时的备选）


## Pitfalls\n\n- **⚠️ 新浪字段索引易混淆：索引1=开盘价，索引2=昨收价，索引3=当前价**。常见错误是把索引1当当前价、索引3当开盘价。涨跌幅必须用 (当前价 - 昨收) / 昨收，不是 (当前价 - 开盘)/开盘。索引从0开始计数，确认清楚再写代码。\n- curl 必须加 `Referer: https://finance.sina.com.cn` 头，否则403
- GBK编码问题：用 `iconv -f GBK -t UTF-8` 或 Python 的 `.decode('gbk')`
- **subprocess.run获取新浪行情时不要用text=True**：会强制utf-8解码失败，正确做法是 `capture_output=True` 不加text参数，再 `.decode('gbk')`
- **curl的-H参数必须带 Referer: 前缀**：正确格式 `-H "Referer: https://finance.sina.com.cn"`，错误格式 `-H "https://finance.sina.com.cn"`（缺少 `Referer: ` 头字段名）。后者在shell中看似工作但实际没传正确的HTTP头，导致403
- **新浪行情代码需去掉交易所前缀**：Sina返回 `sh600519` 格式，Python解析时必须剥离前2个字符得到 `600519`，否则与股票池代码映射不匹配（股票池用纯数字代码）
- **A股价格过滤阈值**：优质蓝筹股（宁德时代382元、寒武纪1350元、贵州茅台1308元）价格远超100元。如果设定价格上限 ≤100 会漏掉关键龙头。建议上限设为 500 或直接不做价格过滤（用市值过滤替代）。个股推荐池中的股票应基于市值+板块覆盖手动构建，而非价格过滤
- 新浪单次请求最多约 100 只股票，过多会被截断
- 板块排名用东方财富推送接口（`push2.eastmoney.com`），新浪不提供
- **东方财富板块排名API偶发空响应**：非硬依赖，可从个股评分聚类反推热点板块
- **Python urllib对东方财富K线API偶发SSL握手失败**（curl正常），建议脚本中用curl替代
- 科创板/创业板与主板的涨跌幅限制不同（20% vs 10%），计算涨幅时注意
- 新浪K线不含成交额和换手率，需要这些字段时用东方财富K线API
- **多源价格不一致**：同一股票在新浪、东方财富、Google Finance可能显示不同价格（价差可达5%+）。原因是数据源更新频率不同（新浪实时，东方财富2-5秒延迟，Google可能更滞后）。做分析时必须交叉验证：取3个来源中价差<2%的版本为准。价差>5%说明数据异常，需重新获取。查询用web_search配合web_extract快速验证。
- **除权除息日 hq 昨收 ≠ K线前收**：个股除息当天 hq 昨收字段是交易所调整后参考价（实测 2026-08-13 潍柴动力 hq昨收30.94 vs K线前收31.31），直接用K线对比会高估跌幅。日报表格用 hq 昨收算官方涨跌幅；与 verify_v2_daily.py（原始K线口径）数字不一致时先查除息，别当数据错误。

## 验证

### curl 直查
```bash
curl -s -H "Referer: https://finance.sina.com.cn" \
  "https://hq.sinajs.cn/list=sh688256" | iconv -f GBK -t UTF-8
```

### 脚本查询
```bash
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/sina_ashare.py quote sh688432
```

### 板块排名
```bash
python3 ~/.hermes/skills/finance/a-share-market-data/scripts/sina_ashare.py sectors --top 10
```
