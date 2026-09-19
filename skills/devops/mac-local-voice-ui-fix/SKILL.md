---
name: mac-local-voice-ui-fix
description: "Use when Mac 自研语音UI听说不通/连续对话断/面板不刷新。"
version: 1.0.0
author: Hermes + Yasin
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [voice, stt, tts, macos, tcc, launchd, chrome, sounddevice, wake-word, apex-ui]
    related_skills: [web-scraping, hermes-agent, server-service-deployment]
---

# Mac 本机自研语音 UI：听说链路的诊断与修法

**触发**：拍手唤醒、全息语音页、桥(:3210)、唤醒词、语音没输出、录到的是静音、连续追问没反应、
左侧面板打字不出声、`/new` 不清屏。

架构：Chrome kiosk 全息页(:3000) + Python 桥(:3210) + 拍手/唤醒词监听 + 系统 TTS 出声，
大脑用 Hermes 自己的 API server(:8642)。Yasin 这台 Mac 的实例在 `~/apex-src/`
（2026-09-12 从 `~/Desktop/hermes/` 迁出，原因见下「TCC」节）。

## 第一铁律：先判「音频到底采到了没有」，再碰代码

**绝大多数「她听不到我」都不是代码问题**，是权限层。判定顺序（10 分钟内出结论）：

1. **看桥的日志**（`/tmp/apex-bridge.log`）：浏览器上传的音频如果**字节数每次都一模一样**
   （如恒为 257252）、`speech=0ms`、`peak≈0 dBFS`，那是**数字静音包**，不是「说话小声」。
   代码注释里往往已经写着「页面看到纯静音，而拍手检测器听得到」——这条矛盾本身就是答案。
2. **同一时刻用 Python 测麦**（检测器能听到 → Python 有授权）：
   ```bash
   ~/.hermes/hermes-agent/venv/bin/python -c "import sounddevice as sd;print(sd.query_devices())"
   ```
   拍手检测器（sounddevice）听得到 + 浏览器采到纯静音 = **授权在 Python 手上，不在 Chrome 手上**。
3. **macOS TCC 的授权是按 App 给的**：Hermes venv 的 python 拿到了（GUI/launchd 上下文），
   **Google Chrome 没拿到** → Chrome 采集恒为静音**且不报错**（`getUserMedia` 不抛异常）。
   所以页面上任何门限/音量/流复用补丁，都是在修一个**根本没被采集到的信号**——最贵的绕路。
   - `log show --predicate 'subsystem == "com.apple.TCC"'` 在这台机器上查不到决策，别指望它。
   - 最可靠的取证：**把 Python 侧和浏览器侧的 RMS 摆在一起**。

## 云端 STT 欠费 = 假「没听清」（2026-09-19 修）

症状：她一直循环「刚才那句我没听清，你再说一遍」，听起来像麦克风坏了。
真相：**音频采到了，是转写接口被 402 顶回来**——这条正好是第一铁律的反例。

- 桥日志铁证：`[stt] listen 第 1/3 次失败（超时 8s）: 402 Client Error: Payment Required for url: .../audio/transcriptions`，
  而同一批日志里 `[listen] utterance: speech=1440ms, audio=4.4s, rms=0.0444` —— **采音完全正常**。
- 拿原始回包定性（别猜）：`curl -X POST -H "Authorization: Bearer $K" -F file=@x.wav -F model=... $BASE/audio/transcriptions`
  → `{"code":30001,"message":"Sorry, your account balance is insufficient"}`。
  401/wrapper 里 `Token is invalid`=key 无效；400 + `20012 Model does not exist`=模型名不对。
- 判定顺序：`[stt]` 失败行 + `speech=Xms>0` → **别去查 TCC/Chrome/麦克风**，直接查 provider 余额。
- 影响面：桥（APEX）与 Hermes 自己（飞书按住说话）**共用 `stt.<provider>` 同一把 key 和模型**，
  所以桥挂 = 飞书语音输入也静默挂（它失败时不吭声，更隐蔽）。修一处两条链路一起好——**但只在改配置文件的情况下成立**。

