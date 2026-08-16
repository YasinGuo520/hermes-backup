#!/bin/bash
# ~/.hermes/scripts/wechat_keepalive.sh
# 每25分钟执行一次，通过 getconfig 保活 + gateway 进程守护
# 与 wechat_watchdog.sh 互补：keepalive防断线，watchdog检测断线后报警

set -e

# === 第一部分：getconfig 保活（刷新session，阻止4小时过期）===
ACCOUNT_FILE=$(ls -t ~/.hermes/weixin/accounts/*.json 2>/dev/null | head -1)
if [ -n "$ACCOUNT_FILE" ]; then
    TOKEN=$(python3 -c "
import json
with open('$ACCOUNT_FILE') as f:
    acct = json.load(f)
    print(acct.get('token', ''))
" 2>/dev/null)
    if [ -n "$TOKEN" ]; then
        curl -s -X POST "https://ilinkai.weixin.qq.com/ilink/bot/getconfig" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $TOKEN" \
          -d '{}' > /dev/null 2>&1
    fi
fi

# === 第二部分：gateway 进程守护 ===
if ! systemctl --user is-active hermes-gateway.service > /dev/null 2>&1; then
    systemctl --user start hermes-gateway.service
    echo "[$(date)] Gateway was down, restarted" >> ~/.hermes/logs/keepalive.log
fi

echo "[$(date)] Keepalive done" >> ~/.hermes/logs/keepalive.log
