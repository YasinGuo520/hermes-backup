---
name: mac-launchd-service-ops
description: "Use when Mac 后台服务莫名全停/要一键启停。launchd 生命周期、睡眠、TCC 验收。"
version: 1.0.0
author: Hermes
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [launchd, macos, keepalive, sleep, tcc, pmset, service-lifecycle, apex-ui]
    related_skills: [mac-local-voice-ui-fix, china-im-channels, server-service-deployment]
---

# Mac 上的 launchd 服务：启停、保活、与「它为什么停了」

**触发**：用户问「得开桌面端才能常驻吗」「怎么退出这个功能」「服务怎么全没了」、
IM 渠道/自研语音 UI 突然无响应、要做一个能双击的启停开关、要验收一段读麦克风的脚本。

适用范围：任何跑在 Mac 上的后台服务（本机实例：`ai.hermes.gateway` + `ai.hermes.apex-{bridge,clap,ui}`）。
APEX 语音链路的**音频层**细节（STT/TTS/VAD/barge-in）在用户自有技能 `mac-local-voice-ui-fix` 里，
本技能只管「服务本身是不是活着、怎么开关、怎么验收」。

## 第一件事：先分清进程是谁起的，再回答「要不要开桌面端」

```bash
launchctl list | egrep -i "hermes|apex|gateway"     # 能列出来 = launchd 管的 job
ls ~/Library/LaunchAgents/*.plist
ps -o pid,ppid,lstart,command -p <PID>              # PPID=1 (/sbin/launchd) = 后台服务
lsof -nP -iTCP:8642 -sTCP:LISTEN                    # 哪个进程在提供这个口
```

判据：**PPID=1 且出现在 `launchctl list`** = 后台服务，**跟任何窗口/桌面端 App 开没开无关**。
2026-09-14 实测：`ai.hermes.gateway` 一个 launchd job 同时管 IM 渠道和 `127.0.0.1:8642`，
所以「长驻」从来不需要桌面端——需要的是**机器别睡**。

## 服务死了？按这个顺序排除（三类真因）

| 真因 | 特征 | 验证 |
|---|---|---|
| **重启后没自启** | `uptime` 比想象的新；服务全无、没报错 | `uptime` vs job 的 `lstart`；`RunAtLoad` 是否为 false |
| **合盖睡眠** | 一段时间窗口内渠道静静哑掉，进度无报错 | `pmset -g log`（见下） |
| **只 bootout 没 bootstrap** | 改完 plist 后服务永久不在 | `launchctl print gui/$(id -u)/<label>` |

### 合盖睡眠：`sleep 0` 拦不住

```bash
pmset -g log | egrep "Entering Sleep|Wake from|DarkWake" | tail -12
uptime
pmset -g | egrep -i "^ *sleep|displaysleep|standby|womp"
```

读法：`Entering Sleep state due to 'Maintenance Sleep'` = **合盖睡眠**（Deep Idle），
跟 `sleep` 设的分钟数无关；`Wake from … due to EC.PowerButton/User` = 人按了电源键；
`Using BATT/AC (Charge:NN%)` 看得出当时在不在充电（电池档更易合盖睡）。

2026-09-14 实测：用户 09:27 合盖 → 09:26–10:14 一直在 DarkWake/Sleep 循环，
`ai.hermes.gateway` 与 apex 全停，**微信渠道表现为「发不出信息、也不报错」**；
10:14 按电源键唤醒后渠道自己就恢复了。

要「随时都在」只有三条路：**接电源 + 外接屏（clamshell）、`caffeinate`、`sudo pmset -c disablesleep 1`**。
先问用户要哪种，**别自己改电源设置**（这是他的机器习惯）。

## 按需启停（三件套）与 `RunAtLoad` 的语义

模式（实例：`~/apex-src/apex-up.sh` / `apex-down.sh` / `apex-mute.sh`，另配双击图标）：

| 脚本 | 做什么 |
|---|---|
| `*-up.sh` | 逐个 `launchctl bootstrap gui/$U <plist>`（已加载则跳过，用 `launchctl print` 判断）+ `launchctl kickstart gui/$U/<label>`；**依赖顺序：页面 → 主服务 → 耳朵** |
| `*-down.sh` | 逆序 `bootout`，再收拾它拉起的 GUI 子进程 |
| `*-mute.sh` | 只停「耳朵」那个 job，其余保留 |

**关键一步：把 plist 的 `RunAtLoad` 改成 `false`。** 否则 `bootout` 后**下次登录 launchd 又把它拉起来**，
用户「我不想常驻」的意图在重启后失效。代价与补丁两边都要记住：
- 改 plist 后必须 `bootout` + `bootstrap` 才重读（`kickstart -k` 用的是缓存的 job 定义）；
- 而 `RunAtLoad=false` 时 bootstrap **不会自己起进程** → 启脚本里要补 `launchctl kickstart`。

