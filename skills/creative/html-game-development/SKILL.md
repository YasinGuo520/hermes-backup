---
name: html-game-development
title: HTML Game Development
description: Build interactive browser games as single HTML files — point-and-click adventures, visual novels, puzzle games, and other 2D experiences. Uses write_file for full HTML/CSS/JS, terminal for HTTP server, and browser for testing.
trigger: user asks to build a game, make a playable demo, create an interactive experience, or "can you make X game"
---

# HTML Game Development

## When to use

The user asks to:
- "make a game like X"
- "build a demo I can try"
- "can you code a game that does Y"
- "show me something interactive"
- "create a playable prototype"

**Default: YES you can.** Don't say "可以做但效果不好" or "这个有点难" without first building a minimal demo. Ship first, then iterate.

## Game types I can build (confirmed working)

| Type | Complexity | Tech | Notes |
|------|-----------|------|-------|
| Click-based adventure/puzzle | ★★★★☆ | Canvas + State Machine | Best match for point-&-click (like 纸嫁衣) |
| Visual Novel / Branching narrative | ★★★☆☆ | DOM + Dialogue Queue | 200+ line branching possible |
| Hidden object / Scene search | ★★★☆☆ | DOM + z-index + event delegation | Easy to make, good for horror |
| Text RPG / CYOA | ★★☆☆☆ | DOM + State + localStorage | Simplest to make well |
| Card / Board game | ★★★☆☆ | Canvas or DOM grid | Logic-heavy, lightweight rendering |
| 2D platformer | ★★★★☆ | Canvas + requestAnimationFrame | Physics = simple gravity only |
| Puzzle (logic/maze/sokoban) | ★★☆☆☆ | Grid + BFS/DFS solver | Good for demonstrating AI+game hybrid |
| Audio-driven / Ambient | ★★★☆☆ | Web Audio API + edge-tts | Edge-tts + Web Audio = minimal file size |

## Toolchain

```
write_file(path)      → write the game HTML (single file, self-contained)
terminal(cmd)         → python3 -m http.server <PORT> (background)
browser_navigate(url) → test in browser
browser_console(expr) → debug / inspect state
vision_analyze()      → visual check (if display available)
```

## Architecture template (click-based adventure)

```
┌─────────────────────────────────────┐
│  HTML Structure                     │
│  ├── #title-screen (start button)   │
│  ├── #game-container                │
│  │   ├── #scene (interactive area)  │
│  │   ├── scene elements (canvas/div)│
│  │   ├── #inventory-bar (道具栏)    │
│  │   └── #dialogue-box (对话框)     │
│  └── <style> (所有CSS)              │
└─────────────────────────────────────┘

// Game State (JS object)
const state = {
  phase: 0,          // story progression
  inventory: [],     // collected items
  flags: {},         // boolean state flags
  dialogueQueue: []  // pending dialogue lines
};

// Systems
function showDialogue(name, lines[]) → render dialogue queue
function interact(id) → phase-based dispatch
function pickup(id) → add to inventory + update UI
function useItem(itemId, targetId) → state change
```

## Step-by-step

1. **Clarify the scope**: "how long should the game be? (15min / 1hr / 2hr+)? Any specific mechanics?"
2. **Build the skeleton first**: title screen → scene layout → dialogue system → state machine
3. **Test early**: start HTTP server, load in browser after first 30 lines of code
4. **Add interactivity iteratively**: one scene element at a time, test each
5. **Polish at the end**: ambient particles, sound effects (edge-tts), transitions

## Design principles for horror/adventure games

- 氛围 > 画面: CSS特效 + 暗色调 + 音效比精致美术重要
- 叙事驱动: 对话系统比复杂解谜更重要
- 状态机: 每个阶段有清晰的 progress 条件
- 容错: 点错不给惩罚，给额外 flavor text
- 低门槛: 点击即交互，不教就懂

## Known limitations (be upfront)

