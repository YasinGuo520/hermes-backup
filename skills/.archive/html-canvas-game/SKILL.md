---
name: html-canvas-game
description: Build single-file HTML/Canvas games with scene exploration, puzzle chains, inventory, and dialogue — no framework, no build step.
version: 1.0.0
author: Yasin's AI Co-pilot
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game, canvas, html, puzzle, interactive, creative, prototype]
    related_skills: [sketch, claude-design, immersive-html-experiences]
---

# HTML Canvas Game Builder

Build a playable **single-file HTML/Canvas game** — point-and-click adventure, puzzle escape, or interactive narrative. Zero dependencies, no build step, runs in any browser.

## When to Use

- User asks "can you make a game like X" (纸嫁衣,密室逃脱, point-and-click adventure)
- User wants a playable demo/prototype, not just a description
- User needs an interactive experience for marketing/narrative/education

## Core Architecture

```
┌──────────────────────────┐
│   Game State (G object)  │ ← single source of truth
│   scene / phase / flags  │
│   inventory[]            │
├──────────────────────────┤
│   Canvas Render Loop     │ ← requestAnimationFrame
│   drawScene()            │
├──────────────────────────┤
│   Scene System           │ ← SCENES object
│   items[] / exits[]      │
├──────────────────────────┤
│   Interaction Engine     │ ← hit detection + hover
│   getHit(mx,my)          │
├──────────────────────────┤
│   Puzzle Logic           │ ← checkPuzzle(itemId)
│   state-dependent gates  │
├──────────────────────────┤
│   Dialogue System        │ ← queue-based narrative
│   say() / nextLine()     │
├──────────────────────────┤
│   Inventory UI           │ ← bar at bottom of screen
│   4-6 slots              │
└──────────────────────────┘
```

## Step-by-Step Recipe

### 1. Game State Container

Start with a single `G` object that holds everything:

```js
const G = {
  state: 'title',     // title | play | ending
  scene: 'hall',      // current scene id
  phase: 0,           // narrative progression (0→1→2→3→...)
  inventory: [],      // item strings
  flags: {},          // arbitrary boolean gates
  mouseX: 0, mouseY: 0,
  hoverItem: null,    // for glow/highlight
  clock: 0,           // for animations
};
```

**Rule:** Every puzzle gate is a `flags[key]` check. Never encode progression in scene count or phase number alone — use named flags so they're debuggable.

### 2. Scene Definition

Define scenes as data objects:

```js
const SCENES = {
  hall: {
    name: '祠堂正厅',
    bg: {r:20, g:12, b:8},                    // RGB for radial gradient
    items: [
      {id:'candle', x:420,y:280,w:16,h:50, label:'烛台'},
      {id:'altar',  x:350,y:140,w:200,h:160, label:'供桌'},
    ],
  },
  shrine: { /* same shape */ },
};
```

Each scene renders differently via `drawScene()` — use `if(G.scene==='hall')` branches for scene-specific visuals.

### 3. Exits (Scene Transitions)

```js
const EXITS = {
  hall_to_shrine: {x:920,y:320,w:60,h:120, go:'shrine', label:'→ 偏殿'},
};

function getExits(scene) { /* return array for current scene */ }
```

### 4. Canvas Rendering

```html
<canvas id="gc"></canvas>
```

```js
const canvas = document.getElementById('gc');
const ctx = canvas.getContext('2d');
canvas.width = 1000; canvas.height = 700;

function drawScene() {
  // 1. Background gradient (radial, from scene.bg)
  // 2. Scene-specific geometry (walls, furniture)
  // 3. Items (draw basic shapes or embedded images)
  // 4. Exits (green indicator labels)
  // 5. Fog overlay (darken edges)
  // 6. Atmospheric particles (paper ash, fireflies)
}
```

**Pitfall:** Keep canvas fixed-size (1000×700) and use CSS scaling. Don't fight responsive resizing in game logic.

### 5. Hit Detection

```js
function getHit(mx, my) {
  // Check items first, then exits
  for (const item of SCENES[G.scene].items) {
    if (mx>=item.x && mx<=item.x+item.w &&
        my>=item.y && my<=item.y+item.h) {
      return {type:'item', id:item.id, label:item.label};
    }
  }
  // Check exits...
}
```

### 6. Puzzle Logic (State-Dependent)

This is the game's backbone. Each item triggers `checkPuzzle(itemId)`:

```js
function checkPuzzle(itemId) {
  switch(itemId) {
    case 'candle':
      if (!G.flags.candleLit && G.inventory.includes('matches')) {
        G.flags.candleLit = true;  // gate opens
        // Optional: spawn new item, update scene visuals
        return {type:'action', desc:'蜡烛亮了！供桌下出现暗格。'};
      }
      if (!G.inventory.includes('matches')) {
        return {type:'action', desc:'你没有能点火的东西。'};
      }
      return null;  // already done, silent

    case 'bell':
      if (G.inventory.includes('talisman') && !G.flags.gateOpen) {
        G.flags.gateOpen = true;
        return {type:'ending'};
      }
      return {type:'action', desc:'铜铃无风自鸣...'};
  }
}
```

