---
name: server-migration
description: |
  Migrate a user's complete Hermes setup (project files, cron jobs, Obsidian vault,
  scripts) from one machine (e.g. local Mac) to another (e.g. cloud server).
  End-to-end: audit → transfer files → recreate cron jobs with adjusted paths →
  set up knowledge base → verify.
version: 1.0.0
---

# Server Migration Skill

Use when the user asks to "move everything to the server", "migrate my setup",
"搬服务器", or "迁移到云端".  Covers the full workflow of relocating a Hermes
user's working environment from one machine to another.

## The Canonical Workflow

### Phase 1: Audit the target server

Run these checks to understand the current state:

```bash
# 1. System info
hostname && df -h / && cat ~/.hermes/config.yaml

# 2. Skills inventory
hermes skills list | head -5   # just confirm 100+ skills are loaded

# 3. Gateway state
cat ~/.hermes/gateway_state.json   # which platforms are connected

# 4. Existing files
find ~/ -maxdepth 2 -name "*.py" -not -path "*/.hermes/hermes-agent/*" 2>/dev/null
ls ~/projects/ 2>/dev/null || echo "no projects dir"
```

### Phase 2: Get the source machine's data

Ask the user what they need migrated. Common items:

| Item | How to get |
|------|-----------|
| `.py` / `.md` project files | User uploads or sends GitHub link |
| `jobs.json` (cron config) | User runs: `cat ~/.hermes/cron/jobs.json` |
| Cron job scripts (if any) | User uploads the referenced `.py` / `.sh` files |
| Obsidian vault | User zips and uploads folder |
| Other assets | User uploads or provides source URL |

### Phase 3: Migrate files

Save all user files to `~/projects/` organized by purpose:

```
~/projects/
├── douyin_scraper.py       # business tools
├── viral_copywriter.py
├── daiky_stock_brief.py    # quant scripts (with updated paths)
├── quant_self_evolve.py
├── SOUL.md                 # config/prompts
└── ...                     # add more as needed
```

**⚠️ Path adjustment**: Scripts from macOS often contain hardcoded paths like
`~/Desktop/hermes/` or `/Users/mac/Desktop/hermes/`. These MUST be updated to
`~/projects/` on the Linux server before the scripts will work. Use `patch`
to replace path strings:

```
~/Desktop/hermes/ → ~/projects/
/Users/mac/Desktop/hermes/ → ~/projects/
```

### Phase 4: Recreate cron jobs

Parse the source `jobs.json` to extract each job's config. There are 3 job types:

**Type A — Prompt-only jobs** (pure text prompt, no script):
```
cronjob action=create name="..." prompt="<exact prompt>" schedule="..." deliver="..."
```

**Type B — Script-runner jobs** (prompt tells agent to run a .py script):
```
cronjob action=create name="..." prompt="运行 ~/projects/xxx.py 脚本，直接返回脚本输出。" schedule="..." deliver="..."
```

**Type C — no-agent script jobs** (script runs directly, no agent loop):
```
cronjob action=create name="..." schedule="..." script="hermes-backup.sh" no_agent=true deliver="..."
```

Key fields to extract from `jobs.json`:
- `name` — job name
- `prompt` — the prompt text
- `schedule.expr` — cron expression (e.g. `"0 8 * * *"`)
- `script` — script path (for Type C)
- `no_agent` — boolean
- `enabled_toolsets` — e.g. `["web", "terminal"]`
- `repeat.times` — repeat count (null = forever)
- `origin.platform` / `origin.chat_id` — delivery target

**Skip Mac-only jobs**: backup scripts, local-only tools, macOS-specific tasks.

### Phase 5: Set up Obsidian vault (if applicable)

```bash
# 1. Unzip to ~/obsidian-vault/
unzip ~/obsidian-vault.zip -d ~/obsidian-vault/

# 2. Create symlink from default Obsidian path
mkdir -p ~/Documents
ln -s /home/ubuntu/obsidian-vault/Obsidian\ Vault /home/ubuntu/Documents/Obsidian\ Vault

# 3. Verify
ls ~/Documents/Obsidian\ Vault/
```

The Obsidian skill looks for `OBSIDIAN_VAULT_PATH` env var or defaults to
`~/Documents/Obsidian Vault`. The symlink approach avoids editing protected
`.env` files.

### Phase 6: Final verification

1. List all cron jobs: `hermes cron list`
2. Verify next run times are correct
3. Test-script syntax: `python3 -m py_compile ~/projects/*.py`
4. Test Obsidian reads: `read_file ~/obsidian-vault/Obsidian\\ Vault/_kb/index.md`

### Phase 7: Performance tuning — trim skill load ⚠️ REQUIRED

**Users almost always notice the server feels slower than their local Mac.**
The #1 cause is **all 139+ skills loaded into the system prompt**, consuming
context and slowing response time. The user will ask "why does it have to load
every skill?" or complain about slow/lost context — this is inevitable. **Do not
skip this step.** Fix by moving unused skills out of the active dir:

```bash
mkdir -p ~/.hermes/skills_disabled
cd ~/.hermes/skills
mv <unused-skill-dir> ~/.hermes/skills_disabled/
```