- ❌ No 3D rendering (WebGL technically possible but assetless)
- ❌ No mobile app packaging (can't .ipa/.apk)
- ❌ No multiplayer / real-time networking
- ❌ Art quality ceiling = AI-generated images or CSS
- ❌ No game engine (no Unity/Unreal/Cocos)
- ✅ Sound via Web Audio API or embedded base64
- ✅ Save/load via localStorage

## Pitfalls

- **Don't over-promise art quality.** CSS/emoji art is fine for prototypes. Say "visuals are placeholder" upfront.
- **Don't say "做不了" without trying.** If the user asks for a game, write a 100-line skeleton first, then evaluate. "can't" is a last resort, not a first answer.
- **Dialogue queues must be testable.** If the dialogue system has bugs, the game is unplayable. Test dialogue flow early.
- **State management.** A flat state object is better than nested state for debugging. Log state to browser console on each interaction.
- **CSS-only animations are cheap but limited.** For character animation, use CSS keyframes + transform. For complex scenes, use Canvas 2D.

## Verification

After building:
1. `curl localhost:<PORT>/` → 200 OK
2. Click through start → first interaction → dialogue → second interaction → pickup → use → ending
3. `browser_console('JSON.stringify(gameState)')` → verify state transitions
4. Check for console errors (undefined vars, missing event handlers)

## Canvas 游戏架构细节（合并自 html-canvas-game）

单文件 Canvas 点击冒险游戏（密室逃脱/纸嫁衣类）的核心骨架：

```
const G = { state:'title', scene:'hall', phase:0, inventory:[], flags:{}, mouseX:0, mouseY:0, hoverItem:null, clock:0 };
const SCENES = { hall: { name:'祠堂正厅', bg:{r:20,g:12,b:8}, items:[{id:'candle',x:420,y:280,w:16,h:50,label:'烛台'}] } };
const EXITS = { hall_to_shrine: {x:920,y:320,w:60,h:120, go:'shrine', label:'→ 偏殿'} };
```

- **每条谜题门都是一个 `flags[key]` 检查**：永远不要用 scene 计数/phase 数字编码进度，用命名 flag 便于调试
- **谜题链模式**（密室逃脱标准循环）：`收集A → 门需要A → 收集B → A+B合成 → 新地点 → …`
- **命中检测**：不要给 item 单独绑事件，用一个鼠标 handler 每帧 hit-test 所有 items/exits（简单、无内存泄漏）
- **对话阻塞交互**：click handler 里 `if (textQueue.length > 0) return` 提前返回
- **Canvas 固定尺寸**：1000×700，用 CSS 缩放，不要在游戏逻辑里做响应式
- **背包上限**：push 前检查 `G.inventory.length < maxInv`
- **氛围特效易得**：纸灰飘落（15-20粒子 sine 漂移）、烛光闪烁（CSS ::before keyframes）、雾（radial gradient 边缘暗化）、hover 发光（shadowBlur）
- 完整可运行示例（3场景/12物品/谜题链/背包/对话/Canvas渲染）：`references/demo-complete-game.html`

### 国内服务器环境 gotchas（无GUI、域名受限）
| 问题 | 修复 |
|------|------|
| Google Fonts 被墙 | 系统中文黑体 `font-family:'SimSun','STSong','Songti SC',serif`，零外部 CSS import |
| hf.co / github.com 不通 | `HF_ENDPOINT='https://hf-mirror.com'`；GitHub 用 gitclone.com |
| 无显示器预览 | `curl -s http://localhost:PORT/ \| head -3` 验证；分享公网 IP 给用户 |
| curl 显示旧内容 | 浏览器缓存：`Ctrl+F5` 或 URL 加 `?t=N` |
| 远程浏览器卡顿 | 减粒子数；避免大量 box-shadow；优先 transform 而非 top/left |
| 新进程绑不上端口 | `ss -tlnp \| grep <PORT>` 找到旧 PID kill 后再起 |

## Related skills
- `creative/p5js` — generative art/sketches (canvas, shaders)
- `creative/immersive-html-experiences` — celebration/full-screen pages
- `creative/sketch` — quick HTML mockups (2-3 variants)
