# data.json 桥接模式 — 让静态HTML获取动态数据

## 问题

纯静态HTML（`python3 -m http.server` 服务）无法直接读取本地文件或运行Python。但有些项目需要展示每日更新的数据（如量化推荐、日报、选品数据）。

## 方案

**Python脚本写JSON → HTML用fetch读取**，两层分离：

```
量化系统(cron 8:45) → 生成推荐JSON到logs/目录
      ↓
sync_quant_data.py(cron 8:50) → 读取最新日志 → 输出 data.json
      ↓
index.html 启动时 fetch('data.json?_t='+Date.now()) → 渲染到页面
```

## 基础实施步骤

### 1. 同步脚本结构

```python
#!/usr/bin/env python3
"""sync_data.py — 从数据源生成前端可读的data.json"""
import json, os, glob
from datetime import datetime

DATA_DIR = '/path/to/data/source'
OUTPUT = '/path/to/project/dir/data.json'

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.json')))
    if not files:
        return
    with open(files[-1]) as f:
        raw = json.load(f)
    
    output = {
        'date': raw.get('date', 'unknown'),
        'items': [],
        'updated_at': datetime.now().strftime('%H:%M'),
    }
    
    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
```

### 2. 前端fetch（异步加载）

```js
async function loadData() {
  try {
    const resp = await fetch('data.json?_t=' + Date.now());
    if (resp.ok) {
      const data = await resp.json();
      // 用data渲染页面
    }
  } catch(e) {
    console.log('加载数据失败，使用mock数据');
    // fallback to mock data
  }
}
```

### 3. Cron定时同步

```bash
cronjob(action='create', name='数据同步', schedule='50 8 * * 1-5',
        no_agent=True, script='sync_data.py', deliver='local')
```

## 变体1：实时服务器监控（/proc 数据桥接）

这个会话中创建的 `collect_stats.py` 展示了如何读取Linux内核的 `/proc` 文件系统来获取实时服务器数据：

### 数据采集脚本

```python
def get_cpu():
    stat = open('/proc/stat').read()
    for line in stat.split('\n'):
        if line.startswith('cpu '):
            parts = [int(x) for x in line.split()[1:]]
            total = sum(parts)
            return {
                'user': round(parts[0]/total*100, 1),
                'system': round(parts[2]/total*100, 1),
                'total': round((total-parts[3])/total*100, 1),
                'cores': os.cpu_count() or 1,
            }

def get_memory():
    mem = open('/proc/meminfo').read()
    d = {}
    for line in mem.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            d[k.strip()] = int(v.strip().split()[0]) // 1024
    total = d.get('MemTotal', 0)
    used = total - d.get('MemAvailable', 0)
    return {'total': f'{total}M', 'used': f'{used}M', 'percent': round(used/total*100,1)}

def get_disk():
    import subprocess
    result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
    # 解析 df 输出...
```

### 前端mock/real数据fallback模式

```js
(function(){
  // 先加载真实数据
  fetch('real_data.json?_t='+Date.now()).then(r=>r.json()).then(real=>{
    if(real && real.cpu) window._realData = real;
    renderAll();  // 第一次渲染用真实数据
  }).catch(()=>{
    renderAll();  // fallback用mock数据
  });

  // update() 函数检查是否有真实数据
  function update() {
    const rd = window._realData;
    if (rd) {
      // ── 用真实数据更新DOM ──
      updateWithRealData(rd);
    } else {
      // ── 模拟数据（兜底） ──
      updateWithMockData();
    }
  }
  
  // 自动定时刷新
  setInterval(function(){
    // 每5秒更新一次
    update();
  }, 5000);
})();
```

### 服务端口扫描

采集脚本还可以扫描哪些服务正在运行：

```python
def get_services():
    ports = [(8000,'服小助'),(8894,'简历'),(8895,'导航'),...]
    services = []
    for port, name in ports:
        alive = os.system(f'lsof -ti:{port} > /dev/null 2>&1') == 0
        services.append({'name': name, 'port': port, 'alive': alive})
    return services
```

## 变体2：量化推荐数据桥接（本例中实现）

从量化系统的每日推荐日志 → 前端看板：

1. 量化系统（cron 8:45）输出 `~/Desktop/hermes/quant-skill/logs/{date}.json`
2. `sync_quant_data.py`（cron 8:50）读取最新日志，转换格式并计算统计指标：
   - 信号一致性（tech/kronos/flow三方投票分歧度）
   - win_rate（分歧度低于阈值的比例）
   - 推荐股票列表（含code/name/score）
3. 输出 `data.json` 到 quant-board 目录
4. 前端页面 initApp() 中 fetch data.json → 替换mock持仓 → 更新K线标题和模型统计

## 坑

- **cron job脚本必须在 `~/.hermes/scripts/`**，符号链接受限，用cp复制
- **fetch路径**：`data.json` 相对于HTML文件路径，不是服务器根路径
- **缓存**：用 `?_t=` + 时间戳避免浏览器缓存data.json
- **fallback**：一定要写mock数据fallback，不然第一次加载或同步失败时页面白屏
- **异步时序**：fetch是异步的，如果init代码中先调用了render()再fetch，render会先用空数据渲染。解决方案：把fetch放到render之前，用 `.then()` 确保fetch完成后才调用第一次render
- **端口冲突**：重启服务器时旧进程可能没杀掉，用 `kill $(lsof -ti:{PORT}) 2>/dev/null; sleep 1` 确保端口释放
