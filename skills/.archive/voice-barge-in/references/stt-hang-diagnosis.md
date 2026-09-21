# APEX 语音链路：STT 卡死 与「识别变差」归因（2026-09-12 夜，全部实测）

桥：`~/apex-src/apex-hermes-bridge.py`（launchd `ai.hermes.apex-bridge`，:3210）
日志：`/tmp/apex-bridge.log`（stdout）/ `/tmp/apex-bridge.err`（stderr，append，旧 traceback 会一直在，
别拿它当新故障证据）。

---

## 现象一：对话几轮后「卡死不会回话」

### 日志签名（两条就能定性，不用读源码）
```
[listen] utterance: speech=544ms, audio=2.9s, rms=0.0564
[listen] stt failed: HTTPSConnectionPool(host='api.siliconflow.cn', port=443): Read timed out. (read timeout=120)
[listen] conversation ended (double-clap)
```
- `stt failed` 后面紧跟 `conversation ended (double-clap)` = 用户在静默期自己双击拍手结束了会话。
- 成因：`_transcribe_utterance` 里 `requests.post(..., timeout=120)`，**无重试、无失败提示** →
  这 120 秒页面既不说话也不报错 = 用户体感「死了」。
- 频率判据：`grep -c "stt failed" /tmp/apex-bridge.log` → 本次 = **1**（偶发抖动）。
  配置/网络坏掉会是一堆，别混为一谈。

### 先证伪「provider 坏了」再动代码
```bash
scp scripts/probe-stt-latency.py mac@<host>:/tmp/ && \
ssh mac@<host> '~/.hermes/hermes-agent/venv/bin/python /tmp/probe-stt-latency.py'
```
本次结果：3/3 次 **0.42-0.52s, http=200**（对照：事故当时 120s 无响应）→ 网络与 key 都正常，
要修的是**防御**，不是配置。

### 修法（两条路共用同一个 POST）
```python
STT_TIMEOUT = 8.0            # 正常 0.5s，8s 极宽裕
STT_ATTEMPTS = 3             # 8s × 3 ≈ 24s 封顶（旧：120s 静默）
STT_FAIL_LINE = "刚才那句我没听清，网络卡了一下，你再说一遍。"

def _stt_post(cfg, files, label):   # 返回原文；全失败 → None
    ...

def _transcribe_utterance(wav, speech_ms):
    # 返回值语义必须分开：None = 转写失败（网络）  "" = 听到了但没可用内容
```
调用侧：
- `_conversation`：`None` → `_speak_aloud(STT_FAIL_LINE)` 后继续听（**出声说明，别静默**）；
  `""` → 照旧记为一次空转。
- `_judge_barge`：`None` → **不清停**（判不了就不打断），日志写「转写失败（网络）→ 她继续说完」。
- `/transcribe`（页面 mic 路径）也走 `_stt_post`，失败回 502（页面自己会处理）。

### 验收（两种，都要做）
1. **正常路径**：`say -v Tingting --data-format=LEI16@16000 -o /tmp/x.wav "小贺，帮我查一下今天的抖音热点。"`
   → base64 塞进 `POST /transcribe {data_url, mime_type, speech_ms}` → 本次 1.19-1.25s，`text` 一字不差。
2. **卡死路径**：把 cfg 的 `base_url` 换成黑洞 `http://10.255.255.1:9/v1`（SYN 无应答）
   → 本次 **24.8s** 返回 `None` + 三条「第 N/3 次失败」日志（旧代码 120s 才会醒）。
   用法：`importlib.util.spec_from_file_location` 加载桥模块，直接调 `_stt_post`（模块级无副作用，
   `serve_forever()` 在 `__main__` 里）。

---

## 现象二：「我说完她显示的文字有些不太对 / 没之前那么准」是不是错觉

### 三段归因法（可复用，先做①②再谈③）

**① 模型/参数侧 —— 排除**
同一段 `say` 生成的音频，5 个参数变体各打一次：
仅 `model` / `+language=zh` / `+prompt=热词` / `+initial_prompt=热词` / 两者 → **输出完全一致**；
再用现状参数连跑 3 次 → **一字不差**。
结论：硅基 `Qwen/Qwen3-ASR-1.7B` **忽略 language/prompt/initial_prompt**，在干净音频上稳定且全对。
→ **别在请求参数上找「识别变差」的原因，杠杆不在那里**；也别把「模型升/降级」当第一假设。
（对比：`~/.hermes/config.yaml` 的 `stt.local` 段有 `initial_prompt` 热词，`stt.openai` 段没有——
这条差异**不影响**结果，已实测。）

**② 规则侧 —— 真凶（后置守卫把真人快句当「AI 编造」丢了）**
```
[transcribe] dropped impossible rate: 29 chars / 3008ms = 9.6 chars/s > 8.0 — invented
[transcribe] dropped impossible rate: 32 chars / 3296ms = 9.7 chars/s > 8.0 — invented
[transcribe] dropped impossible rate: 23 chars / 2768ms = 8.3 chars/s > 8.0 — invented
```
统计（`grep -c "dropped impossible rate"`）：**13 条/天被丢，其中 6-8 条是真人快说的正常句**
（中文快语速本来就能到 9-10 字/s）。分母是 RMS 检测到的语音时长，轻声/专名不过门限就少算。
两层修：
- 上限 `8.0 → 11.0`（桥内 `max(MAX_CHARS_PER_SPEECH_SECOND, 11.0)`；这个值是从 Hermes
  `tools.voice_mode` 借来的，**别去改 Hermes 本体**，那会影响桌面端）；