其它实测到的坑：
- **清子进程只能认自己的 profile**：`pkill -f "user-data-dir=$HOME/.apex-kiosk"`。
  宽泛的 `user-data-dir` 会误杀到别的 Electron 应用（本机抖音就走这个参数）。
- **双击图标用 `osacompile -o "$HOME/Applications/X.app" -e 'do shell script …'`**：
  写 `~/Desktop` 会被 TCC 挡（ssh 上下文无权限），`~/Applications` 还能直接拖进 Dock。
- **开机不自启 ≠ 登录不自启**：只把进程 kill 掉，下次登录它又回来；必须改 `RunAtLoad`。

## ⚠️ 麦克风（及其它 TCC 权限）的验收必须走 launchd

2026-09-13 实测：`ssh mac … python clap-wake.py --verbose` 能正常打开 `sd.InputStream`、日志打印
"listening…"，但**外放任何声音都不产生任何事件**（拿到的是静音且不报错）；**同一份脚本用 launchd 起就正常**。
macOS 把麦克风授权记在「Aqua 会话里启动的那个二进制」上，ssh/终端会话的副本不在其列。

两条推论：
1. 启停脚本必须走 `launchctl bootstrap`，**不能直接 `python … &`**；
2. 注入式验收要造临时 launchd job：`scripts/make-test-launchd-job.py`（克隆线上 plist、加 `--verbose`、
   把任何往外发请求的变量指向死端口如 `http://127.0.0.1:9/wake` 以免弹真窗）→ `bootstrap` → 播音频 →
   读 `/tmp` 日志 → `bootout` + 删 plist。

**验收要做 A/B，不要只跑一次**：同一段音频跑两遍，一遍默认、一遍把开关关掉（如
`--env APEX_CLAP_IGNORE_MEDIA=0`），两份日志的差异才是「是那个开关在起作用」的证明。
第一轮只能证明「没弹窗」，证明不了「为什么没弹」。

做「声明式开关」时：所有阈值/开关走环境变量，因为服务是 launchd 起的，plist 的
`EnvironmentVariables` 就是调参面板，不用改代码。

## 「现在机器在放声音吗」——注意哪些判据不可用

| 判据 | 可用性 |
|---|---|
| CoreAudio `kAudioDevicePropertyDeviceIsRunningSomewhere`（默认输出 `dOut` 上查 `gone`） | ✅ 静默 0 / 播放中 1 / 停后 0；`say`、`afplay` 都认。脚本：`scripts/coreaudio-media-probe.py` |
| `pmset -g assertions` 找 coreaudiod | ❌ 常驻那一条是**麦克风输入**的 assertion，静室也永远是 1 |

这是「她听到自己在放的声音就自己弹窗/自己回答」类 bug 的情境型守卫输入（**同一段音频、同一检测器，
只换这个开关就一边弹一边不弹**）。代价要提前说清：**正在放声音时拍手叫不动她**（暂停再拍），
手机/蓝牙音箱外放检测不到。

## 改完/被叫停时的验尸与取证

- 用户说「你先别改」= **立即停手**，且连**只读深挖也要先声明一句「全在只读查询，没动任何东西」**。
- 报「我没动过线上」要拿哈希说话：本地草稿 vs Mac 线上文件各算一次 `md5 -q`（macOS）/ `md5sum`，
  并把「改动只在本地草稿、未部署」+「Mac 上多出哪些临时文件」列清。部署后再复核一次 md5。
- 改前先备份：`cp x.py x.py.bak-<用途>-<时间戳>`，报告里同时给回退命令。
- plist 也备份（`*.bak-runatload-<日期>`），因为改 `RunAtLoad` 就是要改它。

## 支持文件

| 文件 | 用途 |
|---|---|
| `scripts/coreaudio-media-probe.py` | 一行回答「现在有没有 App 在放声音」，exit 1=在放 / 0=静 / 2=探测失败 |
| `scripts/make-test-launchd-job.py` | 克隆线上 plist 造临时验收 job（`--arg` / `--env` / `--out`），麦克风类脚本的唯一可靠验收姿势 |

## 关联

- `mac-local-voice-ui-fix`（**用户自有，改动前需 `hermes curator adopt`**）— APEX 语音链路的音频层细节：
  TCC 与浏览器采集、服务端录音 VAD、媒体误唤醒、日志判读。
- `china-im-channels` — 渠道断连排查（含「先确认宿主没睡」）。
- `server-service-deployment` — 云服务器侧（systemd/防火墙），与 Mac 侧 launchd 对照看。
