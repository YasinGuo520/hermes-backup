# China Network Setup for faster-whisper

## HuggingFace Mirror

All model downloads must use hf-mirror.com:

```bash
export HF_ENDPOINT=https://hf-mirror.com
# Then any HF operation uses the mirror
```

Or inline per command:

```bash
HF_ENDPOINT=https://hf-mirror.com python3.11 -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-tiny')"
```

## Why snapshot_download?

`hf_hub_download(model.bin)` only downloads `model.bin` (~150MB for tiny), but faster-whisper also requires:
- `tokenizer.json`
- `vocabulary.txt`
- `config.json`
- `.gitattributes` (optional)
- `README.md` (optional)

Use `snapshot_download()` to get all 6 files at once. Do NOT chain individual `hf_hub_download()` calls — it's slower and error-prone.

## Python Path Quirk

This Mac has two Python 3.11 installations:
| Location | Source | site-packages |
|----------|--------|---------------|
| `/usr/local/bin/python3.11` | Homebrew | `/usr/local/lib/python3.11/site-packages` |
| `~/.local/bin/python3.11` | uv-managed | `~/.local/share/uv/python/.../site-packages` |

`pip3.11` maps to Homebrew's pip. Packages installed with `pip3.11` end up in `/usr/local/lib/python3.11/site-packages` and are accessible only by `/usr/local/bin/python3.11`.

**Always use `/usr/local/bin/python3.11` for faster-whisper.** The uv-managed `python3.11` does not see the installed package.
