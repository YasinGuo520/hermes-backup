#!/bin/bash
# 无人在场时验「语音助手说话时能不能被打断」。
# 在跑着助手的那台机器上执行：bash inject-voice-barge-test.sh [注入音量，默认 3]
#
# 做什么：让助手开始念一段 → 6 s 后用系统 TTS 经音箱注入一句中文（= 用户插话）→ 打印本轮日志。
# 判读：cue → 判成真插话（写入待问队列）→ 这一轮被打断 → 插话那句接着走 → 新的一轮开始
# 注意：注入是「经音箱再进麦」，比真人对着麦说话弱得多；注入失败 ≠ 打断不好用，真人要单独验。
set -u
VOL="${1:-3}"
PY="${PY:-$HOME/.hermes/hermes-agent/venv/bin/python}"
BRIDGE="${BRIDGE:-http://127.0.0.1:3210}"
LOG="${LOG:-/tmp/apex-bridge.log}"
INJ=/tmp/barge-inject.mp3

"$PY" - "$INJ" <<'PYEOF'
import asyncio
import sys
import edge_tts

TEXT = "等一下，先别念了，我问你一个问题，你听我说完。"


async def main() -> None:
    comm = edge_tts.Communicate(TEXT, "zh-CN-XiaoyiNeural")
    with open(sys.argv[1], "wb") as fh:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])


asyncio.run(main())
PYEOF
ls -la "$INJ"
MARK=$(wc -l < "$LOG")

curl -s -m 240 -X POST -H 'Content-Type: application/json' \
  -d '{"prompt":"请你用三句话介绍一下你自己，说说你能帮我做哪些事。","voice":true}' \
  "$BRIDGE/ask" > /tmp/barge-ask.json 2>&1 &
sleep 6

echo "--- 助手应该在念了 ---"
curl -s -m 5 "$BRIDGE/state" | "$PY" -c \
  "import sys,json;b=json.load(sys.stdin).get('barge') or {};print({k:b.get(k) for k in ('enabled','cues','ref_db','thr_db','peak_db','penalty_db')})"

echo "--- 注入插话（afplay -v $VOL）---"
afplay -v "$VOL" "$INJ"
sleep 14

echo "--- 本轮新日志 ---"
tail -n +$((MARK + 1)) "$LOG" | grep -E "barge|ask\]|listen\]" || echo "（无新日志：助手可能没在播，或注入太弱）"