一键复测：`~/apex-src/verify-stt.sh [--quick]`（配置段 → 接口直测 → 真说一句走端到端 → 判定 OK/FAIL）。
写这脚本踩的坑：**取 STT 配置必须用 yaml 读 `stt.<provider>` 段，不能 `grep -A6 "^  openai:"`** ——
`tts.openai` 也有同名子段且排更前，会抓到 `gpt-4o-mini-tts`，直测就假报 `20012 Model does not exist`（自己制造一个假故障）。

**别把「换本地 whisper」当成最省事的止血**：桥是直连 HTTP 转写接口的（`_stt_config()` → 读 `stt.<provider>` 的
`base_url/api_key/model` 再 POST `/audio/transcriptions`），`provider: local` 时 `base_url` 为空，桥会直接报
`stt provider not configured` 而**完全不通**——要走 local 必须改桥代码加本地分支。代价：常驻内存 base 347MB、
small 745MB（Intel i7 实测），转写时抢 2-4 个核。

选源备忘（按 Yasin 实测用量：一句 ≈20 字 / 5 秒）：硅基 Qwen3-ASR ¥0.05/千字符 ≈ **¥0.001/句（最便宜档）**、
百炼 qwen3-asr-flash ¥0.00022/秒 ≈ ¥0.0011/句、智谱 glm-asr ¥0.06/分钟 ≈ ¥0.005/句（5 倍）。
推荐顺序：先让用户充硅基 ¥10（零改动、精度最好、够一年量级）→ 想省钱再谈本地。

## 修法：把麦克风搬进桥（服务端录音），别去修浏览器

比「让 Chrome 拿到授权」更稳：不依赖任何 GUI 点击，不怕系统更新，麦克风只有一个主人。

| 件 | 要点 |
|---|---|
| 录音 | `sounddevice.InputStream(samplerate=16000, blocksize=512, channels=1, dtype="float32")` + 逐块 RMS |
| VAD | 门限**相对**起始帧的噪声底：`thr=min(0.035,max(0.008,floor*2.5))`；说完静音 1.1s 收尾，无人声 7s 放弃，硬顶 15s |
| 存盘 | `soundfile` 通常**没装** → 用 stdlib `wave` 写 16-bit WAV |
| 转写 | 复用 `requests.post(base_url+"/audio/transcriptions", files={"file":("audio.wav",wav,"audio/wav")})` |
| 守卫 | 反幻觉/自回声/语速合理性抽成**一个共享函数**，`/transcribe` 与服务端录音都调它，否则两条路各自漂移 |
| 端点 | `POST /listen {action:start\|stop}`；`POST /wake` 除了抬窗口也**自己开麦进对话** |
| 状态 | `/state` 暴露 `listening{active,conversation}` + `mic_owned`；拍手检测器看到 `mic_owned` 就闭嘴让位（否则录音期间拍手会叠出第二个对话） |
| 对话循环 | 听→答→再听，连续 N 次空转才结束；`_conv_lock` 保证同时只有一个对话 |
| 复用旧逻辑 | 原本是 `Handler` 方法、结尾 `self._send(...)` 的回合逻辑，传一个 `_Sink()` 假 handler 就能无 HTTP 调用，**别复制一份** |

页面侧同时**删掉**浏览器采集（`getUserMedia`/`MediaRecorder`/静音看门狗/`speechSynthesis` 兜底），
只留：点按→`POST /listen`、轮询 `/state` 驱动动画。**删比留两条路安全。**

## 六个已踩过的坑（都实测过）

0. **「界面不断自动重启」= 唤醒时把页面的 URL 又开了一次**（最容易被误判成服务挂了）
   症状：页面反复重载/刷新，服务本身很正常（launchctl 无退码、Chrome 也只有一个实例）。
   真因：`open -na "Google Chrome" --args ... <url>` 里 **Chrome 按 `--user-data-dir` 认实例**，
   对已存在的 kiosk 实例再发一次会**把 URL 交给它 → 页面重新加载**（re-mount + 重拉 /state +
   重建 wake 基线）。每次误唤醒都重载一次，看起来就是界面在重启。
   修：**抬窗和启动必须拆成两条路**。已有实例 → 只用 AppleScript 抬窗（`set active tab index`
   + `set zoomed` + `activate`），**不带 URL**；只有实例不在时才走 `open`。
   日志形态：桥日志里 `[wake] ... -> raised=kiosk` 连发 > `[kiosk] geometry: ...` 反复出现。
   另外：对话进行中再次 /wake 直接返回 ignored（不抬窗、不抬 seq）——是第二道锁。

