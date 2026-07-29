---
name: pyside6-desktop-apps
description: Build, animate, and package PySide6 desktop applications on macOS — transparent windows, custom QPainter graphics, animation loops, API integration, and .app bundling.
tags: [pyside6, pyqt, desktop, macos, gui, animation, packaging]
trigger: User asks for a desktop app, desktop pet, transparent widget, always-on-top window, macOS .app bundle, PySide6/PyQt application, or any GUI tool that runs natively on the desktop.
---

# PySide6 Desktop Applications (macOS)

Build polished macOS desktop apps with PySide6 — from transparent animated widgets to full AI chatbots — and package them as double-clickable `.app` bundles.

---

## 1. Prerequisites

```bash
# Check Python
python3 --version                     # needs 3.8+

# Check PySide6
python3 -c "import PySide6; print(PySide6.__version__)"

# Install if missing
pip3 install PySide6 requests
```

Essential imports:
```python
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QMenu, ...
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF, QPropertyAnimation, ...
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush, QFont, ...
```

---

## 2. Transparent Always-on-Top Window

The canonical recipe for a frameless, transparent, always-on-top widget:

```python
class DesktopWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool                     # hides from Dock / Alt-Tab
            | Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # required for transparency
        self.setAttribute(Qt.WA_ShowWithoutActivating)   # doesn't steal focus
        self.setFixedSize(width, height)
```

**Key flags explained:**
- `FramelessWindowHint` — no title bar, no borders
- `WindowStaysOnTopHint` — always above other windows
- `Tool` — suppresses dock icon, better for utility windows
- `WA_TranslucentBackground` — enables per-pixel alpha in `paintEvent`
- `WA_ShowWithoutActivating` — appears without stealing keyboard focus

---

## 3. Custom QPainter Drawing

Draw your own graphics in `paintEvent`. Always pair `Antialiasing` + `SmoothPixmapTransform` for Retina displays.

```python
def paintEvent(self, event):
    p = QPainter(self)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)

    # Gradients for depth
    grad = QRadialGradient(cx, cy, radius)
    grad.setColorAt(0, QColor("#light"))
    grad.setColorAt(1, QColor("#dark"))
    p.setBrush(grad)
    p.drawRoundedRect(rect, radius, radius)

    # Paths for organic shapes (trunks, ears, wings)
    path = QPainterPath()
    path.moveTo(x1, y1)
    path.cubicTo(cx1, cy1, cx2, cy2, x2, y2)
    p.drawPath(path)

    p.end()
```

**Pattern for animated characters:**
- Draw shadow first (transparent radial gradient)
- Draw body → feet → ears → head → face → accessories (back-to-front layering)
- Each layer is a separate `_draw_xxx()` method for readability
- Use `QRadialGradient` for soft depth, `QLinearGradient` for flat highlights

### Hover Glow

Give the pet a subtle "alive" feeling when the mouse is near. Track `self.hovered` via `enterEvent` / `leaveEvent` / `mouseMoveEvent`:

```python
def __init__(self):
    self.setMouseTracking(True)   # required for hover without press
    self.hovered = False

def enterEvent(self, event):   self.hovered = True
def leaveEvent(self, event):   self.hovered = False
```

In `paintEvent`, draw a subtle white glow ring around the character when hovered:

```python
if self.hovered:
    painter.setPen(QPen(QColor(255, 255, 255, 25), 2))
    painter.setBrush(QColor(255, 255, 200, 6))
    painter.drawRoundedRect(margin, margin, w - 2*margin, h - 2*margin, 30, 30)
```

Keep it subtle — 6 alpha fill, 25 alpha stroke. The glow should feel like ambient light, not a selection highlight.

---

## 4. Animation: The Timer Trio

Desktop pets need 3 distinct timers. Never use `QPropertyAnimation` for continuous movement — use `QTimer` with manual position updates for finer control.

| Timer | Interval | Purpose |
|-------|----------|---------|
| **Flap** | ~40-50ms | Continuous visual animation (ear flapping, sparkles, breathing) |
| **Move** | ~25-30ms | Smooth positional movement toward target (lerp) |
| **Fly** | ~5-8s | Periodic random target selection (calls `_pick_target`) |

