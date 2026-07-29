# 🐘 Dumbo Desktop Pet — V2: Single-Timer Pure-Drawing Approach

*Session: 2026-06-30*

This version takes a different architectural path from V1 — no API, no ChatDialog, no 3-timer trio. Everything is driven by a single 60fps timer and pure QPainter drawing.

## Architecture

```
┌─────────────────────────────────────┐
│  QApplication (no Dock icon)        │
│  └─ DumboPet (QWidget)              │
│      ├─ timer (16ms, 60fps)         │  drives ALL animation + wander
│      ├─ sparkles: list[Sparkle]     │  particle system
│      ├─ state: 'idle'|'trick'|...   │  timed state machine
│      └─ idle_anim: look/wave/sneeze │  random idle triggers
└─────────────────────────────────────┘
```

## Key Differences from V1

| Feature | V1 (3-timer) | V2 (single-timer) |
|---------|-------------|-------------------|
| Timers | flap (40ms) + move (25ms) + fly (7s) | one timer at 16ms |
| Animation | separate tick functions | `sin(freq * time)` equations in one `_tick` |
| Movement | lerp toward target each 25ms | frame-counter wander with drift |
| Expressions | click-cycle (happy/dazed/sleepy) | state machine (idle/trick/sneeze) |
| Idle variety | none | random look_l/r, wave, sneeze |
| Speech bubble | in ChatDialog | drawn in paintEvent with arrow tail |
| API | DeepSeek chat | none (pure local) |
| Magic prop | 5-point gold star on hat | white feather behind hat band |
| Particles | tiny circles | 4-point star shapes with gravity |
| Drag handling | fly_timer pause (30 min) | wander_target = None while dragging |
| Click | cycle expression | double-click → trick + sparkles + bubble |

## Sine-Driven Parameter System

Every continuous animation parameter is a function of `self.time` at a distinct frequency:

```python
f = self.time
self.ear_angle   = math.sin(f * 0.042) * 20 + math.sin(f * 0.018) * 5
self.bob_offset  = math.sin(f * 0.033) * 3  + math.sin(f * 0.070) * 1.2
self.head_tilt   = math.sin(f * 0.015) * 2
self.trunk_curl  = smooth_interpolate(self.trunk_target, self.trunk_curl, 0.06)
```

The frequencies are chosen to be **non-harmonic** (0.042 / 0.033 ≈ 1.27, not a clean ratio) so the combined motion never feels repetitive.

## Drawing Layer Order (Dumbo-specific)

Origin at center of window, `cy` shifted +12px for floor:

1. **Tail** — cubic bezier path + tuft ellipse
2. **Back ear** (left) — ellipse rotated by `-15 + ear_angle * 0.5`°, inner ear drawn separately
3. **Body** — rounded rect 104×76, radius 28
4. **Feet** — two ellipses at bottom of body
5. **Front ear** (right) — ellipse rotated by `15 - ear_angle * 0.5`°, inner ear
6. **Head** — ellipse 72×68, centered at y=-32
7. **Trunk** — cubic bezier path from face, waving via `idle_anim == 'wave'`
8. **Eyes** — white ellipses, pupils offset by idle_anim direction, blink reduces height
9. **Blush** — transparent pink ellipses on cheeks
10. **Mouth** — quadratic bezier smile arc (or open ellipse during sneeze)
11. **Hat** — rounded rect brim + crown + gold band
12. **Feather** — staggered behind hat band: quill line + bezier vane

## Colour Palette

```python
C_BODY     = QColor(180, 195, 210)    # soft blue-grey
C_EAR_IN   = QColor(232, 192, 200)    # pink inner ear
C_HAT      = QColor(24, 24, 110)      # navy
C_HAT_BAND = QColor(200, 180, 50)     # gold
C_FEATHER  = QColor(245, 245, 250)    # white feather
C_SPARKLE  = QColor(255, 230, 100)    # golden sparkles
C_MOUTH    = QColor(170, 90, 100)     # muted pink mouth
C_BLUSH    = QColor(255, 180, 190, 70) # transparent pink
```

## Context Menu

Styled dark menu with 5 items:
- ✨ 飞呀！ → triggers trick + sparkles
- 💬 你好 → random speech bubble ("小飞象来啦！", "我能飞！", etc.)
- separator
- 📖 关于 → shows "小飞象桌面宠物" as speech bubble
- 🚪 退出 → close()

Styling: `background: rgba(40,40,55,230)`, selected items `rgba(100,140,255,180)`, 8px border-radius.

## Auto-Wander

```python
self._wander_target = None   # QPoint or None
self._wander_counter = random.randint(4000, 10000)  # ms-ish, counted in frames

def _update_wander(self):
    if self._dragging:                           # don't wander during drag
        self._wander_counter = random.randint(2000, 5000)
        return
    if self._wander_target is None:
        self._wander_counter -= 1
        if self._wander_counter <= 0:
            # pick random point on screen with margin
            tx = random.randint(40, screen_w - WIN_W - 40)
            ty = random.randint(40, screen_h - WIN_H - 80)
            self._wander_target = QPoint(tx, ty)
        return
    # drift
    dx = target.x - current.x; dy = target.y - current.y
    dist = hypot(dx, dy)
    if dist < 5:   # arrived
        self._wander_target = None
        self._wander_counter = random.randint(4000, 10000)
        return
    speed = min(WANDER_SPEED, dist)    # WANDER_SPEED = 0.5 px/frame
    self.move(x + dx/dist * speed, y + dy/dist * speed)
```

## Packaging (this session)

Three methods were provided to the user:
1. **Manual .app** — create directory structure, Info.plist, launcher script
2. **py2app** — `setup.py` with `LSUIElement=True` plist
3. **pyinstaller** — `--windowed --onefile --name "DumboPet"`

All three produce apps that hide from the Dock (`LSUIElement`, `Tool` flag).
