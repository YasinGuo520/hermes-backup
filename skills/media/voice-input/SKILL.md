---
name: voice-input
description: "Voice I/O + barge-in on macOS/Linux — transcribe audio (faster-whisper) and run the local real-time voice loop: 说话时能被打断/interrupt、VAD+语速守卫、麦克风归属、TTS 音量调参。"
tags: [whisper, stt, speech-to-text, transcription, voice, audio, macos, linux]
---

# Voice Input (Speech-to-Text) — macOS & Linux

Transcribe audio messages (voice memos, recordings) from the user into text using local offline tools on macOS.

## When to Use

- User sends a voice message on a chat platform (WeChat, Telegram, etc.)
- User has an audio file (recording, interview, meeting) they want transcribed
- User asks "can you listen to this audio?"
- You need to understand spoken content programmatically

## Requirements

- **faster-whisper** (`pip3.11 install faster-whisper`) — Intel Mac CPU backend
- **ffmpeg** — audio format conversion (install via `brew install ffmpeg`)
- **HF mirror** for Chinese users: `export HF_ENDPOINT=https://hf-mirror.com`
- Python must be Homebrew's version, not uv-managed, because faster-whisper's CTranslate2 binary wheels install to `/usr/local/lib/python3.11/site-packages/`

## Transcription Script

A ready-to-use script lives at `~/.hermes/scripts/transcribe.py`. Usage:

```
/usr/local/bin/python3.11 ~/.hermes/scripts/transcribe.py <audio_file> [--model tiny|base|small|medium|large-v3] [--language zh|en|...]
```

Output: prints transcription to stdout. Metadata (timestamps, language) goes to stderr.

### Script key options
| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `tiny` | Model size. tiny=fast, base=balanced, small/medium/large-v3=slower but more accurate |
| `--language` | auto-detect | Force a language (`zh`, `en`, `ja`, etc.) to improve accuracy |
| `--task` | `transcribe` | `transcribe`=original language, `translate`=output English |

## Setup (macOS)

```bash
# 1. Install faster-whisper with Homebrew's Python (NOT uv-managed python)
pip3.11 install faster-whisper

# 2. Pre-download model from HF mirror (required in China)
HF_ENDPOINT=https://hf-mirror.com /usr/local/bin/python3.11 -c "
from huggingface_hub import snapshot_download
snapshot_download('Systran/faster-whisper-tiny')
"

# 3. Verify
/usr/local/bin/python3.11 -c "
from faster_whisper import WhisperModel
model = WhisperModel('tiny', device='cpu', compute_type='int8')
print('OK')
"
```

## Setup (Linux / Ubuntu)

```bash
# 1. Install faster-whisper (use --break-system-packages on Debian/Ubuntu)
pip install faster-whisper --break-system-packages

# 2. Pre-download model from HF mirror (required in China)
export HF_ENDPOINT=https://hf-mirror.com
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('Systran/faster-whisper-tiny')
"

# 3. Verify
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('tiny', device='cpu', compute_type='int8')
print('OK')
"

# 4. ffmpeg (system package, no brew needed)
sudo apt-get install -y ffmpeg
```

**Platform differences from macOS:**
- Use system `python3` (no Homebrew Python needed)
- `pip install --break-system-packages` or use a venv
- model cache goes to `~/.cache/huggingface/hub/`
- First load ~3-5s on modern CPU (much faster than macOS Intel)

### Linux Transcribe Script

A Linux-compatible script lives at `scripts/transcribe_linux.py` under this skill directory. Usage:

```bash
python3 ~/.hermes/skills/media/voice-input/scripts/transcribe_linux.py <audio_file> [--model tiny] [--language zh]
```

## Workflow for transcribing user voice messages

1. Platform delivers audio as a file path or URL (WeChat sends `.aac`/`.mp3`/`.ogg`/`.silk` files)
2. If needed, convert to 16kHz mono WAV:
   ```bash
   ffmpeg -i input.aac -ar 16000 -ac 1 output.wav
   ```
3. Run transcription:
   - **macOS**: `/usr/local/bin/python3.11 ~/.hermes/scripts/transcribe.py output.wav --model tiny`
   - **Linux**: `python3 ~/.hermes/skills/media/voice-input/scripts/transcribe_linux.py output.wav --model tiny`
4. If accuracy is poor on Chinese audio, retry with `--language zh` and/or a larger model (`base` or `small`)
5. Use the transcribed text as input to respond to the user

## Live mic capture in an app (voice UI / push-to-talk / wake word)

This is a DIFFERENT problem class from "transcribe a file the user sent", and it has one rule
that decides the whole design:

> **On macOS, microphone access is granted per app, and the grant belongs to the process that
> asks for it. A process WITHOUT the grant gets no error — it gets DIGITAL SILENCE.**

So pick the capture layer by **which process already holds the grant**, not by which is easier
to write. Validated 2026-09-12 on a macOS kiosk voice UI: Chrome had no mic grant while the
Hermes venv python did (its clap detector heard the room perfectly) — every browser upload was
byte-identical digital silence, and ASR invented text from it.