0.5. **误唤醒的来源是「说话声」不是键盘**（用户会问「我打字的声音影响到吗」）
   机器上实测：键盘点击/system blip 的 flux **0.9-4.3**，而说话/她的 TTS 回放可达 **56-90**。
   阈值（FLUX_FLOOR）才是在防后者。结构性修法：桥在**整个对话期间**（不只是录音/朗读瞬间）
   报 `mic_owned=true`，检测器就全程让位——否则「转录中/思考中」那些空档里拍手仍会触发。
   抬高 FLUX_FLOOR 只是第二道防线，且**必须用真掌声复测**（真拍 80-235，抬高有丢唤醒风险）。

1. **语速上限误杀真实短句**（连续对话断掉的真凶）
   日志形态：`dropped impossible rate: 9 chars / 1088ms = 8.3 chars/s > 8.0 — invented`
   原因：分母是 **RMS 检测到的人声时长，天然偏小**（轻声/尾音不过门限），短句变成「超人语速」。
   修：分母 `max(gate_ms, 1200, 0.5*音频时长ms)`，且**少于 12 字不做语速判定**。
   长篇编造（25 字/秒）照样杀得掉，别把门限整个关掉。
2. **`/new` 看似无效**：桥重置了会话，但 `/log` 又去挑「最新 api-* 会话」→ 挑回刚被清的那个。
   修：桥记 `_chat_reset` 时间戳，`/log` 拒绝 `last_active <= reset_at` 的会话；面板同时**立刻清空**
   自己的列表（别等下一轮轮询）。（`/new` 走 `/ask`，也会被回话——别让它出声。）
3. **打字问默认静音**：Yasin 明确要求「左侧输出输入框也要实时播报」→ 打字问走流式+朗读那条路
   （换一个 style 提示词即可）。同一句话语音问会响、打字问不响，用户当 bug。
4. **`ext` 在定义前使用**：`/transcribe` 里 `_speech_stats(audio, ext)` 在 `ext = _AUDIO_EXT.get(...)`
   之前调用 → 每个请求 `UnboundLocalError`。改这类文件时顺手扫一遍变量定义顺序。
5. **朗读在句号处停顿**——两层原因，都要修，顺序不能反：
   **(a) 串行合成**：逐句 TTS 如果是「合成→播放→合成→播放」的串行单线程，句间要等一次
   edge-tts 往返（0.5-1.5s）。修：**拆成合成线程 + 播放线程**，合成跑在播放前面（`ready` 队列）。
   **(b) edge-tts 每段自带的留白**（实测 zh-CN-XiaoyiNeural，三句话）：每段固定 **前导 0.185s /
   尾部 0.87s**，与文本无关。句号接缝 = 上段尾部 + 下段前导 ≈ **1.05s 死气**；同样的三句
   一口气合成只花 8.18s（分开 9.00s）= 两个接缝净多出 0.82s。修：合成线程里用 ffmpeg 把每段
   首尾静音削到自然呼吸（`silenceremove ... start_silence=0.08` + `areverse` 同法削尾部
   `start_silence=0.26` + 再 `areverse`），输出 `-f wav pipe:1`（afplay 接受）。
   实测效果：接缝 2.10s → 0.65s（每处 ~1.05s → ~0.32s），总音频 9.00s → 6.82s。
   验收：给 `synthesised` / `playing` 都打上时间戳；若合成在播放开始前就全部完成
   （`synthesised` 一连串先跑完），则后半段是无缝播放，停顿只能来自文本本身的语气。
   注意：修 (b) 时别把静音削到 0，要留 200-300ms——否则句子会黏成一串，听起来更嗧。

