---
name: a-share-stock-selection-methodology
description: A股短线交易总纲 — 新浪/baostock行情数据获取 + 多因子量化选股 × 板块轮动 × 风控。覆盖从数据到命中的完整分析框架。
version: 2.1.0
tags: [finance, a-share, stock-selection, quantitative, short-term]
---

# A股短线选股方法论

## 触发条件

用户要求"推荐股票""分析板块""选股""明天哪些会涨""量化选股"时加载此 Skill。

## 中国A股显示规范

任何包含A股涨跌数据的界面（看板/表格/图表），必须使用中国标准配色：
- 红色 = 上涨 `#ef4444`
- 绿色 = 下跌 `#22c55e`
- 与西方惯例相反（西方绿涨红跌）

应用到：表格涨跌列、K线蜡烛、板块热力图、涨跌幅标签、盈亏显示。

```css
:root { --rise:#ef4444; --fall:#22c55e; --rise-dim:rgba(239,68,68,.12); --fall-dim:rgba(34,197,94,.12); }
```

## 分析框架（六大维度）

### ① 技术面（核心维度）
| 指标 | 用途 | 信号含义 |
|------|------|---------|
| 现价/MA5/MA20 | 位置判断 | 价在MA5上=强势，在MA20=支撑，跌破MA20=趋势走弱 |
| RSI14 | 超买超卖 | <30超卖反弹区，30-50偏弱，50-70偏强，>70超买 |
| MACD（金叉/死叉/零轴） | 趋势强度 | 零轴上金叉=最强，零轴下金叉=反弹，死叉=回避 |
| 布林带 | 波动率 | 价格触下轨+缩口=反弹，触上轨+张口=趋势延续 |
| KDJ | 短线超买超卖 | K<20超卖，D>80超买 |
| 成交量对比 | 量价配合 | 今日量/5日均量>1.5=放量启动，>2.5=异常放量需警惕出货 |

### ② 多周期共振
`必须三周期方向一致才推荐，减少70%假信号`
- **日线**（主趋势方向）
- **60分钟**（入场时机——找回调到支撑位的买点）
- **周线**（大方向——周线趋势向上才做多）

### ③ 资金面
| 数据 | 来源 | 用法 |
|------|------|------|
| 主力净流入/流出 | 东方财富/同花顺 API | 连续3日净流入=资金认可 |
| 北向资金 | 沪深港通 | 北向持续买入=外资看好 |
| 大单成交占比 | Level-2 | >30%大单占比=主力控盘 |
| 板块资金流向 | 东方财富板块排名 | 板块资金连续流入才选板块内个股 |

### ④ 基本面
| 指标 | 用法 |
|------|------|
| PE_TTM | 同行业对比，过高不追（除非高增长） |
| PE历史分位 | <20%分位=低估区，>80%分位=高估区 |
| PB | 重资产行业看PB |
| 市值 | 小盘股(<100亿)弹性大风险也大，中盘(100-500亿)兼顾弹性与机构参与度 |
| 复合增速 | 营收/利润连续3季增长才作为基本面加分项 |

### ⑤ 板块轮动
- 只推荐 **资金连续3日净流入** 的板块内的个股
- 板块指数涨幅 > 大盘涨幅 = 主线板块
- 板块内涨停股≥3只 = 板块效应确认
- **高切低**：涨了3天以上的板块不追，找刚启动的板块

### ⑥ 新闻/催化逻辑
- 政策利好、涨价逻辑、海外映射、业绩预告
- 来源：web_search（东方财富/华尔街见闻/格隆汇等）
- 区分"已兑现"和"待催化"——已兑现的利好不追

## 推荐输出格式

### 场景A：日常量化扫描（随机询问）

每只推荐股必须包含：

```
| 股票 | 代码 | 现价 | 今日涨跌 | RSI | MACD | 量比 | 支撑位 | 压力位 | 推荐理由 |
|------|------|------|---------|-----|------|------|--------|--------|---------|
```

**关键规则：**
- 每只股必须带：预期涨幅区间的价位参考 + 止损位（MA20或前低）
- 同时推荐不超过3只（用户注意力有限）

### 场景B：每日简报（8:45定时推送）

