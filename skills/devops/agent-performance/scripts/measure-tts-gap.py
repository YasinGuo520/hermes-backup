#!/usr/bin/env python3
"""Measure the pause between spoken sentences: per-sentence synthesis vs one request.

  ~/.hermes/hermes-agent/venv/bin/python measure-tts-gap.py

Synthesises the SAME three sentences twice with edge-tts and reports duration + leading/trailing
silence for each segment via ffmpeg, isolating the padding that per-sentence synthesis injects
at every sentence boundary. Use it to confirm the seam problem or re-verify a trim.

Baseline (2026-09-12, zh-CN-XiaoyiNeural): every segment carries ~0.185 s lead and a CONSTANT
~0.87 s trail regardless of text; 9.00 s as three requests vs 8.18 s in one -> ~0.4 s extra dead
air per seam. After trimming each segment to 80 ms lead / 260 ms trail: boundary silence
2.10 s -> 0.65 s. Details: references/local-voice-ui-seams-and-thresholds.md

Needs edge-tts (venv) + ffmpeg. On macOS Homebrew ffmpeg lives in /usr/local/bin, which is NOT
on a non-interactive SSH PATH: export PATH=/usr/local/bin:$PATH first.
"""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

VOICE = "zh-CN-XiaoyiNeural"
SENTENCES = ["第一句话在这里。", "第二句话稍微长一点，用来观察句子之间的空隙。", "第三句话收尾。"]


async def synth(text: str, path: Path) -> None:
    buf = bytearray()
    async for chunk in edge_tts.Communicate(text, VOICE).stream():
        if chunk.get("type") == "audio":
            buf.extend(chunk["data"])
    path.write_bytes(bytes(buf))


def probe(path: Path) -> dict:
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af",
                          "silencedetect=noise=-45dB:d=0.05", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    total = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))) if m else 0.0
    lead = 0.0
    m = re.search(r"silence_start: (-?[0-9.]+)", out)
    if m and float(m.group(1)) <= 0.02:
        m2 = re.search(r"silence_end: ([0-9.]+)", out)
        lead = float(m2.group(1)) if m2 else 0.0
    st = re.findall(r"silence_start: ([0-9.]+)", out)
    en = re.findall(r"silence_end: ([0-9.]+)", out)
    trail = total - float(st[-1]) if st and (len(st) > len(en) or float(st[-1]) < total) else 0.0
    return {"path": path.name, "total_s": round(total, 3), "lead_s": round(lead, 3),
            "trail_s": round(trail, 3)}


async def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    print("voice:", VOICE)
    per = []
    for i, s in enumerate(SENTENCES, 1):
        p = tmp / ("seg%d.mp3" % i)
        await synth(s, p)
        info = probe(p)
        per.append(info)
        print("SEPARATE", json.dumps(info, ensure_ascii=False))
    p = tmp / "one.mp3"
    await synth("".join(SENTENCES), p)
    one = probe(p)
    print("ONE SHOT", json.dumps(one, ensure_ascii=False))
    sep = sum(x["total_s"] for x in per)
    print("\nseparate %.3fs (%d segments) vs one %.3fs" % (sep, len(per), one["total_s"]))
    print("dead air from per-sentence synthesis: %.3fs across %d seams"
          % (max(0.0, sep - one["total_s"]), len(per) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
