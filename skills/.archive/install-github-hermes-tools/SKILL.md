---
name: install-github-hermes-tools
description: Install third-party tools from GitHub that ship with their own Hermes skills and plugins (e.g. quant-trade, community projects). Covers cloning, venv setup, symlink integration, and verification.
tags: [github, skills, plugins, setup, integration]
related_skills: [find-skills, skill-creator]
---

# Install Third-Party GitHub Hermes Tools

When a user finds a GitHub project that extends Hermes with its own skills (`skills/` dir) and plugins (`plugins/` dir), use this skill to install and integrate it properly.

## Trigger Conditions

Use this skill when:
- User found a GitHub repo that contains `skills/` and/or `plugins/` directories under a Hermes-agent-compatible project
- User wants to install a third-party quant/automation/utility tool that isn't on the official skill registry
- A community project's README mentions Hermes Agent integration but doesn't provide a `hermes skills install` command

## Installation Steps

### 1. Clone the Repository (preferred)

```bash
cd ~/Desktop  # or a suitable workspace directory
git clone https://github.com/<user>/<repo>.git
```

**China mirror fallback** (when direct GitHub clone times out):
```bash
# Try these mirrors in order:
git clone https://gitclone.com/github.com/<user>/<repo>.git
git clone https://ghproxy.net/https://github.com/<user>/<repo>.git
```

**jsDelivr CDN fallback** (when even mirrors fail — pull individual files instead of full clone):
```bash
# Use jsDelivr CDN to fetch individual raw files (fast in China)
BASE="https://cdn.jsdelivr.net/gh/<user>/<repo>@main"

# Pull SKILL.md files from skills/ subdirectories
curl -sL "$BASE/skills/<skill-name>/SKILL.md" -o ~/.hermes/skills/<skill-name>/SKILL.md

# Pull additional scripts/files
curl -sL "$BASE/skills/<skill-name>/scripts/<script>.mjs" -o ~/.hermes/skills/<skill-name>/scripts/<script>.mjs

# Verify
hermes skills list | grep <skill-name>
```
This avoids the full Git clone entirely — jsDelivr CDN is hosted on Chinese mainland CDN nodes and doesn't suffer from GFW throttling.

### 2. Set Up Python Virtual Environment

Most projects require Python >= 3.12. Prefer the user's Python 3.13:

