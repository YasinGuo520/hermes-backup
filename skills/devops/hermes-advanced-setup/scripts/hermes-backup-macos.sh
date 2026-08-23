#!/bin/bash
# Hermes 自动备份脚本 — 每天运行，保留最近7天
# 自动检测外置盘挂载点（兼容卷名冲突，如 macos1 vs macos1 1）
# 外置盘未挂载时自动跳过，不出错

DATE=$(date +%Y%m%d)
RETENTION_DAYS=7
LOG="$HOME/Desktop/hermes/backup-log.txt"
TMP_DIR="/tmp/hermes-backup-$DATE"

log() { echo "$(date '+%H:%M') $*" >> "$LOG"; }

log "=== 备份 $DATE ==="
log "检查外置盘..."

# 自动检测挂载点：df -h 中找到包含 "macos1" 的卷
DISK_PATH=$(df -h 2>/dev/null | grep "macos1" | head -1 | awk '{print $NF}')
if [ -z "$DISK_PATH" ]; then
  log "⚠️  外置盘未挂载（df 未检测到 macos1 卷），跳过"
  exit 0
fi

BACKUP_DIR="$DISK_PATH/hermes-backups"

# 二次验证：目标目录可写
if ! mkdir -p "$BACKUP_DIR" 2>/dev/null; then
  log "⚠️  外置盘 $DISK_PATH 目标目录不可写，跳过"
  exit 0
fi

log "  ✓ 检测到: $DISK_PATH"

# 备份到本地临时目录
log "打包中..."
rm -rf "$TMP_DIR" 2>/dev/null && mkdir -p "$TMP_DIR"

tar -czf "$TMP_DIR/hermes-config-$DATE.tar.gz" \
  -C "$HOME/.hermes" config.yaml .env 2>/dev/null && log "  ✓ 配置"

tar -czf "$TMP_DIR/hermes-skills-$DATE.tar.gz" \
  -C "$HOME/.hermes" skills/ 2>/dev/null && log "  ✓ Skills"

[ -f "$HOME/.hermes/state.db" ] && cp "$HOME/.hermes/state.db" \
  "$TMP_DIR/hermes-state-$DATE.db" && log "  ✓ 会话"

tar -czf "$TMP_DIR/hermes-workspace-$DATE.tar.gz" \
  -C "$HOME/Desktop" hermes/ 2>/dev/null && log "  ✓ 工作产出"

tar -czf "$TMP_DIR/hermes-kb-$DATE.tar.gz" \
  -C "$HOME/Documents" "Obsidian Vault/_kb/" 2>/dev/null && log "  ✓ 知识库"

# 写入外置盘
log "写入外置盘..."
if cp -f "$TMP_DIR/"* "$BACKUP_DIR/" 2>/dev/null; then
  log "  ✓ 拷贝完成"
  # 清理旧备份（保留7天）
  find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
  find "$BACKUP_DIR" -name "*.db" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
  log "  ✓ 清理旧备份"
else
  log "  ❌ 写入失败（权限问题）"
  log "  📦 备份保留在 $TMP_DIR"
  log "  手动执行: sudo cp -r $TMP_DIR/* $BACKUP_DIR/"
  exit 1
fi

# 清理临时文件
rm -rf "$TMP_DIR" 2>/dev/null

FILE_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
DISK_USAGE=$(du -sh "$BACKUP_DIR" 2>/dev/null | awk '{print $1}')
log "✅ 完成 — $FILE_COUNT 个备份文件，占用 ${DISK_USAGE:-?}"
log ""