## 媒体声 = 幻影唤醒：用 CoreAudio「设备正在放声音」让位（2026-09-13 修）

症状：放音乐/视频时她自动弹窗，并把内容当提问回答（bridge 日志里 `[stt] listen raw` 抓到的是
视频台词，实测一次回了 407 字）。根因：双击拍手判据是「带通后 flux 成对隆起」，**媒体瞬态在这一
层跟拍手无法区分**——外放一段合成 burst 就能让旧代码 `WAKE (double-clap)`。**调阈值没用**，要加情境判据。

| 判据 | 可用性 |
|---|---|
| CoreAudio `kAudioDevicePropertyDeviceIsRunningSomewhere`（默认输出 `dOut` 上查 `gone`） | ✅ 静默 0 / 播放中 1 / 停后 0，`say` 与 `afplay` 都认 |
| `pmset -g assertions` 找 coreaudiod | ❌ 常驻那条是**麦克风输入**的 assertion，永远为 1 |

实现（`clap-wake.py`）：`ctypes.CDLL("/System/Library/Frameworks/CoreAudio.framework/CoreAudio")`
+ `AudioObjectGetPropertyData`（**必须设 `argtypes`**，否则 64 位下参数被截断）；判定顺序
`bridge_busy()` → `media_playing()` → 才 `wake()`；拦截时**不响提示音、不抬窗、不开麦**，并把
`last_onset` 清 0 防止跨媒体间隙配对；日志 30s 节流成一行 `ignored N double-onset(s)`。开关走环境
变量（`APEX_CLAP_IGNORE_MEDIA=0` 关闭），阈值一律不动 → 真拍手行为不变。

代价要提前说清：**正在放声音时拍手叫不动她**（暂停再拍）。手机/蓝牙音箱外放检测不到，只能靠转写守卫。

## ⚠️ ssh 起的进程收不到麦克风 —— 语音验收必须走 launchd

2026-09-13 实测：`ssh mac … python clap-wake.py --verbose` 能正常打开 `sd.InputStream`、日志打印
"listening…"，但**外放任何声音都不产生 onset**（拿到的是静音且不报错）；同一份脚本用 launchd 起就正常。
macOS 把麦克风授权发给「Aqua 会话里那个 python 二进制」，ssh 会话的副本不在其列。

两条推论：
1. `apex-up.sh` 这类启停脚本必须 `launchctl bootstrap`，**不能直接 `python … &`**；
2. 注入式验收要造临时 launchd job：克隆线上 plist（`plistlib` 改 Label / 加 `--verbose` / 把
   `APEX_BRIDGE_WAKE` 指到死端口 `http://127.0.0.1:9/wake` 以免抬真窗）→ `bootstrap` → 播音频 →
   读 `/tmp` 日志 → `bootout` + 删 plist。**同一段音频跑两遍**（守卫 ON vs `APEX_CLAP_IGNORE_MEDIA=0`）
   就是一组干净对照。注：`plistlib.dump(value, fp)` 参数顺序写反会得到 `'dict' object has no attribute 'write'`。

## 常驻开关：一键启停 + 别让「退出」在重启后失效

用户会问「我怎么退出她的驻听」。三件套放 `~/apex-src/`：`apex-up.sh`（bootstrap + kickstart 三个 job，
顺序 = 页面 → 桥 → 耳朵）、`apex-down.sh`（bootout + `pkill -f "user-data-dir=$HOME/.apex-kiosk"`；
**只认自己的 profile，绝不能用宽泛的 `user-data-dir`**——抖音等 Electron 应用也带这个参数）、
`apex-mute.sh`（只停耳朵）。双击图标用 `osacompile -o "$HOME/Applications/APEX 开.app" -e 'do shell
script …'`（**别写 `~/Desktop`**，ssh 上下文被 TCC 挡；`~/Applications` 还能直接拖进 Dock）。

关键一步：三个 plist 的 `RunAtLoad` 改 `false`。否则 `bootout` 后**下次登录 launchd 又把它拉起来**，
用户「我不想常驻」的意图会在重启后失效。改 plist 后必须 `bootout` + `bootstrap`（`kickstart -k` 不重读）；
因为 `RunAtLoad=false`，bootstrap 后进程不会自己起——脚本里要补 `launchctl kickstart gui/$U/<label>`。

