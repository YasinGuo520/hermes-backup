#!/bin/bash
# Hermes 定时大脑清理脚本 — 每周跑一次，保持系统清爽
# 归入 server-service-deployment skill
set -e

LOG="/tmp/hermes-cleanup-$(date +%Y%m%d-%H%M).log"
exec > "$LOG" 2>&1

echo "=== 开始清理 $(date) ==="
disk_before=$(df / | tail -1 | awk '{print $3}')

# 1. UV 缓存
if [ -x ~/.hermes/bin/uv ]; then
  ~/.hermes/bin/uv cache clean 2>&1
fi

# 2. Pip 缓存
pip cache purge 2>&1

# 3. Electron/node-gyp (无用缓存)
rm -rf ~/.cache/electron ~/.cache/node-gyp 2>/dev/null

# 4. __pycache__ + .pyc 垃圾
find /home/ubuntu -maxdepth 6 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /home/ubuntu -maxdepth 6 -name "*.pyc" -delete 2>/dev/null || true

# 5. /tmp 清理（保留最近24小时文件）
find /tmp -type f -atime +1 -delete 2>/dev/null || true

# 6. Hermes 日志 — 只保留最近2个
ls -t ~/.hermes/logs/agent.log.* 2>/dev/null | tail -n +3 | xargs rm -f 2>/dev/null || true
ls -t ~/.hermes/logs/errors.log.* 2>/dev/null | tail -n +3 | xargs rm -f 2>/dev/null || true
ls -t ~/.hermes/logs/gateway.log.* 2>/dev/null | tail -n +3 | xargs rm -f 2>/dev/null || true

# 7. apt 缓存
sudo apt clean 2>&1

# 8. journal 日志 — 只保留200MB
sudo journalctl --vacuum-size=200M 2>&1

# 9. /var/log 过期日志（7天以上）
sudo find /var/log -type f \( -name "*.gz" -o -name "*.old" -o -name "*.1" -o -name "*.2" \) -mtime +7 -delete 2>/dev/null || true

# 10. 系统页缓存释放
sudo sh -c 'sync && echo 3 > /proc/sys/vm/drop_caches' 2>&1

# 11. 看看剩多少
disk_after=$(df / | tail -1 | awk '{print $3}')
disk_freed=$(( (disk_before - disk_after) / 1024 ))
cache_now=$(du -sh ~/.cache/ 2>/dev/null | awk '{print $1}')

echo "=== 清理完成 ==="
echo "释放磁盘: ${disk_freed}MB"
echo "缓存剩余: ${cache_now}"
echo "磁盘剩余: $(df -h / | tail -1 | awk '{print $4}')"
echo "内存可用: $(free -h | grep Mem | awk '{print $7}')"
