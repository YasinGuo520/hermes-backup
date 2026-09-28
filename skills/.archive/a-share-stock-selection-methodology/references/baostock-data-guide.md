# Baostock A股数据源指南

验证时间：2026-07-25
环境：腾讯云轻量服务器（国内）

## 为什么用baostock

| 数据源 | 协议 | 国内服务器可用性 | 速度 | 延迟 |
|--------|------|:---------------:|:----:|:----:|
| **baostock** | TCP socket（本地协议） | ✅ 稳定 | 0.5s/500只 | 无（T+1） |
| akshare | HTTP（东方财富/网易API） | ❌ RemoteDisconnected | - | 15min |
| efinance | HTTP（东方财富API） | ❌ Connection aborted | - | 15min |
| 新浪财经（历史） | HTTP | ❌ Service not valid | - | 实时 |
| 网易财经 | HTTP | ❌ 502 Bad Gateway | - | 实时 |

**结论：国内服务器做A股量化，baostock是唯一可用的历史数据源。**

## 安装

```bash
pip install baostock
```

## 使用

### 登录/登出
```python
import baostock as bs
lg = bs.login()  # 必须调用，建立socket连接
# ... 查询 ...
bs.logout()      # 必须调用，关闭连接
```

**注意：** `login()`/`logout()` 不是幂等的。多次login会返回同一个session，但logout后需要重新login。建议在批量查询的循环外只login一次、logout一次。

### 获取日K线
```python
rs = bs.query_history_k_data_plus(
    "sz.000001",           # sh.600XXX 或 sz.000XXX
    "date,open,high,low,close,volume,amount",
    start_date='2026-01-01',
    end_date='2026-07-24',
    frequency='d',         # d=日线, w=周, m=月, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟
    adjustflag='2'         # 2=前复权, 1=后复权, 3=不复权
)
rows = []
while rs.next():
    rows.append(rs.get_row_data())
df = pd.DataFrame(rows, columns=['date','open','high','low','close','volume','amount'])
# 数值列需要手动转float
for c in ['open','high','low','close','volume','amount']:
    df[c] = df[c].astype(float)
```

### 代码前缀规则
```python
prefix = 'sh' if code.startswith('6') else 'sz'
# 沪市6开头 → sh.600XXX
# 深市0/3开头 → sz.000XXX / sz.300XXX
```

### 常用示例

**单个股票因子计算（含20日动量+波动率+量变）：**
```python
def compute_factors(code, start='2026-01-01', end='2026-07-24'):
    import baostock as bs, numpy as np, pandas as pd
    prefix = 'sh' if code.startswith('6') else 'sz'
    rs = bs.query_history_k_data_plus(
        f"{prefix}.{code}", "close,volume",
        start, end, 'd', '2'
    )
    rows = []
    while rs.next(): rows.append([float(x) for x in rs.get_row_data()])
    c = np.array([r[0] for r in rows])
    v = np.array([r[1] for r in rows])
    
    # 收益率
    r = c[1:] / c[:-1] - 1
    
    # 因子
    n = len(c)
    mom = np.full(n, np.nan)
    inv_vol = np.full(n, np.nan)
    vol_chg = np.full(n, np.nan)
    for j in range(20, n):
        mom[j] = c[j] / c[j-20] - 1
        inv_vol[j] = 1.0 / (np.std(r[j-20:j]) + 1e-8)
        vol_chg[j] = v[j] / v[j-20] - 1
    
    # 标准化+反转（A股呈现均值回归：负RankIC）
    def z(x): return (x - np.nanmean(x)) / (np.nanstd(x) + 1e-8)
    score = -(z(mom) + z(inv_vol) + z(vol_chg)) / 3
    return score[-1]  # 最新评分
```

## 已知问题

- **只支持日频及以上**：分钟线不保证可用
- **T+1数据**：今天收盘后约18:00才能查到今天数据
- **节假日**：baostock不返回节假日数据，日期序列不连续
- **退市/ST股票**：会返回空数据，检查 `len(rows)` 是否足够
- **不能高频调用**：连续大量查询需要加 `time.sleep(0.1)` 避免限流
- **无基本面数据**：需要基本面/财报数据需其他数据源补充

## 与新浪实时行情配合

```
历史数据: baostock (日K线, T+1延迟)
实时行情: hq.sinajs.cn (3秒延迟, 加Referer头)
板块排名: 从个股评分聚类反推 (东方财富API不可靠)
基本面:   待选数据源 (tushare pro 需付费)
```