```python
# Flap: runs every frame for visual effects
self.flap_timer = QTimer(self)
self.flap_timer.timeout.connect(self._tick_flap)
self.flap_timer.start(40)

# Move: smooth interpolation toward target
self.move_timer = QTimer(self)
self.move_timer.timeout.connect(self._tick_move)
self.move_timer.start(25)

# Fly: periodic random target selection
self.fly_timer = QTimer(self)
self.fly_timer.timeout.connect(self._pick_target)
self.fly_timer.start(7000)
```

**Smooth movement formula** (in `_tick_move`):
```python
dx = target.x() - current.x()
dy = target.y() - current.y()
dist = math.hypot(dx, dy)
if dist < 8: return  # arrived
speed = min(4.0, max(target_speed, dist / 20.0 + 0.5))
self.move(
    int(current.x() + dx / dist * speed),
    int(current.y() + dy / dist * speed)
)
```

### Alternative: Single-Timer Approach (Sine-Driven)

For simpler characters with continuous motion, a **single 60fps timer** driving everything via `self.time` counter is cleaner — no sync issues, no overlapping timers:

```python
def __init__(self):
    self.time = 0.0
    self.timer = QTimer(self)
    self.timer.timeout.connect(self._tick)
    self.timer.start(16)  # ~60fps

def _tick(self):
    self.time += 1.0
    self._update_animation()
    self._update_wander()
    self.update()  # repaint

def _update_animation(self):
    f = self.time
    # ALL movement driven by sine waves at different frequencies
    self.ear_angle = math.sin(f * 0.042) * 20 + math.sin(f * 0.018) * 5
    self.bob_offset = math.sin(f * 0.033) * 3 + math.sin(f * 0.07) * 1.2
    self.head_tilt = math.sin(f * 0.015) * 2
```

**Key insight**: each animation parameter gets its own `sin(freq * time)` — ears flap at one rate, body bobs at another, head tilts at a third. They visually decouple and feel organic. No state variables, no reset logic, just pure math.

**Wander behavior** increments `_wander_counter` every frame; when it reaches 0, picks a random `(x, y)` target on screen and drifts toward it at `WANDER_SPEED` px/frame. After arrival, picks a new countdown. This replaces the Fly timer entirely.

---

## 4a. Particle Effects (Sparkles / Stars)

Add a lightweight particle system for happiness, magic, or flying effects:

```python
class Sparkle:
    """Single animated sparkle particle — 4-point star shape."""
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'size')

    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 3.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 0.5
        self.max_life = random.randint(25, 55)
        self.life = self.max_life
        self.size = random.uniform(2.0, 5.0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.04               # gravity
        self.vx *= 0.98               # friction
        self.life -= 1

    @property
    def alive(self): return self.life > 0

    def draw(self, painter, cx, cy):
        ratio = self.life / self.max_life
        alpha = int(min(1.0, ratio * 2) * 255)
        sz = self.size * (0.3 + 0.7 * ratio)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 230, 100, alpha))
        # 4-point star
        path = QPainterPath()
        path.moveTo(cx + self.x, cy + self.y - sz)
        path.lineTo(cx + self.x + sz * 0.35, cy + self.y - sz * 0.15)
        path.lineTo(cx + self.x + sz, cy + self.y)
        path.lineTo(cx + self.x + sz * 0.35, cy + self.y + sz * 0.15)
        path.lineTo(cx + self.x, cy + self.y + sz)
        path.lineTo(cx + self.x - sz * 0.35, cy + self.y + sz * 0.15)
        path.lineTo(cx + self.x - sz, cy + self.y)
        path.lineTo(cx + self.x - sz * 0.35, cy + self.y - sz * 0.15)
        path.closeSubpath()
        painter.drawPath(path)
```

**Lifecycle**: Tick all particles each frame (`s.update()`), filter out dead ones (`s.alive`). Spawn with `_spawn_sparkles(count=15)` on click/trick events. The fade-in/fade-out via `alpha = min(1.0, ratio * 2)` avoids the pop-in look.

---

## 4b. Character State Machine

Use a simple string-based state machine for character behaviour:

