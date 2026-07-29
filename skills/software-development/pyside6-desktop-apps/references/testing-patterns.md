# PySide6 Testing Patterns

*Derived from the Dumbo Desktop Pet session (2026-06-29)*

## Test Matrix for a Desktop Pet

Below is the verification checklist used for the Dumbo pet. Adapt the state/expression names to your own character.

| # | Test | Method | What It Catches |
|---|------|--------|-----------------|
| 1 | Syntax validity | `ast.parse(open(file).read())` | Typos, missing parens, unclosed strings |
| 2 | Import resolution | `python3 -c "import PySide6, requests"` | Missing dependencies |
| 3 | Window flags | `assert w.windowFlags() & Qt.FramelessWindowHint` | Wrong flag combination (e.g., Tool missing) |
| 4 | Expression cycling | Call `cycle_expression()` 3×, assert round-trip to start | State machine broken |
| 5 | Screen placement | Call `_place_random()`, assert valid coords | Screen rect computation |
| 6 | Render non-empty | `.render()` to QImage, assert any non-transparent pixel | All paintEvent paths silently broken |
| 7 | Render ALL states | Loop over every expression/state, repeat test 6 | Missing draw logic for specific expression |
| 8 | Chat dialog | Instantiate, check title & system prompt | Broken QDialog subclass |
| 9 | API configuration | Assert URL, model, env-var-reader exist | Runtime failures on first chat |
| 10 | Process launch | `pgrep -f mac_pet.py` after `open AppName.app` | App launched but crashed silently |

## Complete Headless Test Script (PySide6)

```python
import sys, os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt

app = QApplication(sys.argv)
from mac_pet import DumboPet, ChatDialog, W, H

# 1. Window creation
pet = DumboPet()
assert pet.width() == W and pet.height() == H
print(f'✅ 窗口: {W}x{H}')

# 2. Expression cycling
assert pet.expr == 'happy'
pet._cycle_expression(); assert pet.expr == 'dazed'
pet._cycle_expression(); assert pet.expr == 'sleepy'
pet._cycle_expression(); assert pet.expr == 'happy'
print('✅ 表情循环: happy → dazed → sleepy → happy')

# 3. Window flags
flags = pet.windowFlags()
assert flags & Qt.FramelessWindowHint
assert flags & Qt.Tool
print('✅ 窗口标志: Frameless + Tool')

# 4. Screen placement
pet._place_random()
assert isinstance(pet.x(), int) and isinstance(pet.y(), int)
print(f'✅ 随机放置: ({pet.x()}, {pet.y()})')

# 5. Render all expressions
for expr in ['happy', 'dazed', 'sleepy']:
    pet.expr = expr
    img = QImage(pet.size(), QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    pet.render(p, QPoint(0, 0))
    p.end()
    has = any(img.pixelColor(x,y).alpha() > 0 for y in range(img.height()) for x in range(img.width()))
    assert has
    print(f'✅ 渲染 \"{expr}\": 有内容')

# 6. Chat dialog
chat = ChatDialog()
assert 'Dumbo' in chat.messages[0]['content'] or '小飞象' in chat.messages[0]['content']
print(f'✅ 聊天框: \"{chat.windowTitle()}\"')

pet.close(); chat.close()
print('\n🎉 全部测试通过')
```

## macOS Process Check

```bash
# Launch the app
open /path/to/AppName.app
sleep 2

# Verify it's running
pgrep -f mac_pet.py && echo "✅ 进程运行中"

# Watch CPU usage (active animation → 5-15% CPU)
ps aux | grep mac_pet.py | grep -v grep

# Kill cleanly
kill $(pgrep -f mac_pet.py)
```

## osascript Window Info (use sparingly)

```python
import subprocess
r = subprocess.run(
    ['osascript', '-e',
     'tell app "System Events" to get every window of every process'],
    capture_output=True, text=True, timeout=5
)
```

**Warning:** This prompts for Accessibility permissions on first use and **hangs** until the user responds. Always set `timeout=5` and catch `TimeoutExpired`. If it times out, fall back to `pgrep`.
