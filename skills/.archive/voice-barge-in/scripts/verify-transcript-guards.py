#!/usr/bin/env python3
"""回归：语速上限守卫「真人快句必留 / 编造长句必杀」。

数字取自 2026-09-12 的真实日志（apex-bridge.log），用来防止把上限调得过紧
（误杀真人快语速 → 用户感觉「我说了她没接上」）或过松（放进模型在噪音上编的长句）。

用法（Mac 上，任何能 import 桥的 python 都行）：
  ~/.hermes/hermes-agent/venv/bin/python verify-transcript-guards.py [桥路径]
退出码 0 = 全 PASS；1 = 有 FAIL（含具体哪条）。
"""
import importlib.util
import os
import sys

BRIDGE = (sys.argv[1] if len(sys.argv) > 1
          else os.path.expanduser("~/apex-src/apex-hermes-bridge.py"))

spec = importlib.util.spec_from_file_location("apexbridge", BRIDGE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)          # 模块级无副作用：serve_forever() 在 __main__ 里
print("bridge:", BRIDGE)
print("cap   :", m.MAX_CHARS_PER_SPEECH_SECOND, "(应 >= 11.0，Hermes 默认 8.0 会误杀真话)")

BASE = "帮我查一下今天抖音罗盘的前三热点数据情况怎么样"       # 23 字
CASES = [
    # (说明, 字数, gate_ms=检测到的语音时长, 音频总时长ms, 期望保留)
    ("真·23字/2768ms (音频6s)", 23, 2768, 6000, True),
    ("真·29字/3008ms (音频7s)", 29, 3008, 7000, True),
    ("真·32字/3296ms (音频7s)", 32, 3296, 7000, True),
    ("真·12字/1000ms (页面路径原来无分母兜底)", 12, 1000, 1200, True),
    ("编·25字/996ms", 25, 996, 2500, False),
    ("编·41字/1000ms", 41, 1000, 2000, False),
    ("编·410字/1000ms (噪音编造)", 410, 1000, 2000, False),
]

bad = 0
for name, n, gate, audio, want in CASES:
    text = (BASE * 20)[:n]
    kept = m._guard_transcript(text, gate, audio_ms=audio) != ""
    if kept != want:
        bad += 1
    print("%-42s 保留=%-5s 期望=%-5s %s" % (name, kept, want,
                                             "PASS" if kept == want else "FAIL"))
print("\n总判定:", "PASS" if not bad else "FAIL (%d 条)" % bad)
sys.exit(0 if not bad else 1)