```python
self.state = 'idle'      # idle | trick | sneeze | sleep
self.state_timer = 0

def _tick(self):
    if self.state == 'trick':
        self.state_timer -= 1
        if self.state_timer <= 0:
            self.state = 'idle'
    # drawing code checks state for expression changes
```

| State | Duration | Visual Effect |
|-------|----------|---------------|
| `idle` | indefinite | Gentle bob, ear flap, random looks |
| `trick` | 60-70 frames | ears flap fast, sparkles, speech bubble, extra bob |
| `sneeze` | 30-40 frames | squint eyes, open mouth, big bounce |

The drawing methods read `self.state` to modify expressions — e.g. `if self.state == 'sneeze': squint = 6`.

---

## 4c. Idle Animation Triggers

Add variety with random idle animations on a cooldown timer:

```python
self.idle_anim = None       # 'look_l' | 'look_r' | 'wave' | None
self.idle_timer = 0
self.idle_cooldown = random.randint(60, 360)  # frames

def _tick(self):
    if self.state == 'idle' and self.idle_anim is None:
        self.idle_cooldown -= 1
        if self.idle_cooldown <= 0:
            self.idle_anim = random.choice(
                ['look_l', 'look_r', 'wave', None, None, None]
            )
            self.idle_timer = 40
            self.idle_cooldown = random.randint(120, 720)
    if self.idle_anim:
        self.idle_timer -= 1
        if self.idle_timer <= 0:
            self.idle_anim = None
```

The drawing functions read `self.idle_anim` for small parameter tweaks — e.g. `self.idle_anim == 'wave'` adds `math.sin(time * 0.2) * 25` to the trunk curl, `'look_l'` / `'look_r'` shifts pupil `x` offset by ±1px.

### 4e. Click-to-Trick (Simple Trigger)

Hooking a click to a state-machine transition follows a consistent pattern:

```python
# In _on_single_click (after debounce, see §5):
if random.random() < 0.3:      # 30% chance of a "trick"
    self.state = 'trick'
    self.state_timer = 60       # lasts ~1s at 60fps
    self._spawn_sparkles(15)
    self._say("✨ 嘿嘿！")
else:
    self._cycle_expression()    # otherwise cycle as usual
```

This keeps the character responsive — the user always gets something back, and the trick/sparkle/bubble combination makes repeated clicks feel fresh. `_say()` duration is driven by `speech_timer`, not the state timer, so the bubble can outlast or overlap with the trick animation.

---

## 4d. Speech Bubbles

A simple speech bubble drawn in `paintEvent`:

```python
def _draw_speech(self, p, cx, cy):
    tx, ty = cx, cy - 105
    text = self.speech_text

    p.setPen(QPen(QColor(60, 60, 80), 1.5))
    p.setBrush(QColor(255, 255, 255, 235))

    fm = self.fontMetrics()
    tw = fm.horizontalAdvance(text) + 24
    th = fm.height() + 14
    bx, by = tx - tw // 2, ty - th // 2

    bubble = QPainterPath()
    bubble.addRoundedRect(bx, by, tw, th, 12, 12)
    # tail pointing down toward character
    tail = QPainterPath()
    tail.moveTo(tx - 5, by + th)
    tail.lineTo(tx, by + th + 10)
    tail.lineTo(tx + 5, by + th)
    tail.closeSubpath()
    bubble.addPath(tail)

    p.drawPath(bubble)
    p.setPen(QColor(40, 40, 50))
    p.drawText(QRectF(bx, by, tw, th),
               Qt.AlignmentFlag.AlignCenter, text)
```

Call via a timer- or event-triggered `_say(text)` method that sets `self.speech_text` and a `speech_timer` (e.g. 100 frames ≈ 1.6s at 60fps):

```python
def _say(self, text):
    self.speech_text = text
    self.speech_timer = 100
```

The timer counts down each frame; when it hits 0, clear the text. This auto-dismisses the bubble.

---

## 5. Mouse Event Handling

### Critical: Click vs Double-Click Distinction

Qt fires `press → release → press → doubleClick → release`. A naive single-click handler on `mouseReleaseEvent` fires BEFORE `mouseDoubleClickEvent`, so you must use a **debounce timer**:

