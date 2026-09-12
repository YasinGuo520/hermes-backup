#!/usr/bin/env bash
# 静默验收：不用人说话，让桥自己起一轮短的，确认「起播不会被她自己判成插话」。
#
# 用法: bash barge-silent-acceptance.sh [bridge_url]        (默认 http://127.0.0.1:3210)
#       APEX_BRIDGE_LOG=/tmp/apex-bridge.log  APEX_ACCEPT_PROMPT='只回四个字。'
#       桥若配了 key: 额外导出 APEX_TOKEN=xxx
#
# 判读（三条全中才算过）:
#   ① /state.barge.cues == 0        ② 本轮有 [barge] 回合小结 且 cue 0
#   ③ 本轮没有 [打断]，也没有「耳朵起不来」
# 不能证明: 他插得进 —— 那要真人在场或注入法（见 SKILL.md 验收表）。
set -uo pipefail

BRIDGE="${1:-http://127.0.0.1:3210}"
LOG="${APEX_BRIDGE_LOG:-/tmp/apex-bridge.log}"
PROMPT="${APEX_ACCEPT_PROMPT:-只回四个字：语音测试通过。}"
PY="$(command -v python3)"

HDR=()
[ -n "${APEX_TOKEN:-}" ] && HDR=(-H "X-Token: ${APEX_TOKEN}")

MARK=$(wc -l < "$LOG" 2>/dev/null || echo 0)
echo "== bridge=$BRIDGE  log=$LOG  mark=$MARK"

BODY=$("$PY" -c 'import json,sys; print(json.dumps({"prompt": sys.argv[1]}))' "$PROMPT")
curl -s --max-time 120 -X POST "${HDR[@]}" "$BRIDGE/ask" \
  -H 'Content-Type: application/json' --data-binary "$BODY" | head -c 300
 echo

echo "== 本轮日志 =="
tail -n +$((MARK + 1)) "$LOG" | grep -E '\[barge\]|\[ask\]|\[speak\]|打断|耳朵起不来' | tail -20

echo "== /state.barge =="
curl -s --max-time 5 "$BRIDGE/state" \
  | "$PY" -c 'import sys,json; print(json.load(sys.stdin).get("barge"))'

echo
echo "判定: cues 必须 0 / 小结行 cue 0 / 无 [打断] / 无「耳朵起不来」"
