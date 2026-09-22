#!/bin/sh
# Antigravity (反重力) 2.x on macOS — agentapi 环境发现 + 零配额连通性探针
#
#   sh antigravity-env.sh            探针：自动找出可用的 gRPC 口并报告状态（不消耗配额）
#   eval "$(sh antigravity-env.sh --export)"   导出三件套供后续调用
#
# 前提：Antigravity.app 正在运行（agentapi 必须连活的 language_server）
set -u

export PATH="$HOME/.gemini/antigravity/bin:$PATH"
API="$HOME/.gemini/antigravity/bin/agentapi"

[ -x "$API" ] || { echo "ERROR: 找不到 $API" >&2; exit 1; }

LSPID=$(pgrep -f "language_server --standalone" 2>/dev/null | head -1)
[ -n "${LSPID:-}" ] || {
  echo "ERROR: language_server 未运行 —— 先启动 Antigravity.app（agentapi 不是独立二进制）" >&2
  exit 1
}

# CSRF 来自启动参数，每次启动随机，磁盘上没有 → 只能读进程 argv
CSRF=$(ps -p "$LSPID" -ww -o args= 2>/dev/null | tr ' ' '\n' | grep -A1 -- '--csrf_token' | tail -1)
[ -n "${CSRF:-}" ] || { echo "ERROR: 取不到 --csrf_token" >&2; exit 1; }

PROJ=$(basename "$(ls -1 "$HOME"/.gemini/config/projects/*.json 2>/dev/null | head -1)" .json)
[ -n "${PROJ:-}" ] || { echo "ERROR: 缺 ~/.gemini/config/projects/*.json" >&2; exit 1; }

# 候选端口：language_server 会监听多个口，只有一个能通 gRPC
PORTS=$(lsof -nP -iTCP -sTCP:LISTEN -a -p "$LSPID" 2>/dev/null \
        | sed -n 's/.*:\([0-9][0-9]*\) (LISTEN).*/\1/p')
[ -n "${PORTS:-}" ] || { echo "ERROR: 未找到 language_server 监听端口" >&2; exit 1; }

export ANTIGRAVITY_CSRF_TOKEN="$CSRF"
export ANTIGRAVITY_PROJECT_ID="$PROJ"

GOOD=""
STATUS=""
for P in $PORTS; do
  export ANTIGRAVITY_LS_ADDRESS="127.0.0.1:$P"
  OUT=$("$API" get-conversation-metadata probe-id 2>&1)
  case "$OUT" in
    *"trajectory not found"*)
      GOOD="$P"; STATUS="OK 全通"; break ;;
    *"project_id is required"*)
      GOOD="$P"; STATUS="OK 认证已过（探针缺 project 是预期的）"; break ;;
    *"missing CSRF token"*)
      STATUS="FAIL 端口 $P 对，但 CSRF 无效"; ;;
    *"connection reset"*|*"preface"*|*EOF*)
      STATUS="skip 端口 $P 不是 gRPC 口"; ;;
    *)
      STATUS="? 端口 $P 返回: $OUT" ;;
  esac
done

if [ -z "$GOOD" ]; then
  echo "FAILED — 候选端口: $PORTS" >&2
  echo "$STATUS" >&2
  exit 2
fi

export ANTIGRAVITY_LS_ADDRESS="127.0.0.1:$GOOD"

if [ "${1:-}" = "--export" ]; then
  printf 'export ANTIGRAVITY_LS_ADDRESS=%s\n' "$ANTIGRAVITY_LS_ADDRESS"
  printf 'export ANTIGRAVITY_CSRF_TOKEN=%s\n' "$ANTIGRAVITY_CSRF_TOKEN"
  printf 'export ANTIGRAVITY_PROJECT_ID=%s\n' "$ANTIGRAVITY_PROJECT_ID"
  exit 0
fi

printf '%s (addr=%s project=%s)\n' "$STATUS" "$ANTIGRAVITY_LS_ADDRESS" "$ANTIGRAVITY_PROJECT_ID"
