# Baostock A股数据指南

验证时间：2026-07-25
环境：腾讯云轻量服务器 (43.138.221.174)
结论：**baostock 是本地唯一可用的A股历史数据源**（akshare/efinance/163 API全被墙）

## 为什么选baostock

| 数据源 | 协议 | 腾讯云可用 | 原因 |
|--------|------|:---------:|:-----|
| akshare | HTTP → EastMoney API | ❌ | 远程连接被拒绝 |
| efinance | HTTP → EastMoney API | ❌ | 远程连接被拒绝 |
| 163财经 | HTTP | ❌ | 502 Bad Gateway |
| Sina历史 | HTTP | ❌ | Service not valid |
| 新浪实时行情 | HTTP | ✅ | 一直可用 |
| **baostock** | **本地socket(TLS)** | **✅** | **走自有服务器，不受API封锁影响** |

Baostock走自己的服务器（local socket over TLS），不依赖EastMoney/新浪的HTTP API，所以在第三方API全被墙的情况下依然可用。

## 安装

```bash
pip install baostock
```

## 核心用法

### 登录/登出（每次查询前后必须调用）

```python
import baostock as bs
lg = bs.login()  # 返回 LoginResult，含 error_code/error_msg
# ... 查询 ...
bs.logout()
```

### 历史K线

```python
rs = bs.query_history_k_data_plus(
    "sz.000001",           # 格式: sz/shenzhen或sh/shanghai + 6位代码
    "date,open,high,low,close,volume,amount",
    start_date="2026-01-01",
    end_date="2026-07-24",
    frequency="d",          # d=日线, w=周线, m=月线, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟
    adjustflag="2"          # 1=后复权, 2=前复权, 3=不复权
)

rows = []
while rs.next():
    rows.append(rs.get_row_data())
```

返回值：每行是字符串列表，顺序同传入的field参数。需手动转float。

### 交易日期查询

```python
rs = bs.query_trade_dates(start_date="2026-01-01", end_date="2026-07-24")
# 返回日历信息，含 is_trading_day 字段
```

### 股票基本信息

```python
rs = bs.query_stock_basic(code="sz.000001")
# 返回：代码、名称、上市日期、退市日期、类型、状态
```

## 性能和限制

- 单次请求约 0.1-0.5 秒
- 日线数据范围：1990-至今
- 分钟线范围：约近2年
- **无明确的频率限制**，但建议不要超过10次/秒
- **无成分股/板块接口** → 需要手动维护股票池

## 股票代码格式

| 交易所 | 前缀 | 示例 |
|--------|------|------|
| 上证主板(6) | sh | sh600519 |
| 科创板(688) | sh | sh688256 |
| 深证主板(00) | sz | sz000001 |
| 创业板(300) | sz | sz300750 |
| 北交所(8) | bj | bj830799 |

## 与其它数据源配合使用

```
实时行情:   新浪 Finance (hq.sinajs.cn)  
历史K线:    Baostock  
板块排名:   东方财富推送API (push2.eastmoney.com)  
基本面:     Baostock (部分) 或 Web搜索
```
