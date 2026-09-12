# 「她的档」被插话污染 → 越插越插不进（2026-09-12 夜 实测定标）

本文件是 `voice-barge-in` 的落地细节（对应 SKILL.md 第 5 号坑）。

## 症状（用户原话）

「为什么好像又不能打断了呢」—— 同一台机器当天早些时候明明验过能插话，过了 40 分钟就插不进了，
而且**越试越插不进**。

## 一句话根因

`apex_barge.Monitor._consume()` 在「候选插话」分支里把 `_run_max`（他插话期间的峰值）用快攻写进了
她的基线 `_ref` —— **他的电平变成了「她的档」**，门槛跟着涨到他之上。

## 数字证据链（`/tmp/apex-bridge.log` + `curl :3210/state`）

| 时刻 | 她的档 ref | 他插话峰值 | 门槛 thr | 结果 |
|---|---|---|---|---|
| 23:10 | -23.9 dB | -14.1 dB | -25.4 | cue 生效：`voice 生效：speech=864ms`（差 9.8 dB，轻松） |
| 23:55（一轮长回答，19 行、播了 30+ 块、2 分钟） | **-15.2 dB**（被顶高） | -22.8 dB | **-16.7** | **cue 0 次**，整轮插不进去 |
| 修复前最后一次小结 | -21.7 dB | -20.5 dB | -23.2 | 峰值已低于基线 → 彻底锁死 |

对照行（同一晚）：
```
[barge] 回合小结: 她的档 -24.3 dB / 麦的峰值 -22.8 dB / 中位 -35.0 dB / cue 5 / 门槛 -25.8 dB / 误判收紧 +0.0
/state.barge: {'ref_db': -15.2, 'thr_db': -16.7, 'peak_db': -14.4, 'mid_db': -34.7, 'cues': 5, 'n': 600}
```
**她的真档 -24.3 dB，他正常插话 -22.8 dB（比真档高 1.5 dB，完全正常的插话）**；而 `/state` 同时刻
`ref_db -15.2` —— 中间 9 dB 就是被污染的量。`peak_db ≈ ref_db` 是「他已经插不进」的招牌。

## 代码成因（两处，缺一不可）

1. **候选期补基线（主因）**：
```python
else:                       # db <= thr_db
    if self._playing:
        if 0 < self._over < self._need_blocks:
            self._ref = _ref_step(self._ref, self._run_max, dt, self.release_db_s)  # ← 他的峰值进基线
        self._ref = _ref_step(self._ref, db, dt, self.release_db_s)
```
   初衷是「她自己的重音（短促抬起）事后补进基线」，但**她的播放是一块一块 TTS**：他插话说到一半
   就被块边界/她的句间停顿切成 1~12 块的碎片 → 碎片落进 `0 < over < need` → 他的电平被当成
   「她自己的重音」写进基线。
2. **块边界清零累积**：桥的 `_play_audio()` 每播**一块**就 `set_playing(True)` … `afplay` …
   `set_playing(False)`，而 `set_playing(True)` 里 `self._over = 0; self._armed_at = time.time()`
   → 他说到一半的话一到下一块起播就被清零，**永远攒不满 13 块 / 416 ms**（日志表现：「她在播」
   期间一次 cue 都没有）。

`_ref` **跨回合保留**（`arm()` 不重置它），坏值不会自己回来；只有慢放 1.5 dB/s 才降，而她一播就
没有足够长的静音块给它降 → 打断功能用一阵子就「自己坏掉」，且重启进程前不会自愈。

## 修法（已部署：自测 + 静默验收都过）

