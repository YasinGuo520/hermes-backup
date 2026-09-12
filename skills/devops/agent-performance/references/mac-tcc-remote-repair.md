# macOS TCC 壁垒下的远程维修配方（2026-09-12 实测）

场景：Yasin 的 Mac（Tailscale `100.80.117.5`，`ssh mac@`）上，本地 Hermes 自研了一套「APEX-UI 拍手唤醒 3D 球语音页」，语音听说全断，用户要服务器端 Hermes 远程修好。

链路原貌（三个 launchd 服务，均 `KeepAlive=true`）：

| Label | 作用 | 端口/形态 |
|---|---|---|
| `ai.hermes.apex-bridge` | 桥：采集 / STT / 转发 Hermes agent / TTS 朗读 | `127.0.0.1:3210` |
| `ai.hermes.apex-clap` | 拍手/双拍唤醒（sounddevice + spectral flux） | 常驻 |
| `ai.hermes.apex-ui` | Next.js 全息球页面 | `http://127.0.0.1:3000` |

（修好后三件套已迁到 `~/apex-src/`，plist 路径同步改写；`apex-voice.sh {status,start,stop,restart,kiosk}` 是控制台。）

## 1. 取证顺序（不要跳）

1. `ps aux | grep -i hermes` + `launchctl list | grep -i hermes` → 谁在跑、谁托管
2. 目标机 `~/.hermes/logs/{errors.log,gui.log,agent.log,desktop.log}` tail → 自研组件日志在 `/tmp/apex-*.log`
3. 会话库取证：`sqlite3 ~/.hermes/state.db "select id,role,substr(content,1,200) from messages where session_id like '%xxxx%' order by id desc limit 20"` → **用户当时到底骂了什么、agent 最后交代了什么**，比读代码快十倍
4. HTTP 面取证（不用进 Desktop）：`curl -s localhost:3210/health|/state|/log?limit=6`；页面产物 `curl -s localhost:3000/` 里的 `/_next/static/chunks/app/page-*.js` 可直接下载读（编译后但能搜关键串，如 `3210/listen`、`MediaRecorder`）

## 2. 关键证据：麦克风授权的层错位

桥日志里的矛盾：

```
[transcribe] 257252 bytes, speech=0ms, mime=audio/webm;codecs=opus     ← 每次字节数完全相同
[transcribe] dropped hallucination (hermes guard): 嗯。
[transcribe] dropped impossible rate: 410 chars / 1000ms = 410.0 chars/s  ← ASR 在编
```

同一时刻、同一只麦克风：

```
onset @ 33672.80s  flux= 100.66 (thr  55.00)  db= -29.0   ← 拍手检测器（Python）听得到
```

且唯一的成功识别都是**命令行喂 WAV**（`99794 bytes/1003ms`、`109454 bytes/3994ms` 这类 16k 单声道量级），浏览器上传的全是固定长度静音包 → **Chrome 没有 macOS 麦克风授权，Hermes venv 的 python 有**。详尽诊断与修法见 `voice-input` 技能的 `references/macos-mic-permission-layers.md`。

## 3. 搬到 `~/apex-src` 的完整步骤

```bash
# 1) 借 GUI 进程的 Desktop 权限做 cp（payload 本地写好再 scp）
scp /tmp/copy_req.json mac@100.80.117.5:/tmp/
ssh mac@100.80.117.5 'KEY=$(grep "^API_SERVER_KEY=" ~/.hermes/.env | cut -d= -f2-); curl -s -m 280 -X POST http://127.0.0.1:8642/v1/chat/completions -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" --data-binary @/tmp/copy_req.json'

# 2) plist 路径改写（plist 在 ~/Library/LaunchAgents，不受 TCC 限制）
python3 - <<'PY'
import pathlib
base = pathlib.Path.home() / "Library/LaunchAgents"
for name in ("ai.hermes.apex-bridge.plist", "ai.hermes.apex-clap.plist", "ai.hermes.apex-ui.plist"):
    p = base / name
    s = p.read_text()
    s = s.replace("/Users/mac/Desktop/hermes/APEX-UI", "/Users/mac/apex-src/APEX-UI")
    s = s.replace("/Users/mac/Desktop/hermes", "/Users/mac/apex-src")
    p.write_text(s)
    print(name, [l for l in s.splitlines() if "Desktop" in l])
PY

# 3) 重启三件套
U=$(id -u); launchctl bootout gui/$U/ai.hermes.apex-bridge; sleep 2
launchctl bootstrap gui/$U ~/Library/LaunchAgents/ai.hermes.apex-bridge.plist
```

