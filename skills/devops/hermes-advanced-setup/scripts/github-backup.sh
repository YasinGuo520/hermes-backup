#!/bin/bash
# Daily GitHub backup for Hermes config - zero LLM token usage
# Uses SSH (more reliable from China than HTTPS)
set -e

source "${HOME}/.hermes/.env" 2>/dev/null || true
GITHUB_TOKEN="${GITHUB_TOKEN}"

REPO_URL="git@github.com:<USER>/<REPO>.git"
BACKUP_DIR="/tmp/hermes-github-backup"
HERMES_HOME="${HOME}/.hermes"
TIMESTAMP=$(date -u +%Y-%m-%d)

rm -rf "${BACKUP_DIR}"
git clone --depth 1 "${REPO_URL}" "${BACKUP_DIR}" 2>/dev/null
cd "${BACKUP_DIR}"

# Copy config files
cp "${HERMES_HOME}/config.yaml" "$BACKUP_DIR/" 2>/dev/null
cp "${HERMES_HOME}/SOUL.md" "$BACKUP_DIR/" 2>/dev/null
# rsync with .git exclusion handles nested git repos in skills/
rsync -a --delete --exclude='.git' "${HERMES_HOME}/memories/" "$BACKUP_DIR/memories/" 2>/dev/null || true
rsync -a --delete --exclude='.git' "${HERMES_HOME}/skills/" "$BACKUP_DIR/skills/" 2>/dev/null || true
rsync -a --delete --exclude='.git' "${HERMES_HOME}/cron/" "$BACKUP_DIR/cron/" 2>/dev/null || true

# Use --porcelain to detect untracked files (git diff misses them)
if git status --porcelain | grep -q .; then
    git add -A
    git commit -m "daily backup ${TIMESTAMP}" --quiet
    git push origin main 2>/dev/null || git push origin master 2>/dev/null
    echo "Backed up: $(find . -type f -not -path '*/.git/*' | wc -l) files to GitHub (${TIMESTAMP})"
else
    echo "No changes since last backup. Skipping."
fi

cd /tmp && rm -rf "${BACKUP_DIR}"
