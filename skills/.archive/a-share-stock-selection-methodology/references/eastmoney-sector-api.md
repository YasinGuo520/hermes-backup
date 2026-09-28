# 东方财富板块排名 API 参考

## 接口

```
GET https://push2.eastmoney.com/api/qt/clist/get
```

## 参数

| 参数 | 说明 | 行业板块值 | 概念板块值 |
|:----:|:----:|:----------:|:----------:|
| `pn` | 页码 | 1 | 1 |
| `pz` | 每页条数 | 20 | 20 |
| `po` | 排序方向 | 1=降序 | 1=降序 |
| `np` | 是否分页 | 1 | 1 |
| `fs` | 板块筛选 | `m:90+t:2` | `m:90+t:3` |
| `fields` | 返回字段 | 见下方 | 见下方 |

## 关键字段 (`fields` 参数)

| 字段 | 含义 |
|:----:|:----:|
| `f12` | 板块代码 |
| `f14` | 板块名称 |
| `f3` | 涨跌幅(%) |
| `f20` | 上涨家数 |
| `f21` | 下跌家数 |
| `f62` | 主力净流入 |
| `f66` | 领涨股代码 |
| `f184` | 领涨股涨跌幅 |
| `f8` | 换手率 |
| `f15` | 最高价 |

推荐 fields:
- 基础: `f12,f14,f3,f62,f184,f66,f20,f21`
- 详细: `f12,f14,f3,f62,f184,f66,f20,f21,f8,f15`

## curl 示例

### 行业板块涨幅TOP20

```bash
curl -s "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&fields=f12,f14,f3,f62,f184,f66,f20,f21&fs=m:90+t:2" | python3 -c "
import sys,json
raw = sys.stdin.read().strip().lstrip('(').rstrip(');')
data = json.loads(raw)
for i in data.get('data',{}).get('diff',[]):
    print(f\"{i['f14']}: {i['f3']}% | 涨{i['f20']}跌{i['f21']} | 领涨:{i.get('f66','')}\")
"
```

### 概念板块涨幅TOP20

```bash
curl -s "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&fields=f12,f14,f3,f62,f184,f66,f20,f21&fs=m:90+t:3" | python3 -c "
import sys,json
raw = sys.stdin.read().strip().lstrip('(').rstrip(');')
data = json.loads(raw)
for i in data.get('data',{}).get('diff',[]):
    print(f\"{i['f14']}: {i['f3']}% | 领涨:{i.get('f66','')}\")
"
```

## 注意事项

- 接口返回 JSONP 格式（带括号包裹），需要 strip `()` 或 `;` 后才能解析
- 没有 Referer 要求
- 数据约 3-5 秒延迟
- 频率限制：不要超过每秒 2 次请求
- 本接口非官方，可能随时变更

## 其他东方财富 API

| 用途 | URL |
|:----:|:----:|
| 沪深个股行情 | `https://push2.eastmoney.com/api/qt/stock/get` |
| 板块成分股 | `https://push2.eastmoney.com/api/qt/slist/get` |
| K线数据 | `https://push2his.eastmoney.com/api/qt/stock/kline/get` |
