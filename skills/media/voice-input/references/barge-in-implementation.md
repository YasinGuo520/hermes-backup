# Barge-in 实现配方（本机语音回路）

配套：`voice-input` SKILL.md 的「Real-time voice loop / barge-in」一节。示例环境是一个常驻桥进程
（Python + `sounddevice` 录音 + TTS 播放 + SSE 流式回合），换别的实现也用同一套判据。

## 两条腿的挂点

| 腿 | 要点 |
|---|---|
| **掐（输出侧）** | 播放不能阻塞：`subprocess.Popen(["afplay", ...])` + 30ms 轮询 + `terminate()`；`_cut_requested()` 为真就掐；`POST /interrupt` 供外部掐；`/state` 暴露 `barge{cue,ref,thr,peak,penalty}` 供自查 |
| **听（输入侧）** | 耳朵做成**独立模块**，桥侧 `try/except import`：起不来就 `BARGE_ENABLED=False`，**原有语音链路一行行为不变**（最关键的降级设计）。`arm()/disarm()` 跟着回合生命周期；回合结束**先关耳朵**再把输入设备让给录音函数，别两个流抢设备 |
| **衔接** | 播放循环拿到 "cut" 后先问判定，再决定「重播当前句」还是「放弃整个回合」；SSE 读循环检测 `aborted` → `break`（关流 = 对端收到 SIGINT，剩下的字不再烧 token） |

## 旋钮（全部走环境变量，调参不改代码）

| 常量 | 典型值 | 依据 |
|---|---|---|
| `SR` / `BLOCK` / `BLOCK_MS` | 16000 / 512 / 32ms | 与录音函数同档，STT 要的就是 16k |
| `margin_db` | 5.0，可降到 0 或负（如 -1.5） | 门槛 = 她的档 + margin；她回放峰值 -18.5 dBFS → 门槛 -13.5 等于要用户吼 |
| `sustain_ms` | 420（约 13 块） | 短于它的抬起（她自己的重音）不算 → 单个词可能不够，要主动告诉用户「喊一整句才触发」 |
| `floor_db` | -44 | 安静房间绝对下限 |
| `REF_LEARN_S` | 1.2s | 起播只学不判 |
| `release_db_s` | 1.5 dB/s | 慢放：音量调小后 4s 内自己滑下来 |
| `penalty_db` | +2/次假警报，上限 +8，2 分钟没误判 -1 | 房间/音量变了自愈；**只对耳朵自己触发的 cue 收紧**，外部（拍手/按钮）触发的别拿来调耳朵阈值 |
| `gap_keep_s` | 2.5s | 块间宽限：距上次停播超过它才算「她重新开口」 |
| `trim_s` / `max_s` | 0.9s / 7.0s | 尾静音收尾 / 单次插话最长摘录 |
| TTS 音量 | `*_TTS_VOLUME`（如 0.45–0.6） | **降她的播放音量是唯一有效的门槛杠杆**：回声低 6 dB，可行门槛就低 6 dB |

## 日志签名（对表用）

```
[barge] cue @22:42:20: level -24.8 / thr -31.1 / 她的档 -18.6 dB / +0 / 416 ms (她在播)
[barge] voice 生效：speech=3104ms / 4.9s → '等一下，先别念了…'（这句当下一轮提问）
[barge] voice: 转写是空的 → 当她自己的回声/咳嗽，她继续说完      ← 假警报（当前句重播一次）
[ask] '…' -> 408 chars, spoke 1/1 lines (voice) [打断]
[barge] 回合小结: 她的档 X / 麦的峰值 Y / 中位 Z / cue N / 门槛 T / 误判收紧 +d
```

判读只认两行：① `cue` 之后必有「真插话」或「转写是空的（假警报）」；② 回合小结的
**峰值 Y 就是用户这轮到底进了多少 dB**。`Y ≈ 她的档` = 他插话那一刻的声音根本没进麦（时机/朝向）——**不是阈值问题，别再调旋钮**。

## 部署与回退

```bash
# 只改代码 → kickstart 够；改了 plist 必须 bootout + bootstrap（kickstart -k 用缓存的 job 定义，不重读 plist）
python3 -m py_compile barge_module.py && python3 barge_module.py --selftest
launchctl kickstart -k gui/$(id -u)/<job>
ps -Eww -p <pid> | tr ' ' '\n' | grep <前缀>_     # 验环境变量真进了进程
```
- **改出声/录音路径前先备份**（`cp X.py X.py.bak-<用途>-<时间戳>`）并记下回退命令。
- ⚠️ **还原文件 ≠ 还原进程**：`cp x.py.bak x.py` 之后必须重启那个 job，否则跑着的仍是改过的代码。
- 整体关掉打断功能：`BARGE_ENABLED=False`（或让 import 失败），原链路行为不变。

## 交付纪律

1. 先跑**静默验收**（`scripts/barge-silent-acceptance.sh`）：她自己起一轮，`cues == 0` 且没有 `[打断]`——没做这步就交付 = 「她哑了」事故。
2. 再验「他插话」：注入法（`scripts/inject-voice-barge-test.sh`）或真人。
3. 报告里**明写未验项**（真人音量/距离/噪音）。
4. 中途发现的其他故障**只报告不顺手修**，尤其别在打断还没验完时去改别的链路。