```bash
cd ~/Desktop/<repo>
# Find the right Python
which python3.13  # Homebrew, prefer this
/usr/local/bin/python3.13 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For China users, pip may need extra time — set timeout accordingly (300s).

### 4. Link Skills to Hermes

If the repo has a `skills/` directory with individual skill subdirectories:

```bash
cd ~/Desktop/<repo>
for skill in skills/*/; do
    name=$(basename "$skill")
    ln -sfn "$(pwd)/skills/$name" ~/.hermes/skills/<prefix>-$name
done
```

Use a unique prefix (e.g. `quant-`) to avoid name collisions with existing skills.

### 5. Link Plugins to Hermes

If the repo has a `plugins/` directory:

```bash
cd ~/Desktop/<repo>
ln -sfn "$(pwd)/plugins/<plugin_name>" ~/.hermes/plugins/<plugin_name>
```

### 6. Verify Installation

Test that the core tools import cleanly:

```bash
cd ~/Desktop/<repo>
source venv/bin/activate
python -c "
import sys; sys.path.insert(0, '.')
from plugins.<plugin_name> import *
print('✅ Import OK')
"
```

Then test with a live data call (if applicable) to confirm real functionality.

### 7. Handle Environment Variables

- Check if the project needs a `.env` file
- If API keys are needed, inherit from the user's existing Hermes config where possible (e.g. `OPENAI_API_KEY` for LLM features)
- For optional features (exchange API keys, notification channels), note these as configurable but not required for basic operation

### 8. Install Official Companion Skills

Some projects complement official Hermes skills. Install companion skills non-interactively:

```bash
yes | hermes skills install official/finance/stocks
```

## Pitfalls & Troubleshooting

- **PEP 668 protection** - System Python (brew) prevents `pip install` outside venv. Always use a venv.
- **Python version mismatch** - Check the project's `python_requires` in `pyproject.toml` or `requirements.txt`. Fall back to 3.13 if 3.12+ required.
- **AKShare / Yahoo Finance API drift** - AKS省e 和 yfinance 等免费数据源的API可能变更，导致特定函数失效。验证时先测基础功能（stock_quote等），再看高级功能（估值、研报）。
- **Symlink vs copy** - Use `ln -sfn` (soft link) so updates to the git repo automatically reflect in Hermes. The original project may have gitignored these paths otherwise.
- **GitHub connectivity in China** - If direct clone fails, try `gitclone.com` or `ghproxy.net` mirrors with extended timeout (120s+). For individual files, jsDelivr CDN (`cdn.jsdelivr.net`) is more reliable — no full clone needed.
- **`npx skills add` fails on nested SKILL.md** - `npx skills add <owner>/<repo>` reports "No valid skills found" if SKILL.md is under `skills/<name>/` subdirectory (skills CLI only checks repo root). Use `hermes skills tap add` + manual install, or use jsDelivr CDN to pull files directly.
- **`yes | hermes skills install`** — The install command prompts for confirmation interactively. Pipe through `yes` for non-interactive automation.
- **Memory limit** — Add install record to memory for future reference, but keep it compact (project path, venv path, key features enabled).

## MCP Server Installation

Some tools (like AnySearch for Agent search) are MCP servers, not traditional skills/plugins. They expose tools via the Model Context Protocol.

### Streamable HTTP MCP Servers (Recommended)

For MCP servers that support native Streamable HTTP transport (MCP spec 2025-03-26+):

#### 1. Upgrade the MCP package first

```bash
pip install --upgrade mcp
```

> **Watch out**: Upgrading `mcp` may bump `starlette` to an incompatible version (e.g. 1.x) if `sse-starlette` is also pulled in. If you see `fastapi` dependency errors, pin starlette back:
> ```bash
> pip install "starlette>=0.40.0,<0.42.0"
> ```

#### 2. Add the MCP server

```bash
# Interactive method (use for manual setup)
hermes mcp add <name> --url <mcp_endpoint_url>

# Non-interactive method (for automated setup in scripts/cron)
echo -e "n\n\nY" | hermes mcp add <name> --url <mcp_endpoint_url>
```
The `echo -e "n\n\nY"` answers three prompts in order:
- `n` — "Does this server require authentication?" (anonymous access)
- (empty) — "API key / Bearer token:" (skip)
- `Y` — "Enable all tools?" (auto-enable)

#### 3. Verify

```bash
hermes mcp list
# Expected: <name>  https://<url>...  all  ✓ enabled
```

#### 4. Use the tools

Run `/reset` in session or start a new session. The MCP server's tools appear as first-class Hermes tools.

### When to Use Which Method

| Integration type | Method | Example |
|---|---|---|
| Hermes skill (`skills/` dir) | `ln -sfn` symlink | `install-github-hermes-tools` |
| Hermes plugin (`plugins/` dir) | `ln -sfn` symlink | Custom automation plugins |
| MCP server (HTTP/S) | `hermes mcp add --url` | AnySearch, n8n, etc. |
| MCP server (stdio) | `hermes mcp add --command` | Local node/python MCP servers |

### Finding MCP Servers

Hermes has a built-in catalog:
```bash
hermes mcp catalog           # List Nous-approved MCPs
hermes mcp install <name>    # One-click install from catalog
```

For community MCPs not in the catalog:
1. Search GitHub: `curl -s "https://api.github.com/search/repositories?q=<toolname>+mcp+server&sort=stars"`
2. GitHub API is more reliable than web search in restricted networks

### Pitfalls & Troubleshooting

- **`mcp.client.streamable_http is not available`** — The `mcp` Python package is too old. Run `pip install --upgrade mcp` to get Streamable HTTP support.
- **`hermes mcp add` hangs on prompts** — The command is interactive by default. For automation, pipe answers via `echo -e "n\n\nY"` as shown above.
- **API key not needed?** — Some MCP servers (like AnySearch) support anonymous access with lower rate limits. Answer `n` to the auth prompt for anonymous mode.
- **Tool not showing after install** — MCP server tools are loaded at session start. Run `/reset` or start a new session (`/reload-mcp` should work for MCP-only changes).

### Post-Install: Configure Search Tool Priority

When the installed MCP server **provides search tools** (e.g. AnySearch), the agent gains a **second parallel search path** alongside the built-in `web_search` (from the `web` toolset). The agent cannot choose between them without explicit configuration.

**Required step**: Save a memory entry declaring search priority:

```
搜索优先级：先走AnySearch（MCP，4个工具：search/batch_search/extract/get_sub_domains），AnySearch无结果再走回web_search（web工具集）。
```

Adapt the tool names to match the installed MCP server.

**Why this matters**: Without explicit priority:
- The agent may use `web_search` (which may lack API keys) and silently return nothing
- Context is wasted re-deciding which tool to use each turn
- The agent defaults to the wrong/slower/more expensive path

**Checklist after MCP search install:**
- [ ] `hermes mcp list` — confirm server connected with tools enabled
- [ ] `hermes mcp test <name>` — verify connectivity and latency
- [ ] `grep -E "EXA_API_KEY|TAVILY_API_KEY|BRAVE_SEARCH_API_KEY" ~/.hermes/.env` — check if web_search fallback has credentials (missing keys = silent failure)
- [ ] Add memory entry setting search priority

## Reference

For official skill installations, use `hermes skills install official/<category>/<name>` — no special setup needed.
For single-skill installs from community registries, use the `find-skills` skill.
