# 🐘 Dumbo Desktop Pet — Full Reference

This document walks through the complete desktop pet built in the 2026-06-29 session. Every pattern from the parent skill is demonstrated here.

## Project Files (Desktop)

| File | Purpose |
|------|---------|
| `mac_pet.py` | Main Python application (280 lines) |
| `DumboPet.app` | Bundled macOS app |
| `make_dumbo_app.sh` | Build script to recreate the .app |
| `设置API密钥.command` | Double-clickable API key setup |

## Architecture Overview

```
┌─────────────────────────────────────┐
│  QApplication                       │
│  ├─ DumboPet (QWidget)              │
│  │   ├─ flap_timer  (40ms)          │  ear + sparkle animation
│  │   ├─ move_timer  (25ms)          │  smooth flight toward target
│  │   ├─ fly_timer   (7s)            │  pick new random destination
│  │   ├─ stay_timer  (30min single)  │  pause after drag
│  │   └─ click_timer (350ms single)  │  click vs double-click debounce
│  └─ ChatDialog (QDialog)            │
│      └─ requests.post → DeepSeek    │  API chat
└─────────────────────────────────────┘
```

## Drawing Layer Order

In `paintEvent`, layers are drawn back-to-front:

1. **Shadow** — `QRadialGradient` ellipse below body
2. **Body** — rounded rect with radial gradient (blue-gray `#7895B8`)
3. **Feet** — two small rounded rects
4. **Ears** (flapping) — large ellipses rotated by `flap_phase * sin(time)` — Dumbo's signature
5. **Head** — ellipse with lighter gradient
6. **Trunk** — `QPainterPath.cubicTo` curved line
7. **Cheeks** — pink semi-transparent ellipses
8. **Eyes** — expression-dependent (arcs, circles, or half-covers)
9. **Hat** — circus cone with a 5-point gold star
10. **Sparkles** — tiny fading circles when flying

## Expression State Machine

3 states, cycled by single-click:

| State | Eyes | Mouth | Visual Cue |
|-------|------|-------|------------|
| `happy` | `^_^` (upward arcs) + sparkly pupils | Smile arc | Extra blush |
| `dazed` | `@_@` (big round pupils) | Small "O" | White dot highlights |
| `sleepy` | `-_ -` (half-covered) | None | "z z Z" text floats off |

## Flight Algorithm

```
every 7s: pick random (x, y) within screen bounds
every 25ms:
  dx = target.x - current.x
  dy = target.y - current.y
  dist = hypot(dx, dy)
  if dist < 8: arrived, wait for next 7s tick
  speed = min(4.0, dist / 20.0 + 0.5)
  sway = sin(flap_phase * 0.5) * 0.5       # gentle side-to-side
  lift = -abs(sin(flap_phase * 2)) * 0.8    # bobbing up and down
  move(current.x + cos(angle + sway) * speed,
       current.y + sin(angle) * speed + lift)
```

## Drag → Pause Behavior

```
drag starts → fly_timer stops, is_flying = false
drag releases → stay_timer starts 30-min single-shot
stay_timer fires → is_flying = true, fly_timer restarts, pick new target
drag to same spot → stay_timer restarts (30 more minutes)
```

## macOS .app Structure

```
DumboPet.app/
  Contents/
    Info.plist          — bundle metadata, LSUIElement=true hides dock icon
    MacOS/
      DumboPet          — bash launcher: sources ~/.zshrc, execs python3
    Resources/
      mac_pet.py        — the actual script
```

## API Key Setup Path

The `.command` setup script (`设置API密钥.command`):
1. `read -s` the user's key (hidden input)
2. Checks if `DEEPSEEK_API_KEY` already exists in `~/.zshrc` — if yes, `sed` replaces its value; if no, appends a new line
3. Also does `export DEEPSEEK_API_KEY="$api_key"` for the current terminal session
4. User can then double-click the .app and it'll find the key via the launcher sourcing `~/.zshrc`

## Known Working Config

- **macOS**: 15.0.1 (Sequoia)
- **Python**: 3.9.6 (system)
- **PySide6**: latest (installed via pip)
- **Display**: 2560×1600 Retina + 1920×1080 external
- **DeepSeek**: `deepseek-chat` model, `api.deepseek.com` endpoint