用户要求输出的**固定格式**，标题固定《量化次日潜力板块龙头参考简报》：
- **5个板块 × 每板块前5只龙头**（v4，2026-07-22升级）\n- 每只附带：量化评分/100、基础分、T+1持续性分、安全标签\n- 过滤条件：价格≤500元（原100元会漏掉宁德时代/寒武纪等龙头）、**流通市值≥100亿**（通过个股池预设保证，详见下方脚本说明）、剔除ST/*ST/退市股\n- 板块自动聚类：按板块内个股平均评分排序取**TOP5**\n- 每日自动推送（工作日8:45，cronjob ID: ea324446676f）

## ⭐ T+1趋势持续性评分体系（2026-07-09新增 v3）

A股是T+1交易（买入最早次日才能卖出）。推荐时必须考虑**次日能否顺利离场**，否则今天大涨明天低开反而亏。

> 详细代码实现见 `references/t1-scoring-system.md`

### 评分结构
```
总分 = 基础分(60%) + T+1持续性分(40%)
满分100，现实分布 -10~70
```

### T+1持续性分（40分封顶）— 5因子

| 因子 | 最高分 | 加分条件 | 减分条件 |
|:----|:-----:|:---------|:---------|
| ① 近3天趋势连续性 | 10分 | 连续3天上涨=10分，2天=7分 | 连跌3天=-2分 |
| ② RSI安全区 | 10分 | **40-60最安全**（明天还有空间） | >70=-5分（超买回调风险） |
| ③ MACD柱趋势持续性 | 8分 | 柱连3天扩大=趋势确认 | 持续萎缩=-3分 |
| ④ 距均线空间 | 7分 | 离MA5还有3%以上=补涨空间 | 已远离均线=-3分（追高） |
| ⑤ 单日涨幅不过热 | 5分 | 涨0-5%=温和健康 | >7%=-5分（获利盘抛压） |

### T+1安全性标签

| 标签 | T+1分 | 含义 |
|:----|:-----:|:-----|
| ✅ **T+1安全** | ≥15分 | 明天离场大概率有盈利空间 |
| ⚠️ **T+1需观察** | 0~14分 | 择机入场，注意仓位 |
| ❌ **T+1风险大** | <0分 | 明天可能低开，等回调 |

### 关键经验

- RSI 45-65是**最佳T+1区间**：既不过热也不弱势
- 单日涨幅>7%的票：今天追进去明天低开2-3%是常事
- **MACD柱连续扩大+RSI安全区** = 最可靠T+1信号组合

### 简报中的呈现

每只推荐股新增字段：
```
综合评分: 53/100 | 基础39+T+1持续性14
✅ T+1安全 | RSI48安全区 | MACD柱持续扩大 | 温和上涨1.0%
```

## 糅合量化系统 v2（全面技术指标 + 资金流）

### 概述

技术指标(RSI+MACD+KDJ+BOLL+MA+OBV) × Kronos-small × 资金流 三信号糅合系统。
2026-07-27升级至v2，取代v1的3因子均值回归模型。

**脚本位置：** `~/Desktop/hermes/quant-skill/quant_ensemble.py`

### 系统架构

```
┌──────────────────────────────────────────────┐
│  Data Layer                                  │
│  ├─ baostock (历史K线 — TCP协议最稳)          │
│  └─ 东方财富push2 (资金流向 — 有重试降级)      │
├──────────────────────────────────────────────┤
│  Signal Layer                                │
│  ├─ 技术因子(9维度综合) → RSI+MACD+KDJ+BOLL   │
│  │   +MA+量比+OBV+动量+波动率  权重 0.45     │
│  ├─ Kronos-small → K线形态预测  权重 0.30     │
│  └─ 资金流(主力净流入) → 东方财富API 权重0.25  │
├──────────────────────────────────────────────┤
│  Ensemble Layer                              │
│  ├─ 加权糅合 + z-score归一化(拉大差距)         │
│  ├─ 分歧度检测(>0.5跳过, >0.3标记观望)         │
│  └─ 自进化权重调优(每日15:30)                 │
└──────────────────────────────────────────────┘
```

### 技术指标详解（9维度评分）

每个指标输出[-1,+1]信号，加权后汇总。最后池内z-score归一化拉开差距。

| 维度 | 权重 | 信号逻辑 | 数据需求 |
|:----|:----:|:---------|:--------|
| RSI(14) | 10% | <30超卖→看多(+), >70超买→看空(-) | 60天close |
| MACD(12,26,9) | 15% | 柱正=看多, 柱负=看空; 金叉+0.5, 死叉-0.5 | 60天close |
| KDJ(9,3,3) | 8% | J<0超卖→看多, J>100超买→看空 | 60天high/low/close |
| BOLL(20,2) | 12% | 近下轨→看多, 近上轨→看空, 超出带宽信号加强 | 60天close |
| **MA排列** | **20%** | **价格相对MA5/10/20/60位置; 多头排列加分; 空头排列减分** | 60天close |
| 成交量 | 12% | 放量上涨→看多, 放量下跌→看空, 缩量调整→偏多 | 60天volume |
| OBV | 10% | 能量潮上升→看多, 下降→看空 | 60天close+volume |
| 短期动量 | 8% | 5天跌超5%→超跌反弹(+0.5), 5天涨超5%→过热(-0.3) | 6天close |
| 波动率 | 5% | 近期/历史波动比<0.7→蓄势偏多, >1.5→风险偏空 | 60天close |

### 资金流向

数据源: 东方财富push2 (`ulist.np/get?fields=f2,f3,f12,f14,f62`), f62=主力净流入
Referer头必须用 `https://quote.eastmoney.com/`, 重试2次, 失败降级运行.
主力净流入z-score归一化→tanh压缩→[-1,+1].

### 评分流程

```
① 数据获取 → baostock拉取历史K线(≥60天)
② 资金流向 → 东方财富查主力净流入(可降级)
③ 技术因子 → 9维度评分 → 加权汇总 → 池内z-score归一化
④ Kronos预测 → 本地缓存加载(local_files_only优先) → 预测20日方向
⑤ 糅合评分 → tech×0.45 + kronos×0.30 + flow×0.25
⑥ 分歧度检测 → <0.3 ✅推荐 / 0.3-0.5 ⚠️观望 / >0.5 ❌跳过
⑦ Top-8输出 + 技术指标分解 + 资金流Top5
```

### 每日运行

| 任务 | 时间 | 命令 | Cronjob ID |
|:----|:---:|:-----|:----------|
| 早盘Top-8 | 工作日8:45 | `quant_ensemble.py --top 8` | ea324446676f |
| 收盘自进化 | 工作日15:30 | **实际运行 `~/projects/quant_self_evolve.py --report-only`**（旧自进化脚本，只出报告不调权，**与v2日志不相通**，其累计准确率是旧口径）；v2验证由cron agent手动查Sina完成（见"每日自进化cron验证流程"） | 4b176d3f9c5e |

### 自进化机制

Softmax风格更新: 表现好的信号源加权重, 差的减权重.
约束: tech∈[0.15,0.60], kronos∈[0.10,0.50], flow∈[0.10,0.40]

### 文件结构

```
~/Desktop/hermes/quant-skill/\n├── quant_ensemble.py          # 主脚本(865行) v2\n├── quant_sectors.py           # 板块热点推荐(400行)\n├── weights.json               # 动态权重\n└── logs/                      # 每日推荐记录\n\n### 板块热点推荐系统 (quant_sectors.py)\n\n2026-07-27新增，独立于糅合选股的板块推荐系统。详见 `references/sector-recommendation.md`\n\n**核心逻辑：**\n- 数据源: baostock行业分类(`query_stock_industry` 索引3) + 总股本(`query_profit_data` 索引9) + 新浪行情\n- 行业名映射: 40+行业→短名带emoji (`J66货币金融服务`→`🏦银行`)\n- 市值过滤: ≥100亿（CSI300池子基本都满足）\n- 技术评分: 复用 `quant_ensemble` 的 `compute_tech_score` 函数\n- 板块排序: 按板块内前5只技术分均值排\n\n**用法：** `python3 quant_sectors.py --sectors 3 --stocks 3`\n\n| 数据获取 | 来源 | 时间 |\n|---------|------|------|\n| 行业分类 | baostock query_stock_industry | ~16s |\n| 总股本 | baostock query_profit_data | ~10s |\n| 日K线 | baostock query_history_k_data_plus | ~16s |\n| 实时价 | Sina hq.sinajs.cn | ~2s |
```

### 已知坑

| 问题 | 表现 | 修复 |
|:----|:-----|:-----|
| Kronos加载失败 | Connection reset | `local_files_only=True` 优先加载缓存 |
| **Kronos信号饱和** | **对所有股票都预测+1.0，失去区分度** | **检查Kronos是否退化为默认输出。如果连续3天>90%推荐kronos=+1.0，需降权重或重训模型** |
| baostock stock_basic | 格式要求 `sh.600000`(9位) | 加前缀 + `bs.login()` |
| **baostock API间歇性完全不可用** | **`bs.login()` 超时（9秒+），返回"网络接收错误"** | **几分钟后重试；切换到新浪财经K线API (`money.finance.sina.com.cn`) 作临时备选** |
| name字段索引 | 名称显示IPO日期 | 索引1是名称, 2是IPO日期 |
| 东方财富资金流API | 盘后空返回 | 加Referer头+重试2次; 失败降级 |
| **东方财富资金流API持续数天不可用** | **flow_score=0.0持续4+天，0.25权重完全浪费** | **加入自动检测：flow API连续N次失败则将其权重重新分配给tech/kronos，等API恢复再调回** |
| 技术分集中 | [-0.1,+0.1]无区分度 | z-score归一化+tanh放大 |
| **自进化验证门槛过高** | **`>=5`行行情记录的硬要求，新系统运行不足5天时永远无法触发调权** | **初始期（<10个交易日）把阈值降到`>=2`，积累足够数据后再升回`>=5`** |
| **早报cron超时无日志** | **8:45早报cron（ea324446676f）`TimeoutError: idle for 601s (limit 600s) — waiting for non-streaming API response`，当日 `logs/` 无JSON生成** | **DeepSeek早高峰API慢导致LLM cron超时。诊断：查 jobs.json 的 last_status/last_error 区分休市vs故障。修复：改 no_agent+script 直跑 `quant_ensemble.py --top 8`，绕过LLM API等待（0 token）** |

## 风险提示模板（每次必须带）

```
## ⚠️ 重要声明
1. **多因子量化数据分析结果，不构成投资建议**
2. 已过滤：流通市值≥100亿、ST/*ST/退市股、股价>500元
3. A股T+1交易，严格止损，单股≤20%仓位
4. T+1安全=明日离场有盈利空间 | T+1风险大=明天可能低开
```

## 量化扫描系统（已实现）

### 糅合系统（当前主力 — 全面技术指标 Ensemble v2）

当前每日早盘使用**糅合量化v2**（详见上节"糅合量化系统 v2"），取代旧版纯因子简报和v1糅合。

**脚本位置：** `~/Desktop/hermes/quant-skill/quant_ensemble.py`

**版本差异：**

| 维度 | v1 (3因子) | v2 (全面技术指标+资金流) |
|:----|:----------|:-------------------------|
| 信号源 | 动量+波动率+量变 | RSI+MACD+KDJ+BOLL+MA+量比+OBV+动量+波动率+资金流 |
| 因子数量 | 3个统计量 | 9维度技术指标 |
| 资金流 | 预留接口(未实现) | 已接入(东方财富,有重试降级) |
| 评分校准 | 原始z-score | 池内tanh放大归一化 |
| Kronos加载 | 外网下载 | 本地缓存优先 |
| 输出 | 总分+因子+Kronos | 总分+技术分解+资金流Top5 |
| 分歧度 | >0.5跳过 | >0.5跳过, 0.3-0.5观望(不跳过) |

### 历史系统（仍可使用）

旧版系统脚本在 `~/projects/` 下：

### 脚本1：quant_stock_scanner.py（全维度扫描）
- 17只核心观察股 × 8维度多因子评分（RSI/MACD/布林/KDJ/均线/量比/周线/风险收益比）
- 多周期：日线主趋势 + 周线大方向
- 评分满分100，现实分布 -20~+40，高分≥25
- 参考：`references/quant-scanner-implementation.md`
- 用法：`python3 ~/Desktop/hermes/quant_stock_scanner.py`

### 脚本2：daily_stock_brief.py（每日简报 v4 — 2026-07-22升级）\n- **73只个股**（覆盖14板块，每板块≥5只）× **8因子简化评分 + T+1趋势持续性5因子评分**\n- **数据源：新浪财经API**（`hq.sinajs.cn`）——2026-07-22确认东方财富批量报价API在多家服务器网络下持续返回空数据，已切换至Sina\n- **评分结构**：综合评分 = 基础分(最高60) + T+1持续性分(最高40)\n- **T+1安全性标签**：每只自带 ✅安全 / ⚠️需观察 / ❌风险大\n- **自动板块聚类**：分析后按板块聚合 → 取平均评分**TOP5** → 每板块选**TOP5**\n- **硬性过滤**：价格≤500元（v4放宽，原100元会漏掉宁德时代/寒武纪等高价龙头）、非ST/退市、**流通市值≥100亿**（通过个股池预设保证）\n- **预设题材催化库**：15+板块各有催化逻辑描述\n- **输出固定格式**：标题《量化次日潜力板块龙头参考简报》**5板块×5龙头**\n- **性能优化**：新浪批量行情获取（一次请求全部），单只K线请求间隔0.35秒防限流\n- 参考：`references/daily-stock-brief-implementation.md`\n- 脚本位置：`~/projects/daily_stock_brief.py`

### 定时推送（当前）

| 任务 | 时间 | Cronjob ID | 脚本 | 推送 |
|:----|:---:|:----------:|:----|:----|
| 早盘Top-8选股(v2) + 板块推荐 | 工作日8:45 | `ea324446676f` | `quant_ensemble.py --top 8` + `quant_sectors.py` | 飞书 |
| 收盘自进化 | 工作日15:30 | `4b176d3f9c5e` | `quant_ensemble.py --evolve --days 5` | 飞书 |

### 推荐效果验证流程

用户要求"看你昨天推荐的今天表现"时按以下步骤操作：

1. **批量获取实时行情**：新浪API一次性请求所有推荐股（逗号分隔多代码）
2. **计算今日涨跌**：涨跌幅 = (现价 - 昨收) / 昨收 × 100
3. **识别异常**：涨停（涨幅≥9.9%+封单大）、暴跌、停牌
4. **输出对比表**：
   ```
   | 股票 | 推荐价 | 现价 | 今日涨跌 | 状态 |
   ```
5. **总结统计**：上涨/下跌/涨停各多少只，平均涨幅，命中率

### 用户问"这个skill胜率如何/还有必要吗"

**直接给数字，别拉大盘对比。** 用户要的是本skill输出的实测胜率，不是指数基准分析。最短路径：

```bash
python3 ~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/verify_v2_daily.py ~/Desktop/hermes/quant-skill/logs --top 8
python3 ~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/backtest_quant_logs.py ~/Desktop/hermes/quant-skill/logs --top 8 --window 5
```

输出：累计命中率 + 平均涨幅 + 因子健康度红旗（flow全0/Kronos饱和）。**不要额外拉上证指数/沪深300做跑赢跑输对比**——除非用户明确要求，那是过度分析（2026-08-27被用户纠正："你在拉什么，直接统计最近这个skill输出的胜率效果就行啦"）。

**判定与建议：**
- 命中率 >65% 且跑赢大盘 = 健康
- **命中率 ≤50% = 抛硬币，不跟单，建议先停早报cron**（推了白推还烧token）
- 先分根因：数据源故障（flow因子空转/Kronos饱和）≠ 方法论失效——修好数据源前测不出真实水平
- skill保留价值在框架（评分体系/因子库/A股配色规范），不在每日清单

详细证据见 `references/win-rate-evaluation-2026-08.md`；开源替代调研（GitHub量化skill对比表+结论"无公开可验证A股高胜率skill"）+ **三个补丁改进路线**（①regime门控②因子IC验证/中性化③低波换手因子）见 `references/github-quant-skill-survey.md`

## 用户问"要不要开模拟盘/别人模拟盘效果如何"

**结论：公开世界没有可验证的「别人模拟盘战绩」**（大赛月赚40%冠军无一实盘复现；Guangli v22 只晒流程不晒战绩）。模拟盘胜率虚高三大因：成交理想化（涨停买不进）、零成本、心理差异——**纸面口径 > 模拟盘口径 > 实盘口径**。

模拟盘真正价值 = ①成交修正因子（想买的票实际成交几成，反推真实可执行胜率）②大盘环境分布（哪些日子该空仓）。执行模式抄 Guangli automation-spec（09:00筛选/09:30对账/14:00只卖、幂等键、T+1口径）。详见 `references/paper-trading-validation.md`

### 每日自进化cron验证流程（4b176d3f9c5e，工作日15:30）

收盘后验证当日早报推荐的固定流程（cron prompt已固化）：

1. **跑自进化报告**：`cd ~/projects && python3 quant_self_evolve.py --report-only`（⚠️ 这是**旧脚本**，其累计准确率口径与v2 logs**不相通**，只能看趋势不能当v2准确率）
2. **读当日v2日志**：`~/Desktop/hermes/quant-skill/logs/YYYY-MM-DD.json` → `top_k[]` 每项 `code`+`total`（总分0~1区间，直接填表格总分列）
3. **批量查行情**：新浪API（sh/sz前缀 + Referer头 + GBK），涨幅=(现价-昨收)/昨收×100
4. **输出表格**：代码|名称|昨收|收盘|涨幅|总分|结果(✅/❌)，最后合计涨跌只数、准确率、平均涨幅
5. **今日无日志处理**：先查 `~/.hermes/cron/jobs.json` 中 ea324446676f 的 `last_status`/`last_error` 区分原因——
   - 非交易日（周末/节假日）→ 跳过第二步，只输出自进化报告
   - cron故障（如TimeoutError）→ 如实报告故障原因 + 用**昨日推荐在今日收盘**的表现做替代验证（表格标注"替代验证"），并给出修复建议（把早报cron改 no_agent+script 直跑脚本绕过LLM API等待，0 token不依赖DeepSeek响应）

## 个股深度分析流程（用户问"XX接下来走势"时使用）

按以下五段结构输出：

### ① 关键数据表
| 指标 | 数值 | 含义 |
|------|:----:|------|
| RSI14 | X | 超卖(<30)/偏弱(30-50)/强势(50-65)/超买(>80) |
| MACD柱 | X | 正值且扩大=强势；负值且扩大=弱势 |
| MA5/MA20 | X/Y | 多头排列=价>MA5>MA20；空头排列=反 |
| MA60 | X | 长期生命线，强支撑/压力 |
| 高点到现价回撤 | X% | 回调深度判断 |

### ② 趋势判断
- **中期（1-2周）**：看均线排列+MACD方向 → 偏多/偏空/震荡
- **短期（下周初）**：看RSI是否超卖+是否接近支撑位 → 反弹概率

### ③ 关键价位图
```
压力② MA20=XX
压力① MA5=XX
── 当前价 XX ──
支撑① MA60=XX
支撑② 前低=XX
```

### ④ 情景推演表
| 情景 | 概率 | 触发条件 |
|:----|:---:|:---------|
| 超卖反弹 | ⭐⭐⭐⭐ | RSI<35+支撑位附近+大盘不差 |
| 惯性下跌 | ⭐⭐ | 跌破支撑+放量+大盘弱势 |
| 反转大涨 | ⭐ | 极小概率，需重大催化 |

### ⑤ 结论与操作建议
- 一句话判断 + 具体价格区间 + 止损位

## 数据源技术要点

| 场景 | 接口 | 关键参数 | 注意事项 |
|------|------|---------|---------|
| **历史K线（首选）** | **baostock（TCP socket）** `pip install baostock` 用法见 `references/baostock-data-guide.md` | `bs.query_history_k_data_plus("sh.600XXX","close,volume,amount","start","end","d","2")` | **国内服务器最稳定**，TCP协议绕过HTTP墙；前复权；T+1数据；登录后需logout |
| 实时行情（批量） | `https://hq.sinajs.cn`（首选，最稳定）或 `https://push2.eastmoney.com/api/qt/ulist.np/get`（备选，2026-07发现持续空数据不可靠） | Sina需加 `Referer: https://finance.sina.com.cn` 头+GBK解码；返回 `var hq_str_sh600519="..."` 格式，需剥离 `sh/sz` 前缀得到纯数字代码 | Sina单次请求最多约100只，Referer头格式必须精确 `-H "Referer: https://finance.sina.com.cn"`（缺少头字段名会导致403） |
| K线数据（日线） | `https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=shXXXX&scale=240&ma=no&datalen=N` | scale=240日线, 60=60分钟 | 返回UTF-8 JSON；datalen最大可取1023 |
| 板块排名 | `https://push2.eastmoney.com/api/qt/clist/get` | fs=m:90+t:2=行业板块, t:3=概念板块 | 返回JSONP需strip`()`；偶尔空响应需重试；频率≤2次/秒 |
| 东方财富K线 | `https://push2his.eastmoney.com/api/qt/stock/kline/get` | secid=1.代码(沪)/0.代码(深)；klt=101日线,60=60分 | Python urllib偶发TLS问题，建议用curl |

### GBK编码陷阱
新浪接口（hq.sinajs.cn）返回GBK编码。处理方式：
```python
# subprocess获取后decode
raw = subprocess.run(["curl", ...], capture_output=True).stdout
text = raw.decode("gbk")  # 不能用text=True，那会强制utf-8解码失败
```

## 中线波段选股（中报预增驱动） — 50%-100%潜力股筛选

### 触发条件
用户要求"推荐中线潜力股""波段上涨XX%""翻倍股""下半年能涨的XX股"时，使用本框架代替短线量化扫描。

### 核心差异：短线 vs 中线

| 维度 | 短线T+1 | 中线波段（本框架） |
|:----|:--------|:------------------|
| 持仓周期 | 1-3天 | 2周~3个月 |
| 目标涨幅 | 3-10% | 30-100% |
| 核心筛选 | 技术面+资金面 | 业绩预增+赛道阶段+机构目标价 |
| 主数据源 | K线/量比/RSI | 中报预告/机构研报/52周位置 |
| 入场方式 | 盘中追强 | 回调低吸+分批建仓 |
| 离场方式 | T+1次日卖出 | 分阶段减仓（T1/T2/T-clear） |

### 五步筛选漏斗

**第一步：业绩预增粗筛**
用 `web_search` 筛选中报预增>150%的科技股。优先扣非增速>营收增速的标的（主业改善，非一次性收益）。
搜索示例：`2026 中报预增 净利润翻倍 科技股 AI 半导体`

**第二步：赛道阶段验证**
判断细分赛道处于哪个阶段才能选对弹性最大的窗口：

| 阶段 | 识别标志 | 操作 |
|:----|:---------|:----|
| 🔥 刚启动 | 板块连续流入<5天，涨停<3家 | **优先买入**，弹性最大 |
| 🌊 主升浪 | 板块涨幅>50%，龙头已翻倍 | 可持有但控制仓位 |
| ⚠️ 高位震荡 | 龙头涨3倍+，资金开始轮动 | 不追，等回调 |
| ❌ 见顶回落 | 板块跌幅>15%，机构降级 | 不碰 |

**第三步：价格位置确认**
- 现价在52周范围 **30%-60%分位**（到前高还有40-70%空间）
- 优先 **市值50-200亿**中小盘
- **多源价格交叉验证**：新浪+东方财富+Google Finance取价差<2%版本（A股数据源价差可达5%+）

**第四步：机构目标价对照**
- 机构目标价 > 当前价×150% → 有50%+空间 → 通过
- 无机构覆盖 → 小盘高弹性但风险更高

**第五步：披露时间窗口**
| 时间 | 操作 |
|:----|:-----|
| 业绩预告当天 | 通常是洗盘日，等2-3天 |
| 预告后1-2周 | **最佳建仓窗口** |
| 正式半年报前2周 | 减仓一半 |
| 半年报披露当天 | 清仓 |

### 输出格式
每只推荐必须包含：当前价、市值、中报预增幅度、赛道阶段、52周位置、机构目标价空间、买入区间、两档目标减仓价、止损价、特有风险点。

### 5只推荐组合规则
- 固定5只，每只1/5仓位
- 覆盖至少3个不同细分赛道
- 至少2只市值<100亿（弹性）+1只>200亿（底仓稳）
- 至少3只处于"刚启动"阶段
- 每周复盘淘汰逻辑破坏的

### 常见陷阱（中线版）
- ❌ 推荐已从低点翻倍的股（空间透支）
- ❌ 单一赛道集中（板块退潮全亏）
- ❌ 只看营收不看扣非增速（一次性收益不持续）
- ❌ 不设止损（50%目标对应30%回撤是正常波动）
- ❌ 追涨停建中线仓（等3天回调确认）
- ✅ 区分"已兑现利好"和"待兑现催化"

## AI基础模型融合

当用户询问"AI选股""基础模型""Kronos""强化学习量化""MCP量化工具"等话题时，参见：
- `references/ai-model-fusion-top10.md` — Top 10工具全景对比与融合方案
- `references/kronos-cpu-deployment.md` — Kronos在CPU部署的避坑指南
- `references/signal-validation-workflow.md` — 量化信号验证标准流程

### 当前部署状态（已上线）<br>Kronos-small + 全面技术指标 + 资金流 Ensemble v2 系统已部署运行，详见上节"糅合量化系统 v2"。

| 项目 | 状态 | 路径 |
|:----|:----:|:-----|
| Kronos-small CPU推理 | ✅ 本地缓存加载 | `~/Desktop/hermes/kronos-repo/` |
| 全面技术指标+资金流糅合选股 | ✅ 每日运行(v2) | `~/Desktop/hermes/quant-skill/quant_ensemble.py` |
| 自进化权重调优 | ✅ 每日运行 | `--evolve` 模式 |
| 资金流信号 | ✅ 已接入(东方财富) | 有重试降级机制 |

### 核心原则

传统因子系统和AI基础模型是**互补关系**。Kronos擅长K线形态模式提取（价格结构/波动率模式），因子系统擅长均值回归/资金面。两种错误来源不同，Ensemble后整体误差下降。

### 2026-07-25实测结论

| 项目 | 结果 | 含义 |
|------|:----:|------|
| 传统因子(K线动量+波动率+量变) | RankIC=-0.23, ICIR=-0.73 | **强负相关=均值回归主导**，反着用预期RankIC=+0.23 |
| Kronos-small方向预测(5只) | 100%准确 | CPU可跑，方向信号值得深挖，但样本不足 |
| 糅合可行性 | 正交互补 | 因子看大势反转，Kronos看价格形态，互补性高 |

### A股特殊发现：因子方向反转

2026年上半年实测显示：**简单动量因子在A股呈现强负IC（RankIC=-0.23）**。

这意味在这段时间里，A股更倾向于**均值回归**而非追涨——涨多了的要跌，跌多了的要涨。而非美股常见的动量效应（涨的继续涨）。

处理方式：
- 传统因子系统应该**同时测试正负方向**，不要假设动量一定有效
- 加入因子方向自动检测：每月计算一次各因子RankIC，方向跟着走
- 多因子框架中允许因子权重可正可负

### 融合路径优先级

| 方案 | 准确率 | 复杂度 | 说明 |
|:----|:-----:|:------:|:-----|
| **Ensemble集成** | ★★★ | 高 | Kronos+FinRL+因子+资金流→元模型加权 |
| **Kronos信号作为新因子** | ★★☆ | 低 | 最快落地，喂进现有打分系统 |
| **Kronos主+因子验证** | ★★☆ | 中 | 保守型，但会误杀正确信号 |

推荐先走**Kronos信号作为新因子**路径：1天落地，跑1个月看RankIC增量。

### 实施

1. `pip install kronos-model-arch` → Kronos-mini(4M参数CPU可跑)
2. 数据源：**baostock**（最稳）→ `pip install baostock`（详情见 `references/baostock-data-guide.md`）
3. Kronos输出RankIC信号作为第N+1个因子加入现有打分
4. 跑1个月监控RankIC增量 > 再决定是否升级到Ensemble

> 模型输出是原始预测信号，不是交易信号。实盘需组合优化+冲击成本建模。

## 常见陷阱

- **别追连续涨停后的高位股**（利好已兑现，获利盘随时砸）
- **别只看当天跌幅大的"便宜"股**（可能趋势已走坏）
- **别在下午2:30后推荐**（尾盘资金行为无法反映次日）
- **大盘单日跌超1%时不推荐买入**（系统性风险覆盖个股逻辑）
- **前日涨停的股次日高开不追**（大概率利好兑现出货）
- **baostock query_stock_basic 代码格式**：必须用 `sh.600000`(9位含前缀)，只用数字代码会报"股票代码应为9位"。必须先 `bs.login()` 再查
- **baostock stock_basic 返回索引**：索引0=code, 1=name(中文名), 2=ipoDate。取name要用索引1不是2
- **Kronos加载失败**：国内服务器从huggingface.co下载会Connection reset。优先 `local_files_only=True` 从 `~/.cache/huggingface/hub/` 加载
- **东方财富push2资金流API盘后不稳定**：尤其非交易时段经常返回空。加Referer头+重试2次，失败自动降级不影响主体评分\n- **东方财富批量行情API（push2.eastmoney.com/api/qt/ulist.np/get）不可靠**：2026-07-22确认在多家服务器网络下持续返回空数据。**勿作行情主数据源**，优先用新浪`hq.sinajs.cn`。如需流通市值字段，通过个股池预设+手动维护实现\n- **新浪行情代码必须剥离交易所前缀**：Sina返回`var hq_str_sh600519="..."`格式，`sh600519`需提取为`600519`，否则与股票池数字代码不匹配\n- **curl -H参数格式必须精确**：`-H "Referer: https://finance.sina.com.cn"`（含头字段名），不能只有值\n- **A股价格过滤不宜设100元**：宁德时代382元、寒武纪1350元、迈瑞医疗152元等蓝筹皆超100元，设100会漏掉核心龙头。建议上限500或跳过价格过滤纯用市值\n- **新浪实时行情必须加Referer头**：否则返回403
- **A股因子方向会变化**：2026年上半年实测显示简单动量因子的RankIC为-0.23（强负相关），说明当期A股以均值回归为主而非追涨。**不要假设因子方向永远不变**，建议每月重算各因子RankIC，方向跟着走。多因子框架应允许权重可正可负

---

## 市场数据获取速查（合并自 a-share-market-data）

> 原独立技能 a-share-market-data 已并入本技能。数据获取脚本与参考资料全部在本技能目录下，**路径已更新**：
> - 脚本：`~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/`（sina_ashare.py / backtest_quant_logs.py / verify_v2_daily.py）
> - 参考：`references/sina-finance-api.md` / `eastmoney-kline-api.md` / `eastmoney-sector-api.md` / `baostock-data-guide.md`（另存 `baostock-data-guide-market-data.md` 为市场数据版）/ `quant-recommendation-verification.md` / `quant-cron-drift-diagnosis.md` / `quant-ensemble-health-diagnostics.md`

### 实时行情（首选新浪）
```bash
curl -s -H "Referer: https://finance.sina.com.cn" "https://hq.sinajs.cn/list=sh688256,sz002185" | iconv -f GBK -t UTF-8
```
- 字段索引（逗号分隔，从0起）：0名称 1开盘 2昨收 3当前价 4最高 5最低 8成交量 9成交额；涨跌幅=(当前-昨收)/昨收
- **必须带 `Referer: https://finance.sina.com.cn` 头**（否则403）；GBK 解码（`subprocess.run` 别用 text=True，用 `capture_output=True` 再 `.decode('gbk')`）
- 单次请求 ≤30只（超了 Connection reset）；代码剥离 sh/sz 前缀与股票池匹配
- **除权除息日口径**：hq 昨收是交易所调整后参考价、K线前收是原始价（实测潍柴动力差一个分红幅度）——日报用 hq 口径，累计准确率用脚本口径并注明差异

### K线数据源（按稳定性）
1. **baostock**（TCP socket，国内最稳，不走HTTP）：`bs.login()` → `query_history_k_data_plus("sh.600000","close,volume,amount",start,end,"d","2")` → `bs.logout()`；行业分类 `query_stock_industry()`（索引1=code含前缀, 3=industry）；总股本 `query_profit_data()`（索引9）；股票名 `query_stock_basic()`（**索引1=名称，索引2=IPO日期**——取错显示成日期）
2. **新浪K线**（HTTP最稳）：`https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh688256&scale=240&ma=no&datalen=100`（scale=240日线/60=60分钟；无Referer要求；不含成交额/换手率）
3. **东方财富K线**（含换手率/成交额）：`https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600000&klt=101&fqt=1&lmt=100`（secid: 1.=沪 0.=深；klt=101日线/102周线/60=60分；urllib 偶发 SSL 失败用 curl）

### 板块排名
`https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fields=f12,f14,f3,f62,f184,f66&fs=m:90+t:2`（t:2=行业 t:3=概念；f3=涨跌幅 f14=板块名 f62=主力净流入）；JSONP 需 strip 括号；偶发空响应重试；频率≤2次/秒。

### 资金流向
东财 `push2.eastmoney.com/api/qt/ulist.np/get?fields=f2,f3,f12,f14,f62` 的 f62=主力净流入（元）；**盘后/非交易时段常空响应**（Connection reset），交易时段较稳；Referer 必须 `https://quote.eastmoney.com/`；失败自动降级不阻塞主评分。

### 验证与回测脚本（路径已更新）
```bash
# 批量行情（quote）+ 板块排名（sectors / concept）
python3 ~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/sina_ashare.py quote sh688432 sz002185
python3 ~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/sina_ashare.py sectors --top 10
# 多日回测 + 因子健康度（Kronos饱和/flow全0/重复代码 红旗检测）
python3 ~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/backtest_quant_logs.py ~/Desktop/hermes/quant-skill/logs --top 8 --window 5
# 当日口径累计准确率（推荐日收盘 vs 前一交易日收盘；T+1口径用 backtest 脚本）
python3 ~/.hermes/skills/finance/a-share-stock-selection-methodology/scripts/verify_v2_daily.py ~/Desktop/hermes/quant-skill/logs --top 8
```
- **因子失效红旗**：Kronos 连续全 1.0/0.0 = 信号饱和（strength 放大系数降到 2~3）；flow 连续全 0 = 东财 API 空转（权重自动重分配）；top_k 反复同批代码 = 只剩 MA 排序在推大盘蓝筹
- **cron 无日志排查**：先查 `~/.hermes/cron/jobs.json` 的 last_status/last_error 区分休市 vs 故障；`RuntimeError: Skipped to prevent unintended spend: global inference config drifted` = 模型配置漂移被安全守卫拦截（**不是非交易日**）→ 改回 config.yaml + jobs.json 四字段（provider/model/provider_snapshot/model_snapshot）

