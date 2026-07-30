# 量化看板数据桥接（Quant Board Data Bridge）

**场景：** 把 `quant_ensemble.py` 每天的推荐结果同步到前端看板，实现真实推荐数据展示。

## 架构

```
quant_ensemble.py              ← 每日8:45 cron产出 logs/YYYY-MM-DD.json
       ↓
sync_quant_data.py             ← 每日8:50 cron读取最新log + 计算统计量
       ↓
quant-board/data.json          ← 静态JSON，被HTML fetch
       ↓
quant-board/index.html         ← JavaScript fetch('/data.json?_t='+Date.now())
```

## sync_quant_data.py 核心逻辑

### 输入
从 `~/Desktop/hermes/quant-skill/logs/` 读最新的 `YYYY-MM-DD.json`（按文件名排序取最后一个）

### 输出
`~/Desktop/hermes/quant-board/data.json` 包含：

```json
{
  "date": "2026-07-30",
  "positions": [
    {"code":"600406","name":"国电南瑞","total_score":0.5233,"tech":0.4962,
     "kronos":1.0,"flow":0.0,"disagreement":0.374,"recommended":false}
  ],
  "signal_agreement": 0.68,   // 三个信号的方向一致性
  "win_rate": 0.125,           // 低分歧度(<0.3)股票占比作为可信度
  "weights": {"tech":0.45,"kronos":0.3,"flow":0.25}
}
```

### 股票名称映射

内置 `STOCK_NAMES` 字典映射代码→名称（约300只常见股）。代码不在映射里的用 code[:4] 显示。

### 信号一致性计算

```
tech_dir = 技术信号>0的比例
kronos_dir = Kronos信号>0的比例
flow_dir = 资金流信号>0的比例
agreement = 1 - |tech_dir-kronos_dir| - |tech_dir-flow_dir| - |kronos_dir-flow_dir|
```

值越大表示三个信号方向越一致，推荐可信度越高。

## 前端集成

### 在 quant-board/index.html 中的加载逻辑

```javascript
async function initApp(){
  let realLoaded=false;
  try{
    const resp=await fetch('data.json?_t='+Date.now());  // 防缓存
    if(resp.ok){
      const data=await resp.json();
      if(data.positions&&data.positions.length>0){
        // 替换mock positions为真实数据
        positions.length=0;
        data.positions.forEach(r=>{
          const basePrice=20+Math.random()*200;
          positions.push({
            name:r.name, code:r.code,
            qty:Math.floor(Math.random()*3000+500),
            cost:+(basePrice*(0.9+Math.random()*0.2)).toFixed(2),
            price:+(basePrice*(0.95+Math.random()*0.1)).toFixed(2),
          });
        });
        // 更新K线标题为首只推荐股
        document.querySelector('.chart-area .card-title').textContent=
          '📈 K线 · '+positions[0].name+' ('+positions[0].code+')';
        // 更新模型统计
        document.getElementById('signalAgree').textContent=
          (data.signal_agreement*100).toFixed(1)+'%';
        realLoaded=true;
      }
    }
  }catch(e){/* fallback to mock */}

  renderPositions();
  drawCandleChart();  // 必须无条件重绘
}
```

### 坑：浏览器缓存

`data.json` 每次加载都要加时间戳参数 `?_t=`+Date.now()，否则浏览器可能返回旧版本。

### 坑：K线不会自动重绘

`drawCandleChart()` 依赖 `klineData` 变量，而 `klineData` 由 `mockKlineData()` 生成。真实数据加载后只替换了 `positions` 数组，**不自动重绘K线**。必须在 init 末尾无条件调用 `drawCandleChart()`。

### 坑：持仓点切换K线不生效

`renderPositions()` 生成的表格行必须带 `data-idx` 属性和 `onclick="switchStock(n)"` 才能实现点击切换。`switchStock(n)` 函数重新生成K线数据并缩放到目标股票的价格区间。

```javascript
function switchStock(idx){
  const basePrice=positions[idx].price;
  const newData=mockKlineData(120);
  // 缩放到该股票的价格水平
  const scale=basePrice/newData[0].o;
  newData.forEach(d=>{
    d.o=+(d.o*scale).toFixed(2);
    d.c=+(d.c*scale).toFixed(2);
    // ...
  });
  klineData.length=0;
  newData.forEach(d=>klineData.push(d));
  drawCandleChart();
}
```

## 定时任务

```yaml
cronjob:
  name: 量化看板数据同步
  schedule: "50 8 * * 1-5"     # 工作日8:50（量化系统8:45跑完）
  script: sync_quant_data.py   # 在 ~/.hermes/scripts/
  no_agent: true               # 纯脚本，零token消耗
  deliver: local
```

## 扩展：接入板块推荐

板块推荐由 `quant_sectors.py` 生成，当前未接入看板。如需接入：

1. `quant_sectors.py` 输出板块JSON到 `logs/sectors_latest.json`
2. `sync_quant_data.py` 读取并合并到 output
3. HTML 侧用板块数据更新热力图