### The signature of "capturing without a grant" (measure before touching code)

| Evidence | How to get it |
|---|---|
| every upload is the **same byte size** (e.g. byte-identical `257252`-byte blobs) | service log, one line per upload |
| ~0 dBFS peak **and** 0 s of speech | `ffmpeg -i x.webm -ac 1 -ar 16000 out.wav` then `ffmpeg -i out.wav -af silencedetect=noise=-40dB:d=0.15,volumedetect -f null -` |
| the SAME mic works for another process at that moment | 2 s `sounddevice`/`sox` level meter, or that process's log (here: clap onsets at `flux 55-500`, `db -25..-33`) |
| ASR answers with canned junk (`嗯。` `啊。`, subtitle lines, impossible chars/s) | provider response + guard log |

⚠️ "ASR keeps hallucinating" and "she never hears me" are usually **one** bug: nothing was
captured. Hallucination guards (blocklists, char-rate ceilings, TTS-echo checks) are worth
having, but they can never fix a silent capture path — the audio was never there.

### Fix pattern that worked (no OS permission dialog needed)

1. **Move capture into the process that holds the grant** (e.g. `sounddevice` in the already
   running service) and let the UI (browser/app) do nothing but POST start/stop and render state.
2. **One speaker only.** If both the backend and the page can speak, every reply plays twice —
   users say "双声音 / double voice" — and the second copy re-enters the mic.
3. **One shared guard pipeline**, extracted into a function every audio entry point calls. A
   guard fixed on one path silently leaves the other open (extract it as soon as there are two).
4. **VAD thresholds relative to the measured noise floor** (min RMS over the opening frames),
   never a fixed constant. End an utterance on ~1.1 s trailing silence; hard-cap it (~15 s).
5. **Say who owns the mic.** Expose `listening`/`mic_owned` in the state endpoint so the
   wake-word/clap detector stands down while the service records — otherwise speech re-triggers
   the wake mid-turn and the assistant answers its own recording.
6. **Verify with real audio, not intent**: play a known sentence through the speakers
   (`say -v Tingting "..."` on macOS) and check the service log reports non-zero speech_ms and
   the exact characters back. End-to-end proof you can run yourself.

If a browser path must stay, the user has to grant it in System Settings → Privacy & Security →
Microphone (a GUI step no shell can do). Note that `--use-fake-ui-for-media-stream` only
auto-accepts the *Chrome* layer — it does nothing for TCC, which is exactly how a kiosk page ends
up recording pure silence with no error.

Diagnostic recipe and the full kiosk case in `references/macos-mic-permission-layers.md`.

## Real-time voice loop：说话时能被打断（barge-in）

**触发**：「她在念的时候我插不进话」「非要等她念完才听我说」；或反过来——打断做了但**把助手自己掐哑了/反复被掐断**（那是坑 0 没做，见下）。判据对任何「边说边听」的本地回路（常驻进程录音 → STT → LLM → TTS 播放）都成立。

### 先查三处再下结论（别猜、别急着写代码）

| 查什么 | 命中即说明 | 修法 |
|---|---|---|
| `InputStream` 是否**只在录音函数里**开 | 她说话时麦克风是关的 → 用户插的话**一个字都没录到** | 说话期间常开一支耳朵（独立模块） |
| `/state` 的 `mic_owned` 是否把 `speaking` 也算进去 | 唤醒/拍手监听在**整个说话期间让位** | 说话期间改语义：由「唤醒」变「打断」 |
| 播放是不是阻塞调用（`subprocess.run`） | 阻塞到整句播完、手里**没有进程柄**，掐不掉 | 换 `Popen` + 30ms 轮询 + `terminate()` |

三层墙都在时，唯一的「打断」就是等她播完（单轮硬顶一两百秒）——先查清再动手，别靠反复试阈值碰运气。

### 判定必须两层证据

1. **快（音频域）**：块级 dB 相对「她那一档」抬高 ≥ margin 且持续 ≥ 420ms → 立刻掐（感受上像插话，容许偶发误判）
2. **准（文本域）**：掐完房间是静的（无回声）→ 从起话头那一帧取音频交 STT：空/她自己的回声 → **假警报，当前句重播**；有内容 → **直接当下一轮提问**（一个字不丢）

### 六条硬规则（全部实测定标）

