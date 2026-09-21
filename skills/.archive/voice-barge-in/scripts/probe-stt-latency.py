#!/usr/bin/env python3
"""STT 探针：证明「转写慢/卡」是 provider 抖动还是配置坏了。

读 ~/.hermes/config.yaml 的 stt.<provider>（bridge 用的就是这一段），合成一段音频打 N 次，
打印每次的耗时/状态/文本。正常应当 <1s、http=200：
  · 全绿  → 故障是偶发抖动，只修「有界超时 + 重试 + 出声提示」这套防御；
  · 全挂  → 配置/key/网络问题，先修那个。

用法（Mac 上用 Hermes venv 的 python，它才有 yaml/requests）：
  ~/.hermes/hermes-agent/venv/bin/python probe-stt-latency.py [provider] [次数]
  provider 缺省取 config.yaml 的 stt.provider。
"""
import os
import random
import struct
import subprocess
import sys
import tempfile
import time

import requests
import yaml

CFG = os.path.expanduser("~/.hermes/config.yaml")
RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 3


def load_cfg(provider=None):
    cfg = yaml.safe_load(open(CFG, encoding="utf-8")) or {}
    stt = cfg.get("stt") or {}
    name = provider or stt.get("provider") or "openai"
    sec = stt.get(name) or {}
    return name, (sec.get("base_url") or "").rstrip("/"), sec.get("model") or "", sec.get("api_key") or ""


def synth(text="小贺，帮我查一下今天的抖音热点。"):
    """真语音优先（macOS say，最接近线上音频）；没有 say 就退回噪音 WAV 只测延迟。"""
    path = os.path.join(tempfile.gettempdir(), "probe_stt.wav")
    try:
        subprocess.run(["say", "-v", "Tingting", "--data-format=LEI16@16000", "-o", path, text],
                       check=True, capture_output=True)
        return open(path, "rb").read(), "say 真语音"
    except Exception:
        sr, n = 16000, 16000 * 3
        frames = b"".join(struct.pack("<h", int(1500 * random.uniform(-1, 1))) for _ in range(n))
        hdr = (b"RIFF" + struct.pack("<I", 36 + len(frames)) + b"WAVEfmt "
               + struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16)
               + b"data" + struct.pack("<I", len(frames)))
        return hdr + frames, "合成噪音（无 say）"


def main():
    name, base, model, key = load_cfg(sys.argv[1] if len(sys.argv) > 1 else None)
    print("provider=%s model=%s base=%s key_set=%s" % (name, model, base, bool(key)))
    if not base or not key:
        print("配置不完整：config.yaml 的 stt.<provider> 缺 base_url/api_key")
        return 1
    audio, how = synth()
    print("音频: %s, %d bytes" % (how, len(audio)))
    worst = 0.0
    for i in range(RUNS):
        t = time.time()
        try:
            r = requests.post(base + "/audio/transcriptions",
                              headers={"Authorization": "Bearer " + key},
                              files={"file": ("audio.wav", audio, "audio/wav")},
                              data={"model": model}, timeout=120)
            el = time.time() - t
            worst = max(worst, el)
            try:
                text = (r.json().get("text") or "")[:60]
            except Exception:
                text = "<非JSON>" + r.text[:60]
            print("  #%d %.2fs http=%s -> %r" % (i + 1, el, r.status_code, text))
        except Exception as exc:
            worst = max(worst, time.time() - t)
            print("  #%d %.2fs EXC %s" % (i + 1, time.time() - t, exc))
    print("最慢 %.2fs" % worst)
    print("判定:", "PASS 探针全绿（故障是偶发抖动，修防御即可）" if worst < 5 else
          "FAIL 探针本身慢/挂 —— 先修配置/网络/key")
    return 0


if __name__ == "__main__":
    sys.exit(main())