**Common candidates to disable on a headless Linux server:**
bfl-api, data-science, dogfood, drawio-skill, email, flux-best-practices,
github, mlops, research, smart-home, social-media (xurl), yuanbao,
quant-* (if scripts run directly rather than through skills)

**What to keep** — skills the user actively uses:
Video/audio ali creation, content generation, creative tools (image gen,
cover, xhs), finance, productivity (translate, markdown, OCR, Notion),
software development, note-taking (obsidian), media, hermes-agent, computer-use.

**Restore a disabled skill:** `mv ~/.hermes/skills_disabled/<name> ~/.hermes/skills/`

⚠️ Skill changes take effect after a **session restart** (`/reset`).
The gateway service does NOT need a restart.

## Cron 迁移专节（合并自 hermes-cron-migration）

当迁移重点是**定时任务**时（用户说「把本地的定时任务迁移上去」「换了机器」），补充细节：

**获取配置**：`cat ~/.hermes/cron/jobs.json` 最可靠（`hermes cron job view <id>` 某些版本不存在）。提取字段：id/name/prompt/schedule/deliver/origin/model_snapshot/repeat/script/no_agent/enabled_toolsets。

**迁移判断规则**：
- 备份/本地专属脚本（macOS 外置盘备份、hermes-backup.sh）→ 跳过
- 纯 prompt 任务（无 script 字段）→ 直接 `cronjob action=create` 重建
- 脚本任务（script 引用本地路径）→ 获取脚本 + 调整路径

**脚本任务要点**：
- 用户拖文件到聊天 → 文件存 `~/.hermes/cache/documents/`，需要 copy 到项目目录
- 路径调整表：`~/Desktop/hermes/xxx.json` → `~/projects/xxx.json`；`/Users/mac/Desktop/hermes/` → `~/projects/`；Mac 的 `/Volumes/` 映射到 Linux 路径
- **shebang 行**：macOS 默认 `/usr/bin/python3`，Linux 可能是 `/usr/bin/python3.11`，确保兼容
- **文件权限**：复制脚本后 `chmod +x`
- **repeat.times**：源任务有次数限制（如 30 次/600 次）要一致，`cronjob create` 用 `repeat` 参数设置
- **性能提示**：prompt 中注明脚本运行时间（「需要约45-60秒」），避免 agent 超时
- **`~` 在双引号内不展开**：cron prompt 里 `~/projects/xxx.py` 会被 Hermes 解析，但 terminal 命令要用完整路径 `/home/ubuntu/projects/`
- **delivery 重定向**：目标机器 chat_id 从 `gateway_state.json` 查；脚本依赖包（openpyxl/playwright/openai）先在目标机器安装

## Common Pitfalls

1. **Script paths from macOS** — scripts saved to `~/Desktop/hermes/` won't
   exist on Linux. Always `patch` to `~/projects/`.
2. **Protected .env file** — Cannot edit `.env` directly (blocked by Hermes
   security). Use symlinks or default paths instead.
3. **rm -rf blocked** — The terminal security system blocks `rm -rf`. If the
   user explicitly approves, run it. Otherwise leave small artifacts (__MACOSX
   etc.) — they don't affect functionality.
4. **Cron delivery** — The server's weixin/feishu chat IDs may differ from
   the source machine. Use the server's gateway_state.json to find correct IDs.
5. **Model performance difference** — The server may use a slower API provider.
   If user complains, switch provider or model in config.yaml.
6. **`~` doesn't expand in double quotes** — Use full paths (`/home/ubuntu/`)
   in shell commands, not `~/`.
7. **139+ skills cause slow responses** — **MANDATORY FIX**: User WILL complain
   the server feels slow. Immediately trim skills (Phase 7) after migration.
   Skill changes take effect on session restart (`/reset`).
8. **computer-use won't work for remote desktop control** — `computer-use`
   controls the **local machine's** desktop (Linux X11/wayland display). On a
   headless cloud server there is no display, so it CANNOT be used to remotely
   control the user's Mac. Alternative remote-control approaches:
   - **向日葵/Todesk/TeamViewer**: user installs, shares temp link
   - **SSH tunnel**: if Mac has public IP or frp/ngrok tunnel
   - **Local Hermes**: user switches to local Mac terminal for desktop tasks
   - **Script-and-send**: for剪映 editing, write the Python script and ask
     user to run it on their Mac
9. **GitHub downloads blocked from China** — Many GitHub release downloads
   time out on Chinese servers. Use a mirror:
   ```bash
   curl -fsSL --max-time 60 "https://gh-proxy.com/github.com/org/repo/releases/download/vX.Y.Z/file.tar.gz" -o /tmp/file.tar.gz
   ```
   Alternative mirrors: `ghproxy.com`, `mirror.ghproxy.com`. If all mirrors
   fail, try an older version via version-pin env vars the tool exposes.
10. **__MACOSX folder from zip** — macOS zips include a harmless `__MACOSX/`
    metadata folder. Deleting it (`rm -rf`) may trigger terminal security blocks
    even when user-approved. Leave it — it doesn't affect functionality.

## Verification Checklist

- [ ] All project files in `~/projects/`
- [ ] Paths updated for Linux (no macOS paths)
- [ ] All cron jobs created and scheduled
- [ ] Scripts pass `python3 -m py_compile`
- [ ] Obsidian vault readable (if migrated)
- [ ] Delivery channels match server's gateway config