0. **基线没学到就判定 → 她一个字都念不出来**（真实事故：一轮 21 次假 cue、反复被掐断）。起播头 1.2s **只学不判**；`ref is None` 必须走学习分支
1. **候选插话期间绝不能喂基线**（连瞬间峰值也不补）：否则他的声音把「她的档」顶上去，**门槛跟着涨，永远不触发**（详见 `references/barge-in-threshold-calibration.md`）
2. **基线不能用中位数/分位数**：她自己的语音在她的回放里，中位数与句子起头重音能差 13 dB。用**快攻慢放**（高了立刻跟、低了 ~1.5 dB/s 放）→ 基线停在「她最响那一档」
3. **判定链里的 STT 也要有有界超时**：卡住的不只是不能插话——**整个对话看起来死了**（8s × 3 次 + 出声提示）。完整配方见 `references/stt-hang-and-transcript-guards.md`
4. **拍手/唤醒检测器不能直接当打断键**（她说话时它本来就隔几秒一个 onset）→ 要重做必须先量「真人拍手 vs 她回放」的电平差；宁可只留「开口打断」
5. **可行门槛由回声决定，不由算法决定**：唯一有效杠杆是**降她的播放音量**（回声低 6 dB，门槛就低 6 dB）→ 所有阈值走环境变量；服务用 launchd 时 plist 的 `EnvironmentVariables` 就是调参面板

### 验收三档（分清验到了什么）

| 手段 | 能证明 | 不能证明 |
|---|---|---|
| 纯函数自测（喂合成电平序列） | 判据逻辑（她的重音不触发 / 他持续 416ms 触发 / 基线没被顶跑） | 麦克风路径、真实阈值 |
| **注入法**（`scripts/inject-voice-barge-test.sh`：用 edge-tts 生成不同文本 + `afplay -v N` 从音箱放出来） | 整条链：cue → 掉 → 摘录 → STT → 当下一轮提问 | 真人贴麦说话的电平 |
| 真人在场说一句 | 可行门槛是否真够 | ——（**必须做，别替用户下结论**） |

没人可插话时先跑 `scripts/barge-silent-acceptance.sh`（她起一轮，`cues == 0` 且无 `[打断]`）——
**只证明「起播不会被她自己判成插话」，证明不了「他插得进」**，报告里别混为一谈。

### 支持文件

- `references/barge-in-implementation.md` — 两条腿的挂点、旋钮取值与实测依据、日志签名、部署与回退
- `references/barge-in-threshold-calibration.md` — 基线污染定标（数字证据链 + 已否决修法 + 只看两个读数）
- `references/stt-hang-and-transcript-guards.md` — STT 有界超时、语速守卫误杀、三段归因、日志判读表
- `scripts/probe-stt-latency.py` / `scripts/verify-transcript-guards.py` / `scripts/barge-silent-acceptance.sh` / `scripts/inject-voice-barge-test.sh`

## Chinese Network Notes

- HuggingFace is blocked from mainland China. Always set `HF_ENDPOINT=https://hf-mirror.com` before downloading models.
- Use `snapshot_download()` (not `hf_hub_download`) to get all model files — downloading just `model.bin` is insufficient; faster-whisper also needs `tokenizer.json`, `vocabulary.txt`, `config.json`.

## Model Sizes & Performance (Intel Mac i7, CPU only)

| Model | Load Time | Use Case |
|-------|-----------|----------|
| `tiny` | ~77s | Quick voice messages, short clips |
| `base` | Untested | Good default |
| `small` | Untested | Noisy recordings |
| `medium` | Untested | Batch transcription |
| `large-v3` | Untested | Highest accuracy |

## Pitfalls

### macOS
- **Python version mismatch**: `pip3 install` (system Python 3.9) vs `pip3.11` (Homebrew) install to different site-packages. The script must use `/usr/local/bin/python3.11`.
- **Model download timeout**: HuggingFace direct downloads fail from China — use `HF_ENDPOINT=https://hf-mirror.com`.
- **First load is slow**: ~77s on Intel CPU. For repeated use, consider a background server that holds the model in memory.
- **ffmpeg missing**: Run `brew install ffmpeg` if needed.
- **No GPU**: Intel Iris Plus Graphics — `device="cpu"` only. Do not attempt GPU acceleration.
- **Silk format**: WeChat uses `.silk`. ffmpeg may not handle it directly. Try conversion or ask user to forward in another format.

### Linux (Ubuntu/Debian)
- **PEP 668 blocks pip**: Use `pip install --break-system-packages` or create a venv. Don't use `sudo pip`.
- **Model cache**: Stored in `~/.cache/huggingface/hub/`. Delete if model is corrupted.
- **First load faster**: ~3-5s on modern CPU. tiny model is sufficient for short clips.
- **edge-tts network**: MS Edge TTS servers are intermittently unreachable from Chinese servers. Retry 2-3 times, or use espeak-ng as fallback (install: `sudo apt-get install espeak-ng`).

## Related

- Script (macOS): `~/.hermes/scripts/transcribe.py`
- Script (Linux): `scripts/transcribe_linux.py` (in this skill directory)
- Reference: `references/voice-interaction-setup.md` — full voice interaction setup notes (TTS pipeline, robotic voice effects with ffmpeg, platform quirks)
- Barge-in / 实时回路: `references/barge-in-implementation.md`、`references/barge-in-threshold-calibration.md`、`references/stt-hang-and-transcript-guards.md`
- 探针与验收脚本: `scripts/probe-stt-latency.py`、`scripts/verify-transcript-guards.py`、`scripts/barge-silent-acceptance.sh`、`scripts/inject-voice-barge-test.sh`
