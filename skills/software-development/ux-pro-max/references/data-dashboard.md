---
name: data-dashboard
description: Build single-file HTML data dashboards with sci-fi dark themes — sortable tables, Canvas/CSS charts, heatmaps, animated stat counters. Covers Monitor-surface composition, data visualization patterns, and Chinese e-commerce dashboard conventions.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dashboard, data-viz, html, chart, canvas, dark-theme, ecommerce, chinese, monitor-surface]
    related_skills: [claude-design, popular-web-designs]
---

# Data Dashboard Patterns

Use when the user asks for a "dashboard", "大屏", "看板", "monitor", "analytics page",
or data-heavy HTML page with tables, charts, and stats.

## Surface Classification

All data dashboards are **Monitor** surfaces:

- Density and glanceability beat hero layouts
- Stats row at top is the standard entry point
- No centered hero, no feature-tile card grid
- The composition answers: *what changed, what needs attention, what do I decide*

## Dashboard Layout Recipe

```
┌─────────────────────────────────────────────┐
│              Title Header                    │
├──────────┬──────────┬──────────┬────────────┤
│  Stat 1  │  Stat 2  │  Stat 3  │  Stat 4   │
├──────────┴──────────┴──────────┴────────────┤
│                    │                         │
│   Data Table /     │   Charts / Viz         │
│   Rankings         │                         │
│                    ├──────────┬──────────────┤
│                    │  Chart 1 │  Chart 2     │
├────────────────────┴──────────┴──────────────┤
│           Heatmap / Overview                 │
└─────────────────────────────────────────────┘
```

Use CSS Grid for the main layout. Place the table column spanning 2 rows when it's
the primary content, charts in the right column.

## Sci-Fi Dark Theme Recipe

| Token            | Value      | Usage                              |
|------------------|------------|------------------------------------|
| bg               | `#0a0e1a`  | Body background                    |
| card bg          | `#101830`  | Card surface                       |
| grid line        | `rgba(0,212,255,.04)` | Background grid          |
| accent-primary   | `#00d4ff`  | Active borders, glow, headings     |
| accent-secondary | `#7b61ff`  | Chart second gradient color        |
| accent-tertiary  | `#ff6ec7`  | High-value highlights              |
| accent-gold      | `#ffd700`  | #1 ranking, price values           |
| text-primary     | `#c8d6e5`  | Body text                          |
| text-muted       | `#4a6a8a`  | Table headers, secondary labels    |
| border           | `rgba(0,212,255,.12)` | Card borders             |
| glow             | `0 0 12px rgba(0,212,255,.3)` | Element glow       |

### Implementation

```css
body {
  background: #0a0e1a; color: #c8d6e5;
}
body::before {              /* grid overlay */
  content: ''; position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(0,212,255,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,.04) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none; z-index: 0;
}
.card {
  background: linear-gradient(135deg, rgba(16,24,48,.92), rgba(10,14,36,.96));
  border: 1px solid rgba(0,212,255,.12); border-radius: 12px;
}
.card::before {             /* top glow border */
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  opacity: .5;
}
```

## Data Viz Techniques

### 1. Canvas Doughnut Chart

For category distribution / percentage breakdowns:

```js
const ctx = canvas.getContext('2d');
const cx = w/2, cy = h/2;
let start = -Math.PI/2;
entries.forEach(([label, value], i) => {
  const slice = value/total * Math.PI*2;
  ctx.beginPath();
  ctx.arc(cx, cy, outerR, start, start+slice);
  ctx.arc(cx, cy, innerR, start+slice, start, true); // reverse for doughnut
  ctx.closePath();
  ctx.fillStyle = colors[i]; ctx.fill();
  ctx.shadowColor = colors[i]; ctx.shadowBlur = 8; // glow
  ctx.fill();
  ctx.shadowBlur = 0;
  start += slice;
});
```

Key: treat `innerR` for ring (doughnut) shape; `ctx.shadowBlur` for per-segment glow.

### 2. CSS Horizontal Bar (table row bars)

For sales volume / rank bars embedded in cells:

```html
<div class="sale-bar-outer">
  <div class="sale-bar-inner" style="width:${pct}%"></div>
</div>
```

Normalize: `pct = (item.value / maxValue * 100).toFixed(1)`

### 3. CSS Vertical Bar Chart (distribution)

For price ranges, time buckets:

`display:flex; align-items:flex-end` on container; `flex-direction:column; align-items:center` on each column.
Add `min-height:4px` and `transition:height .8s ease` on bars.

### 4. CSS Heatmap Grid

For cross-dimensional data (category × price range):

```css
.heat-grid { display:grid; gap:4px; grid-template-columns:repeat(N, 1fr); }
.heat-cell { aspect-ratio:1; border-radius:3px; }
.heat-cell:hover { transform:scale(1.08); }
```

Color mapping: array from dark (low) to bright (high):

```js
const colors = ['#0a1628','#1a3a5c','#2a6a9e','#4a9ad4','#7b61ff','#ff6ec7','#ffd700'];
const idx = Math.min(colors.length-1, Math.floor(value / maxValue * colors.length));
```

### 5. Animated Stat Counters

