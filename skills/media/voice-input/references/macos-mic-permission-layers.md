# macOS microphone permission layers — diagnosing "she can't hear me"

Case: 2026-09-12, Yasin's Mac (Tailscale `100.80.117.5`). A self-built kiosk voice UI (Next.js
page + local Python bridge + clap-wake detector + edge-tts/afplay) reported "speech produces no
output / she ignores me". The browser-side voice path was the broken half.

## The two permission layers people conflate

| Layer | When denied | Where it shows up |
|---|---|---|
| **Chrome/site permission** | `getUserMedia` throws `NotAllowedError` | page can report "no mic permission" |
| **macOS TCC** (per-app; System Settings → Privacy & Security → Microphone) | **no error at all** — the capture track goes live and delivers silence | page looks "connected", audio is empty |

`--use-fake-ui-for-media-stream` (kiosk Chrome flag) auto-accepts the *Chrome* layer only. It does
nothing for TCC — which is how a kiosk page ends up recording pure silence without an error.
TCC grants cannot be written from a plain SSH shell; the reliable fix is not to depend on them
(see below), or ask the user for the one click.

## Evidence chain (repeat in this order)

1. **Service log, per upload**: identical byte size every time (`257252 bytes`), then `speech=0ms`
   from the service's own ffmpeg measurement.
2. **Decode and measure the blob yourself**:
   ```bash
   ffmpeg -v error -y -i upload.webm -ac 1 -ar 16000 -f wav out.wav
   ffmpeg -v info -i out.wav -af silencedetect=noise=-40dB:d=0.15,volumedetect -f null - 2>&1 \
     | grep -E 'silence_duration|max_volume'
   ```
   A near-0 dBFS peak *together with* 0 s of non-silence = digital silence, i.e. a dead capture
   track — not a quiet room and not "the user did not speak".
3. **Same mic, other process, same minute**: the Python clap detector logged real onsets
   (`flux 55-500`, `db -25..-33`) while the page saw silence. Decisive: hardware and OS input
   level are fine; the capture consumer lacks the grant.
4. **The successes came from the CLI, not the page**: successful transcripts were
   `99794 bytes/1003ms` and `109454 bytes/3994ms` — WAV-scale payloads (16 kHz mono ≈ 32 kB/s),
   i.e. command-line tests somebody had run, while every page upload was a fixed-size blob.
5. **Cross-check inside the page** (only if a CDP-capable Chrome instance exists): run the
   `getUserMedia` + RMS probe on the live page. `rmsPeak ≈ 0` while Python hears the room = TCC
   layer confirmed. Probe: `scripts/probe-live-page.py` in the `agent-performance` skill.
   A Chrome whose `/json/version` returns **404 with an empty body** is not a usable CDP endpoint —
   launch your own instance for the probe instead of concluding "CDP is broken".

## Fix applied (architecture, not a patch)

Capture moved out of the browser into the service that already held the grant:

```python
# 16 kHz mono, 512-frame blocks (32 ms) — same profile as the wake-word detector
REC_SR, REC_BLOCK = 16000, 512
UTTERANCE_MAX_S, UTTERANCE_TRIM_S, UTTERANCE_OPEN_S = 15.0, 1.1, 7.0
SPEECH_MIN_MS = 200

with sd.InputStream(samplerate=REC_SR, blocksize=REC_BLOCK, channels=1, dtype="float32") as stream:
    while True:
        block, _ = stream.read(REC_BLOCK)
        x = block[:, 0]
        rms = float(np.sqrt(np.mean(x * x)))
        floor = rms if floor is None else min(floor, rms)      # opening-frames noise floor
        thresh = min(0.035, max(0.008, floor * 2.5))            # relative, not a constant
        # stop: 1.1 s after last voice / 7 s with no voice at all / 15 s hard cap
```

WAV bytes with the stdlib (`wave` + numpy int16) — `soundfile` was not installed and is not
needed. Then a shared `_guard_transcript()` → STT provider → streaming sentence-by-sentence TTS
with a single speaker. The UI keeps only start/stop + rendering.

Self-verified by speaking through the Mac's own speakers (`say -v Tingting`):

```
[listen] utterance: speech=4768ms, audio=8.1s, rms=0.0386
[listen] -> 23 chars: 你好，这是一次语音链路测试，请用一句话回答我。
[speak] playing 27648 bytes via zh-CN-XiaoyiNeural
[ask] ... -> 20 chars, spoke 1/1 lines (voice)
```

## Related lessons from the same job

- **Typed asks must be spoken too unless told otherwise.** Yasin: 「页面左侧的输出输入框也要实时
  播报才行哦」 and 「我也可以在那里输入指令，我就不用开桌面端 Hermes 了」 — the panel is a control
  surface, so route typed turns through the same streaming-speak path (a `TEXT_STYLE` system
  prompt), and keep a `{"speak": false}` escape hatch for text-only callers. Verified by giving the
  panel a task with a visible side effect (it wrote a file): 10.6 s, spoken answer.
- **Never let two speakers own a turn.** Double audio in a voice UI is almost always
  backend-TTS + page-`speechSynthesis` (or two overlapping turns). Pick one owner.
- **Wake detectors and recorders fight over the mic.** Both may open the input at once, but the
  wake engine will happily treat the user's own speech as a trigger; expose a mic-ownership flag
  and have it stand down.
- **zh_CN voices**: macOS `say -v Tingting` is the usable one (`say -v '?' | grep zh_CN` to list;
  Eddy/Flo/Grandma are novelty voices).