```python
def __init__(self):
    self._pending_click = False
    self._click_timer = QTimer(self)
    self._click_timer.setSingleShot(True)
    self._click_timer.timeout.connect(self._on_single_click)

def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton and self._is_potential_click:
        self._pending_click = True
        self._click_timer.start(350)  # debounce window (350-400ms)
    super().mouseReleaseEvent(event)

def mouseDoubleClickEvent(self, event):
    if event.button() == Qt.LeftButton:
        self._pending_click = False    # CANCEL single click
        self._click_timer.stop()
        self._handle_double_click()    # open chat, etc.
    super().mouseDoubleClickEvent(event)

def _on_single_click(self):
    if self._pending_click:
        self._pending_click = False
        self._handle_single_click()    # cycle expression, toggle, etc.
```

### Drag Handling

Track `_is_potential_drag` using `manhattanLength()` threshold (~8px):

```python
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        self._is_potential_drag = True
        self._click_start = event.position().toPoint()
        self.drag_offset = event.position().toPoint()

def mouseMoveEvent(self, event):
    if event.button() == Qt.LeftButton and self._is_potential_drag:
        delta = (event.position().toPoint() - self._click_start).manhattanLength()
        if delta > 8:
            self.is_dragging = True
            self.move(self.mapToGlobal(event.position().toPoint() - self.drag_offset))
```

### Context Menu (Right-Click)

```python
def contextMenuEvent(self, event):
    menu = QMenu(self)
    menu.setStyleSheet("""...""")  # dark theme stylesheet
    action = QAction("🤖 AI Chat", self)
    action.triggered.connect(self._open_chat)
    menu.addAction(action)
    menu.addSeparator()
    menu.exec(event.globalPos())
```

---

## 6. API Integration (DeepSeek / OpenAI)

Use the OpenAI-compatible endpoint. Config:

```python
import os, requests

API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

def chat(messages):
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return "⚠️ DEEPSEEK_API_KEY not set"

    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages, "temperature": 0.85, "max_tokens": 500},
        timeout=20,
    )
    return resp.json()["choices"][0]["message"]["content"]
```

**API Key management:**
- Read from `os.environ.get("DEEPSEEK_API_KEY", "")`
- Shell launcher can source `~/.zshrc` to pick up the env var
- Provide a `.command` setup script to write `export DEEPSEEK_API_KEY="sk-..."` into `~/.zshrc`

---

## 7. Testing & Verification

Before packaging, verify the app works without needing a physical display. This catches import errors, rendering bugs, and state-machine regressions early.

### 7.1 Syntax & Import Check (Fast Gate)

```bash
# Syntax validation only (no GUI, no import)
python3 -c "import ast; ast.parse(open('mac_pet.py').read()); print('✅ Syntax OK')"

# Import check (triggers top-level imports, but not QApplication)
python3 -c "exec(open('mac_pet.py').read().split('def main():')[0]); print('✅ Imports OK')"
```

The `ast.parse` approach is safer than running the script — it won't trigger any side effects from `QApplication` construction, window creation, or display connection. Use this as a first pass in automated checks.

### 7.2 Offscreen Headless Testing

Set `QT_QPA_PLATFORM=offscreen` to instantiate Qt widgets without a display server:

```python
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # must be set BEFORE QApplication

from PySide6.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)

from my_app import MyWidget

widget = MyWidget()
assert widget.windowFlags() & Qt.FramelessWindowHint
assert widget.width() == 180

# Test state transitions
widget.cycle_expression()
assert widget.expr == 'dazed'
```

**Key pattern:** Set the env var before importing `QApplication`. Setting it after Qt's display plugin is already loaded has no effect.

### 7.3 Render Frame Verification

Capture each visual state to a QImage and check it has content (non-transparent pixels):

```python
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt

for expr_name in ['happy', 'dazed', 'sleepy']:
    widget.expr = expr_name
    widget.flap_phase = 0.0

    img = QImage(widget.size(), QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    painter = QPainter(img)
    widget.render(painter, QPoint(0, 0))
    painter.end()

    # Verify the image has actual content
    has_content = any(
        img.pixelColor(x, y).alpha() > 0
        for y in range(img.height())
        for x in range(img.width())
    )
    assert has_content, f'{expr_name} rendered all-transparent!'

    # Optionally save for manual inspection
    img.save(f'/tmp/screenshot_{expr_name}.png')
```

