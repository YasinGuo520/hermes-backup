#!/bin/bash
# 微信断线检测 + 自动生成二维码 + 飞书通知
# 每30分钟由cron执行一次
# 注意：不能包含 gateway restart 命令（cronjob会拦截SIGTERM传播）
# 本脚本只负责检测和保存新凭证，gateway重启需手动

LOG_FILE="$HOME/.hermes/logs/gateway.log"
FLAG_FILE="/tmp/.wechat_qr_sent"
HERMES_HOME="$HOME/.hermes"
VENV_DIR="$HOME/projects/ai_cs_saas/venv"
FEISHU_TARGET="feishu:oc_61850e610adf5771e7ba779c955a061e"

# 检查Session expired
RECENT_EXPIRED=$(tail -20 "$LOG_FILE" 2>/dev/null | grep -c "Session expired")
LAST_MSG_TIME=$(tail -20 "$LOG_FILE" 2>/dev/null | grep "weixin.*inbound" | tail -1 | grep -oP '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || echo "")

if [ "$RECENT_EXPIRED" -gt 0 ]; then
    NOW=$(date +%s)
    if [ -f "$FLAG_FILE" ]; then
        LAST_SENT=$(cat "$FLAG_FILE")
        DIFF=$(( (NOW - LAST_SENT) / 60 ))
        [ "$DIFF" -lt 10 ] && exit 0  # 防重复
    fi

    cd "$VENV_DIR" && source bin/activate && timeout 30 python3 -c "
import asyncio, sys, json, os
sys.path.insert(0, '$HOME/.hermes/hermes-agent')
os.environ['HERMES_HOME'] = '$HERMES_HOME'
from gateway.platforms.weixin import qr_login
async def main():
    result = await qr_login('$HERMES_HOME', timeout_seconds=30)
    if result:
        with open('$HOME/.wechat_new_cred.json', 'w') as f:
            json.dump(result, f)
        print('SUCCESS')
    else:
        print('FAILED')
asyncio.run(main())
" 2>/dev/null

    if [ -f "$HOME/.wechat_new_cred.json" ]; then
        CRED=$(cat "$HOME/.wechat_new_cred.json")
        ACCOUNT_ID=$(echo "$CRED" | python3 -c "import sys,json; print(json.load(sys.stdin).get('account_id',''))" 2>/dev/null)
        TOKEN=$(echo "$CRED" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
        BASE_URL=$(echo "$CRED" | python3 -c "import sys,json; print(json.load(sys.stdin).get('base_url','https://ilinkai.weixin.qq.com'))" 2>/dev/null)
        USER_ID=$(echo "$CRED" | python3 -c "import sys,json; print(json.load(sys.stdin).get('user_id',''))" 2>/dev/null)

        if [ -n "$ACCOUNT_ID" ] && [ -n "$TOKEN" ]; then
            mkdir -p "$HERMES_HOME/weixin/accounts"
            cat > "$HERMES_HOME/weixin/accounts/${ACCOUNT_ID}@im.bot.json" << FEOF
{
  "token": "$TOKEN",
  "base_url": "$BASE_URL",
  "user_id": "$USER_ID",
  "saved_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
FEOF
            echo "$NOW" > "$FLAG_FILE"
            export PATH="$VENV_DIR/bin:$PATH"
            hermes send -t "$FEISHU_TARGET" "⚠️ 微信连接已断开，新凭证已保存。请在服务器上执行: systemctl --user restart hermes-gateway"
        fi
    fi
fi

# 超过2小时无消息报警
if [ -n "$LAST_MSG_TIME" ]; then
    LAST_TS=$(date -d "$LAST_MSG_TIME" +%s 2>/dev/null)
    NOW=$(date +%s)
    if [ -n "$LAST_TS" ]; then
        SILENT_MIN=$(( (NOW - LAST_TS) / 60 ))
        if [ "$SILENT_MIN" -gt 120 ]; then
            LAST_WARN=$(cat "$FLAG_FILE" 2>/dev/null || echo "0")
            if [ $((NOW - LAST_WARN)) -gt 3600 ]; then
                hermes send -t "$FEISHU_TARGET" "⚠️ 微信已超过${SILENT_MIN}分钟没有消息，请确认是否正常连接。"
                echo "$NOW" > "$FLAG_FILE"
            fi
        fi
    fi
fi
