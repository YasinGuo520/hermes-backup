# 实时数据看板实现示例

本会话中实现的两个实时数据看板案例。

## 案例1：服务器状态页 (8917)

### 采集脚本
`~/Desktop/hermes/server-status/collect_stats.py`

数据源：/proc/stat, /proc/meminfo, df, /proc/net/dev, /proc/uptime

### 前端读取
`~/Desktop/hermes/server-status/index.html` 中的JS：
- 初始化时 fetch('real_data.json?_t=...') 
- 存到 window._realData
- render() 函数优先用真实数据，没有则 mock 兜底

### cron
每5分钟执行一次 `collect_stats.py`，no_agent=true

## 案例2：量化K线看板 (8912)

### 采集脚本
`~/Desktop/hermes/quant-board/sync_quant_data.py`

数据源：`~/Desktop/hermes/quant-skill/logs/{date}.json`（量化系统每日推荐输出）

### 前端读取
`~/Desktop/hermes/quant-board/index.html` 中的 initApp()：
- 加载时 fetch('data.json?_t=...')
- 替换 positions 数组为真实推荐股票
- 更新模型表现数据

### cron
每个交易日8:50执行（量化系统8:45出结果后5分钟）
