#!/bin/bash
# Hermes Agent Mac 诊断脚本
# 跑法：bash mac-hermes-diagnostic.sh
# 输出全部复制贴回给服务器助手分析

echo "=== 1. 系统 ==="
sw_vers 2>/dev/null
echo "Arch: $(uname -m)"

echo ""
echo "=== 2. Hermes 进程 ==="
echo "主进程:"
ps aux | grep "Hermes.app" | grep -v grep | head -5
echo ""
echo "CLI/网关进程:"
ps aux | grep "hermes_cli" | grep -v grep | head -5

echo ""
echo "=== 3. 配置 ==="
echo "config.yaml 大小: $(wc -c < ~/.hermes/config.yaml 2>/dev/null || echo 'N/A')"
echo "SOUL.md 前10行:"
head -10 ~/.hermes/SOUL.md 2>/dev/null || echo "no SOUL.md"

echo ""
echo "=== 4. Python 环境 ==="
which python3 2>/dev/null && python3 --version
ls ~/.hermes/venv*/bin/python 2>/dev/null || echo "no venv"

echo ""
echo "=== 5. 端口监听（微信/网关）==="
lsof -iTCP -sTCP:LISTEN -P 2>/dev/null | grep -v "rapportd\|ControlCe" | head -15

echo ""
echo "=== 6. 磁盘 ==="
df -h / | tail -1

echo ""
echo "=== 7. 网络连通 ==="
curl -so /dev/null -w "github: %{http_code} (%{time_total}s)\n" https://github.com --connect-timeout 5
curl -so /dev/null -w "feishu: %{http_code} (%{time_total}s)\n" https://www.feishu.cn --connect-timeout 5

echo ""
echo "=== 8. Tailscale（如有）==="
which tailscale 2>/dev/null && tailscale status 2>/dev/null || echo "no tailscale"

echo ""
echo "=== DONE ==="
