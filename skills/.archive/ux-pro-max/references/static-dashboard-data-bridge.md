# 静态HTML看板 · 每日数据同步桥接模式

> 当需要把cron定时产生的数据（量化推荐、日报、选品数据等）展示在一个静态HTML页面上时，
> 用这个模式：Python工具桥 → data.json → HTML fetch，避免架设后端。

## 架构

```
量化系统(cron 8:45) → 写入 JSON 日志
        ↓
sync_quant_data.py(cron 8:50) → 读取最新日志 → 生成 data.json
        ↓
静态HTML页面 fetch('data.json') → 渲染数据
```

## 实现步骤

### 1. 创建桥接脚本

```python
#!/usr/bin/env python3
"""sync_xxx_data.py — 读取最新数据，输出为前端可用JSON"""
import json, os, glob
from datetime import datetime

# 配置
LOG_DIR = os.path.expanduser('~/Desktop/hermes/quant-skill/logs')
OUTPUT = os.path.expanduser('~/Desktop/hermes/quant-board/data.json')

def get_latest():
    logs = sorted(glob.glob(os.path.join(LOG_DIR, '*.json')))
    return logs[-1] if logs else None

def main():
    path = get_latest()
    if not path: return print('❌ 无数据')
    
    with open(path) as f:
        raw = json.load(f)
    
    output = {
        'date': raw.get('date', ''),
        'data': raw.get('top_k', []),
        'updated_at': datetime.now().strftime('%H:%M'),
    }
    
    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✅ 已同步 → {OUTPUT}")

if __name__ == '__main__':
    main()
```

### 2. HTML端加载数据

```javascript
async function loadData(){
  try{
    const resp = await fetch('data.json?_t=' + Date.now());
    if(!resp.ok) throw new Error('fetch failed');
    const data = await resp.json();
    if(data.data && data.data.length > 0){
      // 用真实数据替换mock
      myData.length = 0;
      data.data.forEach(item => myData.push(item));
      render();
    }
  } catch(e) {
    console.log('加载真实数据失败，使用mock', e.message);
    // 继续使用已有的mock数据
  }
}
loadData();
```

### 3. 设置定时同步

```bash
# 复制脚本到 ~/.hermes/scripts/
cp ~/Desktop/hermes/xxx-board/sync_xxx_data.py ~/.hermes/scripts/sync_xxx_data.py

# 创建cron job（Hermes内）
# cronjob action=create name="xxx数据同步" no_agent=true script=sync_xxx_data.py schedule="50 8 * * 1-5" deliver=local
```

## 坑

- **缓存问题**：浏览器可能缓存 data.json，fetch 时加 `?_t=${Date.now()}` 防缓存
- **路径问题**：data.json 必须和 HTML 在同一目录（否则 fetch 路径不对）
- **数据缺失**：HTML 必须要有 mock 数据兜底，不能完全依赖 data.json
- **Cron顺序**：同步脚本必须在数据源脚本之后执行（留5分钟缓冲）
