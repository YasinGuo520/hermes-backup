---
name: macos-backup-automation
description: "Set up automated backups of Hermes data (and other agent data) to an external drive on macOS. Covers the macOS permission quirk where /Volumes/<name> mount points can be root-owned, and the workaround using fallback strategies."
version: 1.1.0
author: Yasin's AI副驾驶
tags: [backup, macos, cron, automation, hermes, data-preservation]
---

# macOS Backup Automation

Automated daily backup of agent data (config, sessions, skills, workspace files, knowledge base) to an external drive.

## The macOS Permission Quirk

On some macOS configurations, external drive mount points under `/Volumes/<name>` can have `root:wheel` ownership with only `--x` permissions on the directory itself. This means:

- `ls /Volumes/<name>` → `Permission denied`
- `mkdir`, `cp`, `tar` → all fail
- `osascript` (`do shell script`) → also fails (still runs as the user)
- Finder (`duplicate` via AppleScript) → succeeds but can hang/timeout

**Detection test:**
```bash
ls /Volumes/macos1/ 2>/dev/null || echo "不可读或未挂载"
df -h | grep macos1  # 显示挂载点和容量 → 挂载了但不可写
diskutil list external  # 检查外部磁盘
```

## Backup Strategy

1. **Pack locally first** → `tar` + `cp` to `/tmp/hermes-backup-<date>/` (always works)
2. **Copy to external drive** → try direct `cp`
3. **Graceful skip** → if drive not mounted or unwritable, log and exit cleanly

## Setup

### 1. Create backup script

Place in `~/.hermes/scripts/hermes-backup.sh`. The script uses `df -h` to dynamically discover the mount path — this handles cases where the volume mounts with a different name due to stale directories in `/Volumes/`:

```bash
#!/bin/bash
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

# 打包
rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"
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
  find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
  find "$BACKUP_DIR" -name "*.db" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
  log "  ✓ 清理旧备份"
else
  log "  ❌ 写入失败（权限问题）"
  log "  📦 备份保留在 $TMP_DIR"
  exit 1
fi

rm -rf "$TMP_DIR"
FILE_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
DISK_USAGE=$(du -sh "$BACKUP_DIR" 2>/dev/null | awk '{print $1}')
log "✅ 完成 — $FILE_COUNT 个备份文件，占用 ${DISK_USAGE:-?}"
```

### 2. Register cron job

```bash
hermes cron create "0 3 * * *" --name "外置盘备份" --no-agent --script hermes-backup.sh
```

Or via cronjob tool:
```bash
# action=create, name=外置盘备份, schedule=0 3 * * *, script=hermes-backup.sh, no_agent=true
```

### 3. Data backed up

| Module | Source | Estimated size |
|--------|--------|----------------|
| Config + memory | `~/.hermes/config.yaml`, `.env` | ~10 KB |
| Skills | `~/.hermes/skills/` | ~100-500 KB |
| Session DB | `~/.hermes/state.db` | ~1-50 MB |
| Workspace | `~/Desktop/hermes/` | ~1-100 MB |
| Knowledge base | `~/Documents/Obsidian Vault/_kb/` | ~1-50 MB |

### 4. Retention

- 7-day rolling window — backups older than 7 days auto-deleted
- Log at `~/Desktop/hermes/backup-log.txt`

## Verification

Check backup log:
```bash
cat ~/Desktop/hermes/backup-log.txt
```

List backup files (when drive mounted):
```bash
DISK_PATH=$(df -h | grep macos1 | head -1 | awk '{print $NF}')
ls -lh "$DISK_PATH/hermes-backups/"
```

## Recovery

To restore from backup (use the script's dynamic path detection to find the actual mount):
```bash
DISK_PATH=$(df -h | grep macos1 | head -1 | awk '{print $NF}')
# Restore config
tar -xzf "$DISK_PATH/hermes-backups/hermes-config-<DATE>.tar.gz" -C ~/.hermes/
# Restore skills
tar -xzf "$DISK_PATH/hermes-backups/hermes-skills-<DATE>.tar.gz" -C ~/.hermes/
# Restore state.db
cp "$DISK_PATH/hermes-backups/hermes-state-<DATE>.db" ~/.hermes/state.db
```

## Related References

- **`references/macos-external-disk-troubleshooting.md`** — 分层排查指南：当外置盘物理插上但 `diskutil list` 完全看不到时的 5 层诊断流程 + 判断树 + 常见场景表。按「换线→换口→直插→换机验证→NVRAM重置」的排查路径。
- **`scripts/hermes-backup.sh`** — 实际运行的备份脚本，自动检测挂载点。

## Pitfalls

- **`diskutil info` fails** on root-only volumes — use `ls -la /Volumes/<name>/` and check exit code instead
- **osascript Finder operations can hang** — avoid in cron scripts; prefer `cp` fallback
- **Finder's disk list ≠ /Volumes/ directory** — a volume stub in /Volumes/ does not mean Finder can see it
- **APFS snapshot volumes** (Preboot, VM, etc.) are not external drives — never backup to system volumes
- **Cron job runs even when drive disconnected** — the graceful skip is essential; test with the drive unplugged
- **Stale root-owned `/Volumes/<name>/` directory blocks correct mount** — if a disk is force-ejected, macOS leaves an empty root-owned `d--x--x--x` stub in `/Volumes/`. On reconnection, the volume mounts as `<name> 1` (with a space + "1"). The script must use dynamic path detection (`df -h` grep) rather than hardcoded paths.
- **`df -h` is more reliable than `ls` for mount detection** — `ls /Volumes/macos1/` can fail with `Permission denied` even when the disk IS mounted (root-owned `--x` directory). `df -h | grep macos1` checks actual filesystem mount state.
- **Backup activity can trigger force-eject on marginal USB bridges** — if a disk is on the edge of failing (intermittent USB bridge), the `cp`/`tar` I/O can cause macOS Disk Arbitration to forcefully unmount it. The script will then see "not mounted" on subsequent runs. Recovery: plug into Windows to re-initialize the drive, or run `sudo killall -STOP -c usbd; sleep 2; sudo killall -CONT -c usbd` to reset the USB bus without rebooting.
- **Never dismiss user-reported timing correlations** — if the user says "disk was working before your command, then it ejected", the script log may show "skipped" because by the time the check runs, the disk is already gone. The script's own check after failure cannot capture what happened before. Always trust the user's sequence and help them recover rather than arguing causality.
- **"一插就发烫" ≠ bridge board burned out** — when macOS USB controller/NVRAM state is corrupted, the device can enter an abnormal powered state that generates heat. Plugging into Windows re-initializes the USB device and it works fine. The real fix is NVRAM reset on the Mac, not replacing the enclosure. Always cross-validate on Windows first before concluding hardware failure.
