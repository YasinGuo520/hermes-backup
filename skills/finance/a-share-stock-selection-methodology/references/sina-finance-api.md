# 新浪财经免费API参考

## 接口地址

```
GET https://hq.sinajs.cn/list={code1},{code2},...
```

## 必填请求头

```
Referer: https://finance.sina.com.cn
```

不加 Referer 返回 HTTP 403 Forbidden。

## 股票代码格式

| 前缀 | 适用 |
|------|------|
| `sh` | 上海主板 (`600`/`601`/`603`/`605`开头) + 科创板 (`688`开头) |
| `sz` | 深圳主板 (`000`/`001`/`002`开头) + 创业板 (`300`/`301`开头) |
| `bj` | 北交所 (`8`开头) |

## 响应格式

```
var hq_str_sh688256="寒武纪,1355.000,1369.750,1388.000,1439.980,1346.060,1387.990,1388.000,11875332,16641769701.000,15728,1388.000,0,0,0,0,0,0,0,0,0,0.000,0,0,0,0,0,0,0,0,2026-07-07,15:20:34,00,H|1600|2220800.00";
```

## 字段详细说明（逗号分隔）

| 索引 | 字段 | 类型 | 说明 |
|:----:|:----:|:----:|:----:|
| 0 | 股票名称 | str | 中文简称 |
| 1 | 开盘价 | float | 今日开盘价 |
| 2 | 昨收价 | float | 昨日收盘价 |
| 3 | 当前价 | float | 最新成交价 |
| 4 | 最高价 | float | 今日最高价 |
| 5 | 最低价 | float | 今日最低价 |
| 6 | 竞买价 | float | 买一价 |
| 7 | 竞卖价 | float | 卖一价 |
| 8 | 成交量 | int | 总成交量（手） |
| 9 | 成交额 | float | 总成交额（元） |
| 10 | 买一量 | int | |
| 11 | 买一价 | float | |
| 12 | 买二量 | int | |
| 13 | 买二价 | float | |
| 14 | 买三量 | int | |
| 15 | 买三价 | float | |
| 16 | 买四量 | int | |
| 17 | 买四价 | float | |
| 18 | 买五量 | int | |
| 19 | 买五价 | float | |
| 20 | 卖一量 | int | |
| 21 | 卖一价 | float | |
| 22 | 卖二量 | int | |
| 23 | 卖二价 | float | |
| 24 | 卖三量 | int | |
| 25 | 卖三价 | float | |
| 26 | 卖四量 | int | |
| 27 | 卖四价 | float | |
| 28 | 卖五量 | int | |
| 29 | 卖五价 | float | |
| 30 | 日期 | str | YYYY-MM-DD |
| 31 | 时间 | str | HH:MM:SS |

**注意**：部分字段可能在末尾附加元数据（如 `00,H|1600|2220800.00`）——股票状态标志，非标准字段。

## Python解析示例

```python
import re, urllib.request

url = "https://hq.sinajs.cn/list=sh688256"
req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
with urllib.request.urlopen(req) as resp:
    text = resp.read().decode("gbk")

match = re.search(r'"(.*?)"', text)
fields = match.group(1).split(",")

result = {
    "name": fields[0],
    "price": fields[3],
    "change_pct": round((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100, 2),
}
```

## 涨跌幅限制速查

| 板块 | 限制 | 涨停公式 |
|------|:----:|:--------:|
| 上海主板 | ±10% | 昨收 × 1.10 |
| 深圳主板 | ±10% | 昨收 × 1.10 |
| 科创板 (688) | ±20% | 昨收 × 1.20 |
| 创业板 (300/301) | ±20% | 昨收 × 1.20 |
| 北交所 (8) | ±30% | 昨收 × 1.30 |

涨停判断条件：`当前价 >= round(昨收 * 涨停倍率, 2)`