**Why this matters:** A transparent window with `WA_TranslucentBackground` can be invisible if all `paintEvent` drawing paths are broken — the test catches that. The `.render()` method draws directly to a QImage without needing a screen, making it suitable for CI or pre-packaging checks.

For large images, the double-loop over every pixel is slow. Optimise with a short-circuit or use `img.constBits()` for bulk access.

### 7.4 Process-Level Launch Verification

After launching the app (via `.app` bundle or `python3 mac_pet.py &`), verify it's alive:

```bash
# Check process exists
pgrep -f mac_pet.py && echo "✅ Running"

# Check CPU/memory (to confirm animation loop is active)
ps aux | grep mac_pet.py
```

Use this **only** after an `open AppName.app` or background launch — not during development where you're running via terminal.

### 7.5 Window Detection (macOS — optional)

When `osascript` is used to query window info, it may prompt for Accessibility permissions and **time out silently**:

```python
import subprocess
try:
    r = subprocess.run(
        ['osascript', '-e', 'tell app "System Events" to get name of every window'],
        capture_output=True, text=True, timeout=5
    )
    print(r.stdout)
except subprocess.TimeoutExpired:
    print("⚠️  osascript timed out — likely waiting for Accessibility permissions")
```

**Know when to skip:** osascript-based tests are fragile on macOS — they hang when permissions are missing. Prefer `pgrep` for process checks and use osascript only when you've verified permissions are already granted.

---

## 8. macOS .app Bundling

To make a double-clickable app from any Python script:

### Bundle Structure
```
DumboPet.app/
  Contents/
    Info.plist
    MacOS/
      DumboPet          # launcher shell script (executable)
    Resources/
      mac_pet.py        # the actual Python script
```

### Info.plist
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>AppName</string>
    <key>CFBundleIdentifier</key><string>com.yourapp.id</string>
    <key>CFBundleName</key><string>App Display Name</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>LSMinimumSystemVersion</key><string>12.0</string>
    <key>NSHighResolutionCapable</key><true/>
    <key>LSUIElement</key><true/>  <!-- hides from Dock -->
</dict>
</plist>
```

### Launcher Shell Script (MacOS/AppName)
```bash
#!/bin/bash
DIR="$(cd "$(dirname "$0")/../Resources" && pwd)"
cd "$DIR"
# Source user env so DEEPSEEK_API_KEY etc. are available
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc" 2>/dev/null || true
exec /usr/bin/python3 "$DIR/your_script.py"
```

### Build Commands
```bash
rm -rf AppName.app
mkdir -p AppName.app/Contents/MacOS AppName.app/Contents/Resources
cp your_script.py AppName.app/Contents/Resources/
# Write Info.plist with cat heredoc
cat > AppName.app/Contents/Info.plist <<'PLIST'
...plist content...
PLIST
cat > AppName.app/Contents/MacOS/AppName <<'LAUNCHER'
...launcher script...
LAUNCHER
chmod +x AppName.app/Contents/MacOS/AppName
```

### Alternative: py2app (Declarative Build)

For larger projects, py2app is cleaner — it handles the bundle structure, launcher, and Info.plist from a single `setup.py`:

```python
"""
setup.py — py2app build for Mac .app
Usage:  pip install py2app && python setup.py py2app -A
        (remove -A for a standalone bundle with bundled Python)
"""
from setuptools import setup

APP = ['mac_pet.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'AppName',
        'CFBundleDisplayName': 'Display Name',
        'CFBundleIdentifier': 'com.yourorg.appname',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,          # hides from Dock
    },
    'packages': ['PySide6'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
}

setup(app=APP, data_files=DATA_FILES,
      options={'py2app': OPTIONS}, setup_requires=['py2app'])
