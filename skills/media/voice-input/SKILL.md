---
name: voice-input
description: Process voice/audio input from the user — transcribe speech to text using local tools (faster-whisper) on macOS and Linux. Covers setup, model management, platform quirks, and automated transcription pipelines for both platforms.
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
