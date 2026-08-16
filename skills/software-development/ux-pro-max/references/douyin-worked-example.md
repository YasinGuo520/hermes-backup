# 抖音选品大屏 — Worked Example

This file documents the full implementation of a 抖音选品 (Douyin Product Selection) data dashboard,
serving as a concrete reference for building similar Chinese e-commerce data screens.

## Page Structure

```
┌────────────────────────────────────────────────┐
│           抖音选品数据大屏 (title with glow)       │
├──────────┬──────────┬──────────┬───────────────┤
│  监控商品数 │  关联店铺  │  日均总销量 │  平均佣金率    │  ← animated counters
├──────────┴──────────┴──────────┴───────────────┤
│                     │                          │
│   爆品榜单 TOP 20    │    品类分布 (doughnut)     │
│   (sortable table    │                          │
│    with rank, name,  ├──────────┬───────────────┤
│    category, sales   │  价格带分布 │ 品类×价格带     │
│    bar, commission,  │  (vertical│  (heatmap      │
│    price)            │   bar)    │   grid)        │
└─────────────────────┴──────────┴───────────────┘
```

## Data Model

```js
const products = [
  { name: '商品名称',  cat: '品类',    price: 189,  sales: 28500, comm: 0.30 },
  //   ^string         ^string         ^number      ^number        ^float (0-1)
];
```

30 products covering 12+ categories: 女装, 男装, 童装, 食品, 美妆, 数码, 家居, 母婴, 运动, 个护, 鞋靴, 箱包, 玩具.

## Key Implementation Details

### Grid Layout

```css
.grid {
  display: grid; gap: 20px;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
}
.card-hot { grid-column: 1; grid-row: 1/3; }   /* table spans 2 rows */
.card-category { grid-column: 2; grid-row: 1; }
.card-price { grid-column: 2; grid-row: 1; }
.card-heatmap { grid-column: 2; grid-row: 2; }
```

The hot-product table occupies the full left column spanning both rows.
Right column has 3 cards arranged in a 2×2 sub-grid.

### Table Column Sort Keys

```js
const SORT_KEYS = ['rank', 'product', 'category', 'sales', 'commission', 'price'];
```

- `rank`: sort by sales (reversed — rank 1 = highest sales)
- `product`, `category`: string localeCompare
- `sales`, `commission`, `price`: numeric sort

### Canvas Pie Chart Glow

Apply `ctx.shadowBlur` directly after `ctx.fill()` to add a glow pass without
affecting subsequent draw operations:

```js
ctx.fillStyle = color;
ctx.fill();
ctx.shadowColor = color;
ctx.shadowBlur = 8;       // glow
ctx.fill();               // glow overlay (same shape)
ctx.shadowBlur = 0;       // reset
```

### Price Range Distribution

5 bins: 0-49, 50-99, 100-199, 200-299, 300+.

Count products per bin by filtering the full product list (not just top 20):

```js
ranges.map(r => ({
  count: allProducts.filter(p => p.price >= r.min && p.price <= r.max).length
}));
```

### Heatmap Generation

Use deterministic seed-based calculation to avoid random flicker:

```js
const val = ((cat.charCodeAt(0) * 37 + j * 179) % maxHeat + 3000 + j * 2000) % maxHeat;
```

This produces stable per-cell values that look varied but never change on page reload.

### Responsive Breakpoints

```css
@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }  /* all cards stacked */
}
@media (max-width: 600px) {
  .stats-row { grid-template-columns: 1fr; }
  body { padding: 10px; }
}
```

### Stats Animation

Trigger all 4 counters simultaneously, each with independent intervals.
Use `requestAnimationFrame`-free pattern via `setInterval(fn, 25)`:
- Step size: `target / 30` (finishes in ~30 frames ≈ 750ms)
- Use `Math.floor` for integer stats
- Use `.toFixed(1)` for percentage stats

## File

Created at: `~/Desktop/hermes/product-dashboard/index.html`
Served on: port 8911
Size: ~24KB (single file, no dependencies)