```

**Trade-offs:**
- py2app `-A` (alias mode): fast rebuilds, but requires system Python to be present on target machine
- py2app no `-A` (full build): standalone ~60MB bundle, slower build, works on any Mac with matching macOS version
- Manual .app: no extra tooling, but tedious for repeated builds

### Alternative: pyinstaller (Most Reliable)

When py2app has compat issues, pyinstaller tends to work more reliably with PySide6:

```bash
pip install pyinstaller
pyinstaller --windowed --onefile --name "AppName" mac_pet.py
# Output: dist/AppName.app
```

No separate setup.py needed — pyinstaller auto-detects your imports.

---

## 9. .command Setup Scripts for End Users

Create a double-clickable setup script that writes env vars to `~/.zshrc`:

```bash
#!/bin/bash
# 设置API密钥.command
echo "输入你的 API Key:"
read -s -p "➜  " api_key
if grep -q "MY_API_KEY" "$HOME/.zshrc" 2>/dev/null; then
    sed -i '' "s|export MY_API_KEY=.*|export MY_API_KEY=\"$api_key\"|" "$HOME/.zshrc"
else
    echo "export MY_API_KEY=\"$api_key\"" >> "$HOME/.zshrc"
fi
export MY_API_KEY="$api_key"
echo "✅ 已设置！"
chmod +x "设置API密钥.command"  # must be executable
```

---

## 10. Pitfalls & Gotchas

### macOS System
- **Terminal/execute_code blocking**: On managed macOS systems, `terminal()` and `execute_code()` calls that do GUI work (import PySide6, create QApplication) may time out waiting for user consent, especially when the tool requires display access. Use `timeout=15` to fail fast. For import verification and syntax checks, use `ast.parse(open(file).read())` from `execute_code` instead of running the script directly.
- **Permission dialog blocking**: Desktop pets that use `computer_use` or accessibility APIs may trigger macOS permission dialogs. Do NOT click through these programmatically — stop and ask the user to grant permissions manually in System Settings.

### Window / Display
- **Retina blur**: Always set `QT_ENABLE_HIGHDPI_SCALING=1` and `QT_MAC_WANTS_LAYER=1` at startup via `os.environ.setdefault()`
- **White flash on launch**: The `WA_TranslucentBackground` attribute must be set *before* the widget is first shown, or you'll get a split-second white rectangle
- **Window not staying on top**: Add `Qt.X11BypassWindowManagerHint` to window flags for stubborn cases
- **Focus stealing**: Use `WA_ShowWithoutActivating` to prevent the pet from stealing keyboard focus when it auto-moves

### Mouse Events
- **Click vs double-click**: Always use the debounce timer pattern (§5) — without it, single clicks fire before double-click events arrive
- **Drag vs click**: Use `manhattanLength() > 8` threshold — don't use `distance` which is slower
- **mouseDoubleClickEvent order**: It fires before the *second* release event, but after the first press-release cycle

### Animation
- **Timer intervals**: Don't use `QPropertyAnimation` for continuous movement — it creates too many objects. Use `QTimer` + manual lerp.
- **Frame rate**: 40ms (25fps) is smooth enough for character animation. 25ms (40fps) for positional movement.
- **Stop all timers on hide**: If the user hides the window, timers still fire. Stop them in `hide()`, restart in `show()`.

### macOS Packaging
- **Gatekeeper**: First launch of a `.app` from an unsigned developer will be blocked. Tell users: *System Settings → Privacy & Security → "Open anyway"*. Or right-click the app → Open.
- **Environment vars**: `.app` launched via Finder does NOT inherit shell env vars. The launcher must explicitly source `~/.zshrc` or `~/.zprofile`.
- **Python path**: Use `/usr/bin/python3` for system Python or `which python3` from the script — never hardcode a brew/conda path that differs per machine.

### API
- **Timeout**: Set `requests.post(..., timeout=15)` to avoid hanging the UI thread
- **Error display**: Show API errors inline in the chat widget, not in a dialog (less disruptive for a pet)
- **API key in code**: NEVER hardcode — always read from env var
- **Streaming**: Don't use streaming with PySide6 unless you handle it in a QThread — blocking the paint thread freezes the character

---

## References

- `references/dumbo-pet-example.md` — Full source walkthrough of a desktop pet (V1: 3-timer, API-driven)
- `references/V2-single-timer-pure-drawing.md` — V2: single 60fps timer, sine-driven parameters, pure QPainter, no API
- `references/testing-patterns.md` — Headless testing checklist, offscreen render verification, process-level launch checks, complete test script