- **页面路径从前只传 `gate_ms`，没传音频时长** → `0.5*audio_ms` 这个分母下界**从来没生效**，
  比服务端录音路径更容易误杀。`_speech_stats` 现在多返回 `total`（ffmpeg 的 Duration），
  `_handle_transcribe` 组装 `clip_ms` 传进 `_guard_transcript(text, gate_ms, audio_ms=clip_ms)`。
回归：`scripts/verify-transcript-guards.py`（真人快句 4 例必留 / 编造长句 3 例必杀 → 7/7 PASS）。
**别把上限整个关掉**：25 字/1.0s、410 字/1.0s 那种是模型在噪音上编的，必须继续拦。

**③ 输入侧 —— 剩下的物理限制（明说改不动）**
拾音本身：远场（MacBook 内置麦）、无 AEC（扬声器与麦同壳）、她说话时插话、语速快 →
`X`→「叉」、`X 和 IG`→「XIG」这类错。模型侧无解，要 AEC 或近场麦。
`[transcribe] NNN bytes, spoken=Xms (page said Yms), peak=ZdB` 里 **peak** 就是音频质量读数，
远场/小声会明显偏低。

### 结论话术（用户问「是不是我的错觉」时）
一句判定 + 数字 + 修了什么 + 还剩什么，别用「我再查查」收尾：
> 不是错觉，但不是模型变差。同一段音频换 5 种参数跑 3 次一字不差（模型侧排除）；
> 真凶是后置规则：今天 13 条被当「编造」丢掉，其中 6-8 条是你正常语速说的。已把上限 8→11
> 字/秒、页面路径补上音频时长。剩下改不动的是拾音本身。

### 常备诊断（一行代码，建议长期开着）
每条转写在 `_stt_post` 里打印模型原始输出：
```
[stt] page raw(16): 小贺，帮我查一下今天的抖音热点。
```
下次用户说「这句识别错了」，对比 `raw` 和 `[transcribe] -> N chars` 就能一眼分清
**识别错**（raw 本身就错 → 拾音问题）还是**被守卫吞了**（raw 正确、采用为 0 chars）。

---

## 日志判读速查

| 日志行 | 含义 |
|---|---|
| `[listen] utterance: speech=Xms, audio=Ys, rms=Z` | 服务端录音路径收到一句话（rms 是整段含静音的平均，不是灵敏度指标） |
| `[transcribe] NNN bytes, spoken=Xms (page said Yms), peak=ZdB, mime=...` | 页面 mic 路径的音频读数 |
| `[stt] <label> raw(N): ...` | 模型原始输出（诊断用） |
| `[stt] <label> 第 N/3 次失败` | 转写重试失败（网络/超时） |
| `[transcribe] dropped impossible rate ...` | 被语速上限丢（先怀疑误杀） |
| `[transcribe] dropped hallucination` | 模型在静音上编的（「嗯。」「啊。」等） |
| `[transcribe] dropped self-capture of own reply` | 麦里是**她自己的回放**（`is_tts_echo`） |
| `[listen] conversation ended (double-clap)` | 用户双击拍手结束（卡死时就是这样收场的） |
| `[ask] '...' -> N chars, spoke k/n lines (voice)` | 一轮问答完成；带 `[打断]` 表示被插话 |

## 部署与验证次序（本次用的三步）
```bash
# 1. 备份 + 本地改（本地副本改好，patch 工具做精确替换）
ssh mac@<host> "cp ~/apex-src/apex-hermes-bridge.py ~/apex-src/apex-hermes-bridge.py.bak-stt-$(date +%Y%m%d-%H%M%S)"
# 2. 传回 + 双端 sha256 对比 + 目标机语法检查
scp apex-hermes-bridge.py mac@<host>:/Users/mac/apex-src/
ssh mac@<host> 'shasum -a 256 ~/apex-src/apex-hermes-bridge.py; ~/.hermes/hermes-agent/venv/bin/python -m py_compile ~/apex-src/apex-hermes-bridge.py'
# 3. 只改代码 → kickstart 够；改 plist 才要 bootout + bootstrap
ssh mac@<host> 'launchctl kickstart -k gui/$(id -u)/ai.hermes.apex-bridge; sleep 3; lsof -nP -iTCP:3210 -sTCP:LISTEN'
```
- 验收顺序：`grep "APEX⇄Hermes bridge on" <日志> | tail -1`（新进程起来了）→ 正常路径端到端
  → 卡死路径黑洞测试 → `tail /tmp/apex-bridge.err` 看有没有**新** traceback。
- ⚠️ `_speech_stats` 依赖 `ffmpeg`，它在 `/usr/local/bin`（Homebrew），**SSH 非交互 PATH 里看不到**：
  用 `which ffmpeg` 在 ssh 里判「没装」会得出错误结论（曾差点误判）。判据用 plist 的 PATH
  （`PATH=/Users/mac/.hermes/hermes-agent/venv/bin:/usr/local/bin:... command -v ffmpeg`）或直接看
  日志里 `spoken=`/`peak=` 是否有真实读数。