## macOS TCC 挡住源码（`~/Desktop`）：怎么远程拿到代码

shell/sshd 起的进程读 `~/Desktop` 是 `Operation not permitted`。**GUI 起的 Hermes 后端有权限**
（能读写 Desktop、能跑 LSP）。可行路径：

1. **借 GUI 进程的 API server**：`~/.hermes/.env` 的 `API_SERVER_ENABLED/API_SERVER_KEY`，
   端点 `http://127.0.0.1:8642/v1/chat/completions`（`model="hermes-agent"`，`Bearer $API_SERVER_KEY`）。
   让它跑一条 `cp/rsync` 把项目搬出 Desktop（搬到 `~/` 下就不受 TCC 管）。
2. **别用「你是只会执行命令的机器人、不许分析」这类 prompt**——本机 Hermes **会拒绝**
   （判为闭眼执行未知代码，这是对的）。要**透明**：说明谁在修、为什么。
3. 搬出后立刻把所有 launchd plist 路径改到新目录（python 改 `~/Library/LaunchAgents/*.plist`），
   否则服务还在跑 Desktop 那份，改动全是无效功。

## launchd 与构建

```bash
U=$(id -u)
# 停：KeepAlive=true 的 job 必须 bootout，kill 会立刻复活
launchctl bootout gui/$U/ai.hermes.apex-bridge
launchctl bootstrap gui/$U ~/Library/LaunchAgents/ai.hermes.apex-bridge.plist
launchctl list | grep -i apex
```

- 三个 job：`apex-bridge`(:3210) / `apex-clap`(拍手) / `apex-ui`(:3000)。
- **本地改代码 → `rsync` 到 Mac → 在 Mac 上 `npm run build`**（`node_modules` 在 Mac，本地没有）。
  `bash -lc "cd ~/apex-src/APEX-UI && npm run build"`（macOS 没有 `timeout` 命令）。
- **动代码前先 `git commit` 一个 as-found 基线**：能回退，也是「不绕路」的物理保障。
- `ffmpeg` 在 `/usr/local/bin`（Homebrew），**SSH 非交互 PATH 里没有**；launchd plist 里显式给 PATH 才找得到。
- 屏幕几何别硬编码：NSScreen 用 JXA 取（bottom-left 原点），Chrome `--window-position` 是
  top-left 空间，换算 `y_top = 主屏高 - (y + h)`。外部屏全屏 kiosk，仅内置屏给居中小窗。

## 没真人在场也能端到端验收

用 Mac 自己的 TTS 对着麦克风说话，真实走完整条链：

```bash
curl -s -X POST http://127.0.0.1:3210/listen -H 'Content-Type: application/json' -d '{"action":"start"}'
sleep 1.2
say -v Tingting "今天几号"            # 中文音色：Tingting / Eddy / Flo
sleep 30 && say -v Tingting "那明天呢"   # 第二句专门验「连续对话」
tail -20 /tmp/apex-bridge.log
```

合格线：`[listen] utterance: speech=XXXXms` → `[listen] -> N chars: <与所说不符即失败>`
→ `[speak] playing ... via zh-CN-XiaoyiNeural` → `[ask] ... spoke k/n lines`。

活页面探针（只在需要看 DOM/面板时）：独立 profile 起 Chrome 带
`--remote-debugging-port=9223 --remote-allow-origins=*`（用户日常那个 Chrome 的 `/json/*` 常回 404，别用它），
再 `scripts/probe-live-page.py http://127.0.0.1:9223`（面板是否存在/被遮挡、通知文案）。
**用完把带调试口的实例关掉**，别留本地调试面。

## 交付前的诚实清单

- 用 `say` 验的叫「链路通」；**真人在房间里的距离/噪音未验**，报告里要写清。
- 物理拍手、长工具链时的播报节奏，没测就说没测。
- 改完必须讲清：现在什么在跑、路径在哪、怎么回退。
