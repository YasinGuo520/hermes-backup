#!/bin/bash
# 渠道投递体检（只读，不改任何状态、不重启任何服务）
# 用途：用户报「定时任务没发过来」时，30 秒分清「任务没跑」/「跑了没送到」/「通道此刻通不通」
# 用法：bash ~/.hermes/scripts/channel_delivery_probe.sh
set -uo pipefail
H="${HERMES_HOME:-$HOME/.hermes}"

# hermes CLI 常在 ~/.local/bin（非交互 SSH 下 PATH 里没有）
HERMES_BIN="$(command -v hermes 2>/dev/null || true)"
[ -z "$HERMES_BIN" ] && [ -x "$HOME/.local/bin/hermes" ] && HERMES_BIN="$HOME/.local/bin/hermes"

if [ -n "$HERMES_BIN" ]; then
  echo "=== 1. 可用投递目标（bare 平台名需有 home channel）==="
  "$HERMES_BIN" send --list 2>&1
else
  echo "=== 1. 可用投递目标：跳过（没找到 hermes CLI）==="
fi

echo
echo "=== 2. 近 3 天 cron 执行 + 投递结果 ==="
echo "    completed + 投递失败 = 内容已落盘、只是没送出去；claimed/running 才是任务本身没跑完"
python3 - "$H" <<'PY'
import sqlite3, os, sys
db = os.path.join(sys.argv[1], "cron", "executions.db")
if not os.path.exists(db):
    print(f"(找不到 {db})")
    raise SystemExit
c = sqlite3.connect(db)
cols = [r[1] for r in c.execute("PRAGMA table_info(executions)")]
has_delivery = "delivery_outcome" in cols
sel = "substr(claimed_at,1,19), job_id, status"
sel += ", coalesce(delivery_outcome,'-')" if has_delivery else ", '-'"
sel += ", substr(coalesce(error,''),1,60)"
rows = list(c.execute(
    f"SELECT {sel} FROM executions"
    " WHERE claimed_at >= datetime('now','-3 day')"
    " ORDER BY claimed_at DESC LIMIT 30"))
for r in rows:
    print(" | ".join(str(x) for x in r))
if not rows:
    print("(近 3 天无执行记录)")
if not has_delivery:
    print("(本版本 executions.db 无 delivery_outcome 列 → 投递结果看第 3/4 节日志)")
PY

echo
echo "=== 3. 投递成功记录（权威依据）==="
grep -hE "delivered to .* via live adapter|Cron output preserved" "$H"/logs/*.log 2>/dev/null | tail -12 || true

echo
echo "=== 4. 投递失败/通道异常告警 ==="
grep -hE "send failed|rejected send|prepare failed|No home channel|rate limited" "$H"/logs/*.log 2>/dev/null | tail -12 || true

echo
echo "=== 5. 每条任务的最新产出文件（内容没丢，可直接补发）==="
for d in "$H"/cron/output/*/; do
  [ -d "$d" ] || continue
  latest="$(ls -t "$d" 2>/dev/null | head -1)"
  [ -n "$latest" ] && printf '%s  %s\n' "$(basename "$d")" "$latest"
done

echo
echo "=== 6. 通道此刻通不通（下面两条会真发一条消息，按需手动跑）==="
echo "    微信: hermes send --to weixin --json \"通道自检\"     # 会话 token 制，需用户当天在微信说过话，隔夜必死"
echo "    TG  : hermes send --to telegram --json \"通道自检\"    # bot-token 制，无时效窗口"