**Puzzle Chain Pattern** (the standard escape-room loop):
```
Collect Item A → Gate needs A → Collect Item B → Combine A+B → New location → ...
```

### 7. Dialogue System

```js
let textQueue = [];

function say(actor, lines) {
  if (typeof lines === 'string') lines = [lines];
  textQueue = lines.map(l => ({actor, text: l}));
  document.getElementById('dialogue').style.display = 'block';
  nextLine();
}

function nextLine() {
  if (textQueue.length === 0) {
    document.getElementById('dialogue').style.display = 'none';
    return;
  }
  const cur = textQueue.shift();
  document.getElementById('d-text').textContent = cur.text;
}
```

### 8. Inventory UI

```html
<div id="inventory">
  <div class="inv-slot" id="i0"></div>
  <div class="inv-slot" id="i1"></div>
  <div class="inv-slot" id="i2"></div>
  <div class="inv-slot" id="i3"></div>
</div>
```

```js
function updateInv() {
  for (let i = 0; i < 4; i++) {
    const slot = document.getElementById('i' + i);
    if (i < G.inventory.length) {
      const icons = { matches:'🎯', talisman:'🟥', key:'🗝️' };
      slot.textContent = icons[G.inventory[i]] || '📦';
      slot.className = 'inv-slot filled';
    }
  }
}
```

### 9. Main Loop

```js
function loop() {
  drawScene();
  requestAnimationFrame(loop);
}
```

### 10. Event Binding

```js
canvas.addEventListener('click', (e) => {
  if (G.state !== 'play' || textQueue.length > 0) return;
  const hit = getHit(mouseX, mouseY);
  if (!hit) return;
  if (hit.type === 'item') interactItem(hit.id);
  if (hit.type === 'exit') { G.scene = hit.id; say(null, [hit.desc]); }
});

canvas.addEventListener('mousemove', (e) => {
  G.hoverItem = getHit(mx, my)?.label || null;  // triggers glow
});
```

## Quick-Start Template (minimal)

Use this as your starting skeleton:

```html
<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8">
<style>/* reset, #game container, #dialogue, #inventory */</style>
</head>
<body>
<div id="game"><canvas id="gc"></canvas>
  <div id="inventory"><!-- 4 slots --></div>
  <div id="dialogue" onclick="nextLine()">
    <div id="d-text"></div>
    <div id="d-hint">▸ 点击继续</div>
  </div>
</div>
<script>
// === GAME STATE ===
// === SCENES ===
// === RENDER ===
// === INTERACTION ===
// === PUZZLE LOGIC ===
// === DIALOGUE ===
// === LOOP ===
</script>
</body>
</html>
```

## Atmospheric Effects (easy wins)

| Effect | Technique | Code |
|--------|-----------|------|
| Paper ash falling | Array of 15-20 particles, sine-based x drift | `x+=(G.clock*0.3+i*117)%W` |
| Candle flicker | CSS animation on ::before pseudo-element | `@keyframes flicker` |
| Fog | Radial gradient overlay (center transparent → edge dark) | `ctx.createRadialGradient` |
| Scene glow on hover | shadowBlur + fill circle behind item | `ctx.shadowBlur=15` |

## Pitfalls

- **Don't use event listeners on items individually** — use one mouse handler and hit-test all items each frame. Simpler, no memory leaks.
- **Dialogue blocks interaction** — return early if `textQueue.length > 0` in click handler.
- **Canvas needs fixed dimensions** — 1000×700 for desktop. Don't fight responsive.
- **State machine > if-else sprawl** — use `flags` object, not nested if-else chains.
- **Inventory cap** — always check `G.inventory.length < maxInv` before pushing.
- **New process may not bind to port** — always check with `ss -tlnp | grep <PORT>` then kill old PID before starting a new server.

## Chinese Server Gotchas (国内服务器环境)

When deploying on a Chinese cloud server (no GUI, blocked domains):

| Issue | Fix |
|-------|-----|
| Google Fonts blocked (`@import url(...googleapis...)`) | Use system Chinese fonts: `font-family:'SimSun','STSong','Songti SC',serif` — no external CSS imports at all |
| hf.co / github.com unreachable/slow | Set `HF_ENDPOINT='https://hf-mirror.com'`; use `gitclone.com` for GitHub |
| No display to preview | `curl -s http://localhost:PORT/ \| head -3` to verify; share public IP for user to test |
| curl shows old content | Browser cache. Tell user: `Ctrl+F5` or append `?t=N` to URL |
| CSS janky on remote browser | Reduce particle count; avoid `box-shadow` on many elements; prefer `transform` over `top/left` |

## Verification

```bash
# 1. Check file
head -5 /path/to/game.html

# 2. Start server
cd /path/to/game && python3 -m http.server PORT

# 3. Verify via curl
curl -s http://localhost:PORT/ | head -3
# → <!DOCTYPE html><html lang="zh">...

# 4. Browser (if available)
browser_navigate("http://localhost:PORT")
browser_console()  # check for errors
```

## Reference

See `references/demo-game.html` for a complete working example (3 scenes, 12 items, puzzle chain, inventory, dialogue, Canvas rendering).