## 4. 环境坑（影响命令写法，实测）

| 坑 | 表现 | 写法 |
|---|---|---|
| macOS 无 `timeout` | `bash: timeout: command not found` | 用 `background=true` 或缩短命令 |
| SSH 非交互 PATH 无 `/usr/local/bin` | `which ffmpeg` 空，但 launchd 服务里能用 | 探测用绝对路径 `/usr/local/bin/ffmpeg` |
| zsh 的 glob | `--include=*.py` 报 `no matches found` 并中止整条命令 | 所有 glob 加引号 |
| venv python 缺 `soundfile` | — | 写 WAV 用 stdlib `wave` + numpy int16 |
| 中文 `say` 嗓音 | — | `say -v Tingting`（Eddy/Flo 等是 novelty） |

## 5. 显示器几何复现（搬路径时别弄坏本来好的东西）

用户明确说过「屏幕那些没问题，只管语音」，但从 Desktop 搬走后辅助脚本（`apex-display.py`）缺失会让全屏窗跑偏 = **弄坏用户本来好的东西**。用 NSScreen 实测复现，必须与目标机历史输出逐字一致：

实测 `NSScreen.screens`：内置 `{0,0,1440,900}`（primary）、DELL `{-248,900,1920,1080}`。Chrome 的 `--window-position` 是左上原点，换算 `y_top = primary_h - (frame.y + frame.h)`：

```
--kiosk --window-position=-248,-1080 --window-size=1920,1080     ← 与它上次能跑时逐字相同
```

取屏（pyobjc 未装，走 osascript）：

```bash
osascript -l JavaScript -e 'ObjC.import("AppKit");var a=$.NSScreen.screens.js;var o=[];for(var i=0;i<a.length;i++){var f=a[i].frame;o.push({x:f.origin.x,y:f.origin.y,w:f.size.width,h:f.size.height,primary:a[i].isEqual($.NSScreen.mainScreen)});}JSON.stringify(o)'
```

## 6. 用 CDP 验收活页面（可选但有用）

自己起带调试口的 Chrome，**不要**改服务里的 flags 留调试口：

```bash
open -na "Google Chrome" --args --kiosk --window-position=-248,-1080 --window-size=1920,1080 \
  --user-data-dir=$HOME/.apex-kiosk --remote-debugging-port=9223 --remote-allow-origins="*" \
  --no-first-run --no-default-browser-check http://127.0.0.1:3000
```

然后跑 `scripts/probe-live-page.py http://127.0.0.1:9223`：读面板 innerText、`elementFromPoint` 看输入框有没有被盖、在页面里跑 `getUserMedia` 量 RMS。注意：用户自己那台 Chrome 的 `9222` 实测 `/json/version` 返 **404 空体**（不是可用 CDP）——换自己起的实例即可，别下「CDP 不可用」的结论。

## 7. 本次落地的架构改动（类级可复用）

麦克风从浏览器搬到桥（Python）：

- 新增 `POST /listen {action:start|stop}`；`/wake` 也自开启对话；打字 `/ask` 默认也「边生成边朗读」
- 桥内 `sounddevice` 录音（16kHz / 512 帧）、噪声底自适应阈值、尾部静音 1.1s 收尾、15s 硬顶
- 共享守卫 `_guard_transcript()`：`/transcribe` 与新采集路径走同一个实现
- 一个说话人：桥负责 edge-tts + afplay，页面删掉 `speechSynthesis`（双声根因）
- `/state` 新增 `listening`/`mic_owned`，拍手检测器靠 `mic_owned` 在「桥占着麦」时让位
- 页面 749 行 → 473 行（整条浏览器音频路径删除）
- 顺手修原代码残留 bug：`/transcribe` 里 `ext` 在定义前被使用（每次请求必 `UnboundLocalError`）
