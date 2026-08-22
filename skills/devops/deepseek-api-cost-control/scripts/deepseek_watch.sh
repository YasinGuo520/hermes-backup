#!/usr/bin/env bash
# DeepSeek pro 扣费观察检查 - 运行后对比余额基线，提醒用户查控制台
# 部署：cronjob no_agent=true 一次性，脚本放 ~/.hermes/scripts/deepseek_watch.sh
set -e
LOG=~/.hermes/logs/deepseek-watch.log
BASE=~/.hermes/state/deepseek_balance_baseline.txt

# 读取key（~/.hermes/.env 的 DEEPSEEK_API_KEY 才是真key，config.yaml 的 sk-gaw 是 SiliconFlow）
KEY=$(grep -oP 'DEEPSEEK_API_KEY=\K.*' ~/.hermes/.env 2>/dev/null | head -1)
if [ -z "$KEY" ]; then
    echo "❌ 找不到 DEEPSEEK_API_KEY，请手动检查"
    exit 1
fi

# 查询当前余额
NOW=$(curl -s --max-time 15 https://api.deepseek.com/user/balance -H "Authorization: Bearer $KEY" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    b = d.get('balance_infos', [{}])[0]
    print(b.get('total_balance', '?'))
except:
    print('查询失败')
" 2>/dev/null)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 当前余额: ¥$NOW" >> "$LOG"

# 对比基线
if [ -f "$BASE" ]; then
    OLD=$(cat "$BASE")
    echo "基线余额: ¥$OLD → 当前: ¥$NOW"
    echo "【观察提醒】请登录 DeepSeek 控制台 → 用量 → 模型维度，确认观察期内是否还有 deepseek-v4-pro 扣费。"
    echo "如果仍有 pro 扣费 → key 可能泄露，需要立即更换 API Key。"
    echo "如果没有 → 锁死生效，之前的 pro 是历史误切模型的记录。"
else
    echo "$NOW" > "$BASE"
    echo "已记录基线余额: ¥$NOW（首次运行）"
    echo "【观察提醒】观察期结束后请登录 DeepSeek 控制台，查看模型维度是否有 deepseek-v4-pro 扣费。"
fi
