# A股API 工作区与已知陷阱

## 新浪财经 实时行情 API

**URL:** `https://hq.sinajs.cn/list=sh688256,sz002050,...`

### 关键规则
- 上证代码加 `sh` 前缀，深证代码加 `sz` 前缀
- 单次请求最多约 100 只
- **必须加 `Referer: https://finance.sina.com.cn` 头**，否则返回空
- 返回 GBK 编码（var hq_str_... = "..." 格式）

### 编码处理（Python）
```python
def curl_text(url: str) -> str:
    r = subprocess.run(["curl", "-s", "--max-time", "10", "-H",
                       "Referer: https://finance.sina.com.cn", url],
                      capture_output=True)  # 不能设 text=True！
    return r.stdout.decode("gbk").strip()
```

### 字段解析顺序
line.split('"')[1].split(",")
```python
# index: 字段
# 0:     股票名称
# 1:     今日开盘
# 2:     昨收
# 3:     当前价
# 4:     最高
# 5:     最低
# 8:     成交量(手)
# 9:     成交额(元)
# -3:    日期
# -2:    时间
```

## 新浪财经 K线 API

**URL:** `https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData`

### 参数
| 参数 | 值 | 说明 |
|------|-----|------|
| symbol | shXXXX / szXXXX | 上证sh前缀，深证sz前缀 |
| scale | 240=日线, 60=60分钟, 30=30分钟, 15=15分钟, 5=5分钟 |
| ma | no | 不需要均线 |
| datalen | 最多1023 | K线条数 |

### 响应格式（UTF-8 JSON）
```json
[
  {"day": "2026-07-09", "open": "1442.70", "high": "1476.01",
   "low": "1393.00", "close": "1475.88", "volume": "48577"},
  ...
]
```

### 注意
- **不需要 Referer 头**
- 字段是字符串，需要 float() 转换
- 不包含成交额、换手率

## 东方财富 板块排名 API

**URL:** `https://push2.eastmoney.com/api/qt/clist/get`

### 参数
| 参数 | 说明 | 行业板块 | 概念板块 |
|------|------|----------|----------|
| pn | 页码 | 1 | 1 |
| pz | 每页条数 | 10 | 10 |
| po | 排序方向 | 1=降序(涨幅) | 1=降序 |
| np | 是否分页 | 1 | 1 |
| fs | 板块筛选 | m:90+t:2 | m:90+t:3 |
| fields | 返回字段 | 见下文 | 见下文 |

### 推荐fields
- 精简: `f12,f14,f3`（代码/名称/涨幅）
- 完整: `f12,f14,f3,f62,f184,f66,f20,f21,f8`

### 已知陷阱
1. **偶发空响应**：深圳IP可能被限。重试1-2次通常恢复
2. **JSONP格式**：返回 `(json);` 或 `json);`，需要 strip 括号和分号
3. **频率限制**：每秒不超过2次

```python
raw = curl_text(url)
if raw:
    raw = raw.lstrip("(").rstrip(");")  # JSONP 清理
    data = json.loads(raw)
```

## 东方财富 K线 API

**URL:** `https://push2his.eastmoney.com/api/qt/stock/kline/get`

### 参数
| 参数 | 说明 | 值 |
|------|------|-----|
| secid | 交易所+代码 | 1.688256(沪), 0.002050(深) |
| klt | K线周期 | 101=日线, 60=60分钟, 102=周线 |
| fqt | 复权 | 1=前复权 |
| lmt | 条数 | 最多约1000 |
| end | 截止日期 | 20500101 表示最新 |

### 响应格式
```
日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
```

### 已知陷阱
- **Python urllib 偶发 TLS 断开**：Remote end closed connection without response。用 curl 替代
- **不常用此接口**：优先使用新浪K线API（更稳定）

## 简化的 curl 封装（推荐）

```python
import subprocess

def curl_get(url: str, referer: str = None, timeout: int = 10) -> str:
    """跨API统一的curl获取函数"""
    cmd = ["curl", "-s", f"--max-time", str(timeout)]
    if referer:
        cmd += ["-H", referer]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout+5)
        return r.stdout.decode("gbk", errors="replace").strip()
    except:
        return ""
```
