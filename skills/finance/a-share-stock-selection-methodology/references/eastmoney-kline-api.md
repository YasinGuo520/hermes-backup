# 东方财富历史K线 API 参考

## 接口

```
GET https://push2his.eastmoney.com/api/qt/stock/kline/get
```

## 参数

| 参数 | 说明 | 示例 |
|:----:|:----:|:----:|
| `secid` | 交易所+代码 | `1.688256`（上证）, `0.002050`（深证） |
| `klt` | 周期 | `101`=日线, `102`=周线, `103`=月线, `60`=60分钟, `30`=30分钟 |
| `fqt` | 复权 | `1`=前复权, `2`=后复权, `0`=不复权 |
| `lmt` | 返回条数 | `1` ~ `1000` |
| `end` | 截止日期 | `20500101`（最大） |
| `fields1` | 固定 | `f1,f2,f3` |
| `fields2` | 返回字段 | `f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61` |

## fields2 字段说明

| 字段 | 含义 |
|:----:|:----:|
| `f51` | 日期/时间 |
| `f52` | 开盘价 |
| `f53` | 收盘价 |
| `f54` | 最高价 |
| `f55` | 最低价 |
| `f56` | 成交量（手） |
| `f57` | 成交额（元） |
| `f58` | 振幅（%） |
| `f59` | 涨跌幅（%） |
| `f60` | 涨跌额 |
| `f61` | 换手率（%） |

## 周期参数速查（klt）

| klt | 含义 | datalen推荐 | 说明 |
|:---:|:----:|:----------:|:----:|
| 5 | 5分钟 | 120 | 超级短线 |
| 15 | 15分钟 | 96 | 短线 |
| 30 | 30分钟 | 48 | 日内波段 |
| 60 | 60分钟 | 40-60 | 日内趋势/入场时机 |
| 101 | 日线 | 100-500 | 主分析周期 |
| 102 | 周线 | 30-100 | 大方向 |
| 103 | 月线 | 24-60 | 超长周期 |

## 响应格式

可能返回 JSONP 包裹，需清理后再解析：

```python
raw = raw.lstrip("(").rstrip(");")
data = json.loads(raw)
klines = data.get("data", {}).get("klines", [])
```

每条K线格式：`"2026-07-08,1423.00,1413.55,1479.31,1400.01,117177,16775188064.00,5.71,1.84,25.55,1.87"`

字段索引：0=日期, 1=开盘, 2=收盘, 3=最高, 4=最低, 5=成交量, 6=成交额, 7=振幅, 8=涨幅%, 9=涨跌额, 10=换手率%

## curl 示例

```bash
# 寒武纪 日线 前复权 100条
curl -s "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.688256&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&end=20500101&lmt=100"

# 华东医药 60分钟线
curl -s "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.000963&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=60&fqt=1&end=20500101&lmt=40"

# 中科曙光 周线
curl -s "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.603019&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=102&fqt=1&end=20500101&lmt=30"
```

## Python 全量获取示例

```python
import json, subprocess

def get_klines(code: str, period: str = "daily", limit: int = 100) -> list[dict]:
    klt = {"daily": "101", "weekly": "102", "60m": "60"}.get(period, "101")
    secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
    url = (f"https://push2his.eastmoney.com/api/qt/stock/kline/get"
           f"?secid={secid}&fields1=f1,f2,f3"
           f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
           f"&klt={klt}&fqt=1&end=20500101&lmt={limit}")
    raw = subprocess.run(["curl", "-s", url], capture_output=True, timeout=10).stdout.decode()
    raw = raw.lstrip("(").rstrip(");")
    data = json.loads(raw)
    klines = data.get("data", {}).get("klines", [])
    result = []
    for k in klines:
        parts = k.split(",")
        result.append({
            "date": parts[0],
            "open": float(parts[1]),
            "close": float(parts[2]),
            "high": float(parts[3]),
            "low": float(parts[4]),
            "volume": float(parts[5]),
            "amount": float(parts[6]),
            "amplitude": float(parts[7]),
            "change_pct": float(parts[8]),
            "turnover_rate": float(parts[10]),
        })
    return result
```

## Pitfalls

- Python `urllib` 的SSL握手可能失败（`Remote end closed connection`），**用 `curl` + `subprocess` 替代**
- 返回的是JSONP（带括号），不是纯JSON，需要清理
- 偶发空响应/超时，建议重试3次，间隔1秒
- 前复权和后复权数据不同（前复权=分红配股调整后的历史价格，更适合技术分析）
