# STT 卡死 与「识别变差」归因

配套：`scripts/probe-stt-latency.py`、`scripts/verify-transcript-guards.py`。

## 一、Bounded timeout（否则整个对话看起来死了）

默认 `requests.post(..., timeout=120)` 无重试、无失败提示 → 这 120 秒页面既不说话也不报错，用户体感「卡死了」。

```python
STT_TIMEOUT = 8.0            # 正常 0.5s，8s 极宽裕
STT_ATTEMPTS = 3             # 8s × 3 ≈ 24s 封顶
STT_FAIL_LINE = "刚才那句我没听清，网络卡了一下，你再说一遍。"
```

**返回值语义必须分开**：`None` = 转写失败（网络）；`""` = 听到了但没可用内容。调用侧：
- 正常轮：`None` → 出声说 `STT_FAIL_LINE` 后继续听（**出声说明，别静默死等**）；`""` → 记为一次空转。
- 打断判定：`None` → **不清停**（判不了就不打断），日志写「转写失败（网络）→ 她继续说完」。

先证伪「provider 坏了」再动代码：`scripts/probe-stt-latency.py`（读 config 的 `stt.<provider>`，真语音打 3 次）。
全绿（<1s、http=200）= 偶发抖动，只修防御；全挂 = 先修配置/key/网络。

## 二、「识别变差」的三段归因（先做① ②再谈③）

**① 模型/参数侧 —— 排除**：同一段 `say` 音频换 5 种参数（`language` / `prompt` / `initial_prompt` 组合）
各打一次 + 现状参数连跑 3 次 → **输出一字不差**。结论：别在请求参数上找原因，杠杆不在那里。

**② 规则侧 —— 常见真凶**：后置语速上限把真人快句当「AI 编造」丢了。中文快语速本来就能到 9-10 字/s。
- 上限 `8.0 → 11.0`（桥内 `max(MAX_CHARS_PER_SPEECH_SECOND, 11.0)`；**别改 Hermes 本体**，会影响桌面端）
- **页面 mic 路径必须传音频总时长当分母下界**：只传检测到的语音时长时 `0.5*audio_ms` 这个下界从未生效，比服务端录音路径更容易误杀
- 回归用 `scripts/verify-transcript-guards.py`（真人快句 4 例必留 / 编造长句 3 例必杀）
- **别把上限整个关掉**：25 字/1.0s、410 字/1.0s 那种是模型在噪音上编的，必须继续拦

**③ 输入侧 —— 明说改不动**：远场 + 无 AEC（扬声器与麦同壳）+ 她说话时插话 + 语速快 → 错字。要 AEC 或近场麦。

## 三、常备诊断：把模型原始输出打出来

`[stt] <label> raw(N): ...` —— 下次用户说「这句识别错了」，对比 `raw` 与 `[transcribe] -> N chars`
就能一眼分清**识别错**（raw 本身就错 → 拾音问题）还是**被守卫吞了**（raw 正确、采用为 0 chars）。

| 日志行 | 含义 |
|---|---|
| `[listen] utterance: speech=Xms, audio=Ys, rms=Z` | 服务端录音路径收到一句话（rms 是含静音的平均，不是灵敏度） |
| `[transcribe] NNN bytes, spoken=Xms (page said Yms), peak=ZdB` | 页面 mic 路径的音频读数；**peak 就是音频质量读数** |
| `[stt] <label> 第 N/3 次失败` | 转写重试失败（网络/超时） |
| `[transcribe] dropped impossible rate` | 被语速上限丢（先怀疑误杀） |
| `[transcribe] dropped hallucination` | 模型在静音上编的（「嗯。」「啊。」等） |
| `[transcribe] dropped self-capture of own reply` | 麦里是她自己的回放 |

## 四、部署与验证次序

```bash
cp X.py X.py.bak-stt-$(date +%Y%m%d-%H%M%S)              # 备份
python3 -m py_compile X.py                                # 目标机语法检查 + 双端 sha256
launchctl kickstart -k gui/$(id -u)/<job>                  # 只改代码够；改 plist 要 bootout+bootstrap
```
验收：新进程起来的日志行 → 正常路径端到端（`say -v Tingting --data-format=LEI16@16000 -o /tmp/x.wav`）
→ **卡死路径**（把 `base_url` 指向黑洞 `http://10.255.255.1:9/v1`，期望 ~24s 返回 `None` + 三条重试日志）
→ `tail <err 日志>` 看有没有新 traceback（旧 traceback 会一直在，别当新故障）。

⚠️ `ffmpeg` 装在 `/usr/local/bin`（Homebrew），**SSH 非交互 PATH 里看不到**：在 ssh 里 `which ffmpeg`
会得出「没装」的错误结论。判据用 plist 的 PATH，或看日志里 `spoken=`/`peak=` 有没有真实读数。
