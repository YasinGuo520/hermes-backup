# APEX 语音回路的打断实现（2026-09-12 实测）

本文件是 `voice-barge-in` 的落地细节。**先读 SKILL.md 的四条坑，再看这里。**

## 文件挂点（Mac `~/apex-src/`）

| 文件 | 改动 |
|---|---|
| `apex-hermes-bridge.py` | `_afplay()` 可掐（Popen+terminate，支持 `-v` 音量）；`_cut_requested()`；`_Speaker(judge=...)` 加 `aborted`/`replay`；`_ask_hermes_stream` 读循环里 `if speak.aborted: break`；`_handle_voice_ask` 里 `_STOP_PLAY.clear()` → `_arm_barge()` → `speak.finish()` → `_disarm_barge()`；`_judge_barge()` 返回 `barge/cut/resume`；`_conversation` 每轮先取 `_BARGE_PENDING`；`/state.barge`；`POST /interrupt` |
| `apex_barge.py` | 新模块（耳朵）：`Monitor.arm/disarm/set_playing/cue_pending/clear_cue/harvest/note_false_alarm/dump` + 纯函数 `_thr_playing/_ref_step/_thr_quiet` + `--selftest` |
| `clap-wake.py` | **还原原版**（单拍打断已撤，见 SKILL.md 坑 3） |

本地工作副本：`~/Desktop/hermes/apex-work/`（服务器侧改 → scp 到 Mac）。

⚠️ **半成品警告**：`~/Desktop/hermes/apex-work/apex-hermes-bridge.py` 里 `_afplay()` 已引用
`TTS_VOLUME`，但该变量**还没定义**（变量定义那一步没写完）。直接 scp 上去会 `NameError`，
 **部署前先补**：`TTS_VOLUME = float(os.environ.get("APEX_TTS_VOLUME", "1.0"))`（模块级），
或在 plist 加 `APEX_TTS_VOLUME` 并把默认值设成想要的音量。

## 常量与实测数字

| 常量 | 值 | 实测依据 |
|---|---|---|
| `SR` / `BLOCK` / `BLOCK_MS` | 16000 / 512 / 32ms | 与录音函数同档，STT 要的就是 16k |
| `margin_db` | 5.0（`APEX_BARGE_MARGIN_DB`） | 她回放峰值 -18.5 → 门槛 -13.5 |
| `sustain_ms` | 420（约 13 块） | 短于它的抬起（她的重音）不算 |
| `floor_db` | -44（绝对下限） | 安静房间不误触发 |
| `REF_LEARN_S` | 1.2s | 起播只学不判（坑 0） |
| `release_db_s` | 1.5 dB/s | 慢放：音量调小 4s 内自己滑下来 |
| `penalty_db` | +2/次假警报，上限 +8，2 分钟没误判 -1 | 房间/音量变了自愈 |
| `trim_s` / `max_s` | 0.9s / 7.0s | 尾静音收尾 / 一次插话最长摘录 |

环境（实测）：系统输出音量 57%、输入 73%；她自己的回放进麦 **中位数 -37.4 / 峰值 -18.5 dBFS**；
注入测试（edge-tts 语音 + `afplay -v 3`）拿到 cue：level -24.8 / thr -31.1（那时基线还是中位数）。

## 日志签名（对表用）

```
[barge] cue @22:42:20: level -24.8 / thr -31.1 / 她的档 -18.6 dB / +0 / 416 ms (她在播)
[barge] voice 生效：speech=3104ms / 4.9s → '等一下，先别念了，我问你一个问题，你听我说完。'（这句当下一轮提问）
[ask] '请你用中文说一段大约三百字的自我介绍…' -> 408 chars, spoke 1/1 lines (voice) [打断]
[barge] 插话那句接着走：'等一下，先别念了。我问你一个问题，你听我说完。'
[barge] voice: 转写是空的 → 当她自己的回声/咳嗽，她继续说完      ← 假警报（会重播当前句）
[barge] clap: 掐完没人说话 {...}                              ← 拍手路径（已撤）
```

**事故签名**（坑 0）：`/state` 里 `cues` 一路涨到 21、`ref_db: None`、`thr_db: -44.0`，
而她 `spoke 1/1 lines [打断]` —— 基线没学到 + 每句被掐。

## 注入法验收脚本骨架

```bash
PY=$HOME/.hermes/hermes-agent/venv/bin/python
# 1) 生成一段和她不同的中文
$PY - <<'PY'
import asyncio, edge_tts
async def main():
    c = edge_tts.Communicate("等一下，先别念了，我问你一个问题，你听我说完。", "zh-CN-XiaoyiNeural")
    with open("/tmp/barge-inject.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
asyncio.run(main())
PY
# 2) 静默验收：她起一轮，确认 cues==0 且没有 [打断]
M=$(wc -l < /tmp/apex-bridge.log)
(curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"prompt":"请用三句话介绍一下你自己。","voice":true}' http://127.0.0.1:3210/ask >/dev/null &)
sleep 6; curl -s http://127.0.0.1:3210/state | $PY -c "import sys,json;print(json.load(sys.stdin)['barge'])"
# 3) 注入插话（-v 1 接近正常音量；-v 3 是加压）
afplay -v 1 /tmp/barge-inject.mp3
sleep 12; tail -n +$((M+1)) /tmp/apex-bridge.log | grep -E 'barge|ask|listen'
```

⚠️ 脚本里别用 `set -u` + 函数局部变量混着中文 echo（本次踩过 `vol: unbound variable` 把场景 B 整段
跳过）；两个场景直接内联写，别包函数。

## 实施顺序（下次接着干）

1. 补 `TTS_VOLUME` 定义 → scp `apex_barge.py` + `apex-hermes-bridge.py` → Mac venv `py_compile` → `--selftest`。
2. `launchctl kickstart -k gui/$(id -u)/ai.hermes.apex-bridge`；确认 `clap-wake.py` 是**原版**（`grep single clap-wake.py` 应无输出）。
3. 静默验收（`cues==0`、`spoke n/n`、无 `[打断]`）。
4. 把 plist 的 `APEX_TTS_VOLUME` 调到 ~0.45 → kickstart → 再看 `/state.barge.ref_db`（期望从 -18.6 掉到 -28 上下、`thr_db` 到 -23 上下）。
5. 让 Yasin 真人在场说一句「等一下」→ 从日志确认 `[barge] voice 生效` → 报告。
6. 若他正常音量仍打不断：先降 TTS 音量，再考虑 `APEX_BARGE_MARGIN_DB` 3-4（会更容易误判，靠 penalty 自愈）。

## 回退

```bash
cd ~/apex-src && cp apex-hermes-bridge.py.bak-barge-<TS> apex-hermes-bridge.py \
  && cp clap-wake.py.bak-barge-<TS> clap-wake.py && launchctl kickstart -k gui/$(id -u)/ai.hermes.apex-bridge
```
打断功能本身也可整体关掉：桥里 `BARGE_ENABLED=False`（或让 `import apex_barge` 失败），
原有语音链路行为不变——这是设计时就留好的降级路径。