```
~/apex-src/apex_barge.py  备份 → apex_barge.py.bak-refpollution-<TS>
① _consume：候选期（0 < over < need_blocks）一律不喂基线，连 _run_max 也不补
② set_playing：块间宽限 self.gap_keep_s = APEX_BARGE_GAP_KEEP_S(默认 2.5s)
   —— 只有「距上次停播 > 2.5s」才算她重新开口，才清 over / 刷 _armed_at
③ arm()：_playing_off_at = 0.0（回合首次起播必定清零）
④ dump()：新增 over / over_ms / run_max_db —— 卡在哪一段一眼看出
```
部署：`python3 -m py_compile apex_barge.py && python3 apex_barge.py --selftest` →
`launchctl kickstart -k gui/$(id -u)/ai.hermes.apex-bridge`
（只改**代码**不必 `bootout`/`bootstrap`；`apex_barge.py` 是被桥 import 的模块，重启桥即重新加载）。

静默验收实测：
```
[barge] 回合小结: 她的档 -27.0 dB / 麦的峰值 -23.4 dB / 中位 -38.1 dB / cue 0 / 门槛 -28.5 dB / 误判收紧 +0.0
[ask] '只回四个字：语音测试通过。' -> 7 chars, spoke 1/1 lines (voice)
/state.barge: {'ref_db': -27.0, 'thr_db': -28.5, 'cues': 0, 'over': 0, 'run_max_db': -23.4, 'n': 77}
```
ref 重新学成干净的 -27.0（不再是污染的 -15.2），cue 0，无 `[打断]`。
**真人插话（正常音量）当天未复验** —— 这一步只能用户做，报告里要明写。

## 已否决的修法（别再试）

**给快攻加限速**（`_ref_step(..., attack_db_s=6.0)`，一块最多抬 `attack*dt`，想挡住单块瞬态）：
自测直接挂 —— `assert abs(det._ref - (-24.8)) < 1e-6` 只得到 **-35.4**。
基线爬不到「她那一档」，判据的地基（快攻跟峰值，见 SKILL.md 坑 2）就被破坏。
**快攻不能限速；病在「谁被允许进基线」，不在进入速度。**
半成品在 `~/Desktop/hermes/{patch,revert}_apex_barge_*.py`（revert 脚本已把它退回去）。

## 判定「是不是又退化了」：只看两个读数

- `barge.ref_db` 明显高于她正常回放的档（这台机器 ~-24 ~ -27 dB）→ **基线又被顶了**，别调 margin；
- `barge.peak_db ≈ ref_db` → 他的声音没进麦（时机/朝向/音量），也不是阈值问题。

## 未修的相邻问题（已定位，本次没动）

她在**块间隙**（`_playing=False`、但回合还没结束）时，`[listen]` 和 `[barge]` **会抢同一句话**：
正常轮把他前一句收走、耳朵把他补的那半句当插话 → 插话掐掉了正在跑的那一轮 → 那一轮变 **0 字**。
日志签名（2026-09-12 23:54）：
```
[listen] -> 16 chars: 纸飞机上面频道里面英文的频道要。
[barge] cue @23:54:53: level -28.5 / thr -29.6 / 她的档 -25.8 dB / +0 / 416 ms (她没播)
[barge] voice 生效：speech=864ms / 1.7s → '翻译过来的。'（这句当下一轮提问）
[ask] turn aborted by barge — closing the stream
[ask] '纸飞机上面频道里面英文的频道要。' -> 0 chars, spoke 0/0 lines (voice) [打断]
```
修的方向（**未实施、未验**）：块间隙由 `[listen]` 独占，耳朵在 `_playing=False` 期间只守不接管；
或插话生效时把 `[listen]` 已收走的那一轮**合并**进插话那句、而不是 abort 掉。
动手前先跟用户确认（他明确说先确认打断本身通了再说）。

## 数据速查

| 量 | 值 | 来源 |
|---|---|---|
| 她正常回放的档（这台机器） | ≈ -24 ~ -27 dB | 多次回合小结 |
| 被污染后的档 | -15.2 dB | `/state.barge.ref_db` |
| 他正常插话峰值 | ≈ -22.8 dB | 回合小结 peak |
| 触发线 | 13 块 × 32 ms ≈ 416 ms | `_need_blocks` |
| `margin`（该机 plist） | `APEX_BARGE_MARGIN_DB=-1.5` | plist EnvironmentVariables |
| TTS 音量 | `APEX_TTS_VOLUME=0.6` | 同上 |