```js
function animate(el, target) {
  let cur = 0; const step = Math.max(1, Math.floor(target / 30));
  const timer = setInterval(() => {
    cur = Math.min(cur + step, target);
    el.textContent = fmt(cur);
    if (cur >= target) clearInterval(timer);
  }, 25);
}
```

## Sortable Table Pattern

```js
let sortKey = 'rank', sortDir = 'asc';

function render() {
  let items = [...data].sort((a,b) => {
    if (typeof a[sortKey] === 'number')
      return sortDir==='asc' ? a[sortKey]-b[sortKey] : b[sortKey]-a[sortKey];
    return sortDir==='asc'
      ? String(a[sortKey]).localeCompare(String(b[sortKey]))
      : String(b[sortKey]).localeCompare(String(a[sortKey]));
  });
  // render rows...
}

th.addEventListener('click', () => {
  if (currentKey === key) sortDir = flip(sortDir);
  else { sortKey = key; sortDir = 'asc'; }
  updateIndicators();
  render();
});
```

## Rank & Badge Styling

```css
.rank-1 { color:#ffd700; text-shadow:0 0 12px rgba(255,215,0,.4); }
.rank-2 { color:#c0c0c0; text-shadow:0 0 8px rgba(192,192,192,.3); }
.rank-3 { color:#cd7f32; text-shadow:0 0 8px rgba(205,127,50,.3); }

.comm-high { background:rgba(255,110,199,.2); color:#ff6ec7; }
.comm-mid  { background:rgba(123,97,255,.2);  color:#b8a5ff; }
.comm-low  { background:rgba(0,212,255,.15);  color:#00d4ff; }
```

## Delivery & Verification

1. Write single self-contained HTML file with inline CSS/JS
2. No external dependencies (no CDN, no frameworks)
3. Start server: `python3 -m http.server <port>`
4. Verify: `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/<file>`
5. If browser tool available: check console for errors, test sorting clicks

## Data Sync Pattern (Static HTML → Real Data)

For dashboards that should display periodically-updated real data (not just mock):

### Architecture

```
Source script (cron) → sync_*.py bridge (cron) → data.json → index.html fetch()
```

### Bridge Script Template

```python
import json, os, glob
from datetime import datetime
SOURCE = os.path.expanduser('~/path/to/source')
OUTPUT = os.path.expanduser('~/path/to/dashboard/data.json')

def main():
    logs = sorted(glob.glob(os.path.join(SOURCE, '*.json')))
    if not logs: return
    with open(logs[-1]) as f: raw = json.load(f)
    output = {'date': raw.get('date',''), 'items': [], 'updated_at': datetime.now().strftime('%H:%M')}
    with open(OUTPUT, 'w') as f: json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == '__main__': main()
```

### Frontend Fetch Pattern

```js
async function initApp(){
  try{
    const resp = await fetch('data.json?_t='+Date.now());
    if(resp.ok){
      const data = await resp.json();
      if(data.items && data.items.length > 0){
        positions.length = 0;
        data.items.forEach(r => positions.push({
          name: r.name, code: r.code, qty: Math.floor(Math.random()*3000+500),
          cost: +(Math.random()*200+20).toFixed(2),
          price: +(Math.random()*200+20).toFixed(2),
        }));
      }
    }
  } catch(e) { console.log('Using mock data', e.message); }
  render();
}
```

### Cron Setup

Place script in `~/.hermes/scripts/` (copy, NOT symlink).
`cronjob(action='create', name='数据同步', script='myscript.py', schedule='50 8 * * 1-5', no_agent=True, deliver='local')`

## Chinese Stock Display Conventions

For any dashboard showing Chinese A-share data:

| Element | Convention |
|---------|-----------|
| Price Up (涨) | **Red** — `#ef4444` (CSS var `--rise`) |
| Price Down (跌) | **Green** — `#22c55e` (CSS var `--fall`) |
| Background Up | `rgba(239,68,68,0.1+)` |
| Background Down | `rgba(34,197,94,0.1+)` |

**Opposite of Western conventions.** Apply to: table cells, chart candles, heatmap colors, sector labels, tooltips.

```css
:root { --rise:#ef4444; --fall:#22c55e; --rise-dim:rgba(239,68,68,.12); --fall-dim:rgba(34,197,94,.12); }
```

## Interactive Stock Switching

Dashboards with stock list + K-line chart:

1. Clickable rows: `onclick="switchStock(index)"` on `<tr>`
2. Include `i` param: `.map((p,i)=>{...data-idx="${i}" onclick="switchStock(${i})"...`
3. `switchStock(idx)` re-generates K-line data scaled to that stock's price level
4. Update chart title: `'📈 K线 · '+positions[idx].name+' ('+positions[idx].code+')'`

## Pitfalls

- **Canvas DPR**: Always scale by `devicePixelRatio`, otherwise Retina blur
- **Zero-value bars**: Set `min-height: 4px` to prevent collapse
- **Table overflow**: Wrap in scrollable container; set `white-space:nowrap` on cells
- **Resize**: Debounce canvas re-render on window resize
- **Heatmap cell shape**: Use `aspect-ratio: 1` not fixed height
- **Mock data**: Generate deterministic seed-based values, not random (prevents flicker on re-render)
