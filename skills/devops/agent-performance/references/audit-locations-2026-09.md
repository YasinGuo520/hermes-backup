# LLM 调用方配置位置实测表（2026-09-06，腾讯云 43.138.221.174）

## 端口 → 服务 → 配置位置

| 端口 | 服务 | 目录 | 模型配置位置 | 2026-09-06 实测 |
|---|---|---|---|---|
| 8895 | Hub（导航仪） | ~/Desktop/hermes/hermes-hub/ | 纯静态，无模型 | ✓ |
| 8897 | Hermes Dashboard | hermes dashboard | 跟 Hermes config 走，不用单独查 | ✓ |
| 8924-8940 | 公司16 agents | ~/Desktop/hermes/company-agents/ | 公共层 `common/llm.py` 的 `MODEL`；每个 `app.py` 应 `from common import ... llm` | 15/16 走公共层；pipeline(8930) 纯流程页无 LLM |
| 8920 红蓝 | ~/Desktop/hermes/red-blue-method/ | `server.py` `MODEL = "deepseek-v4-flash"` 硬编码 | ✓ |
| 8921 六分身 | six-persona/ | 同上 | ✓ |
| 8922 市场调研 | market-research/ | 同上 | ✓ |
| 8923 行业调研 | industry-research/ | 同上 | ✓ |
| 8002 服小助 | ~/Desktop/hermes/ai_cs_package/ | `app/config.py` `DEEPSEEK_CHAT_MODEL` | flash ✓；⚠️ `DEEPSEEK_EMBED_MODEL="deepseek-embedding"` 调官方 /v1/embeddings **404 不存在**（RAG 语义检索静默降级，DeepSeek 无 embedding） |
| 8001 中年人生(midage.icu) | /var/www/midlife-test/backend/ | `config.py` `DEEPSEEK_MODEL` | 🔴 2026-09-04 抓到写的是 `deepseek-chat`(V3) → 改 flash + `sudo -n supervisorctl restart midlife-test`（supervisord 管理，非 root 直接 supervisorctl 报 PermissionError） |
| 8001 前端 8894 | /var/www/midlife-test/frontend | 静态，调 8001 API | ✓ |
| 8900 工具箱 | toolbox/ | 纯导航卡片页 | ✓ 无模型 |
| 8899/8910-8917/8931 | 生日/案例墙/选品大屏/量化/游戏/占卜/像素画/名片/状态/机甲 | 各展示目录 | 纯前端；grep HTML/JS 直连 `chat/completions\|api.deepseek\|api.siliconflow\|openrouter` 全无 | ✓ |
| 5678 n8n | docker | volume `~/Desktop/hermes/n8n/n8n_data/database.sqlite` | 见 docker-platform-internals.md | 空壳 0 workflow |
| 8850 Dify | docker (full-*) | PG `dify` 库 | 见 docker-platform-internals.md | 2026-09-06 配好 deepseek 官方 flash |

## 标题反查速查（http.server cwd 读不到时）

8899=`🎂 郭泽莹 · 13岁生日快乐`；8900=`方法论工具箱`；8910=`变现案例墙`；8911=`抖音选品大屏`；8912=`QuantBoard`；8913=`彩虹收集乐园`；8914=`玄机灵签`；8915=`像素画展厅`；8916=`3D粒子名片`；8917=`MATRIX SERVER STATUS`；8931=`机甲指挥官`。

## 全盘兜底 grep（排除误报）

```bash
grep -rniE "deepseek-(v4-pro|v4-chat|reasoner|chat)|gpt-4|gpt-5|claude-|qwen-max|kimi|glm-|doubao|hunyuan" \
  <服务目录们> --include="*.py" --include="*.js" --include="*.html" \
  --include="*.json" --include="*.yaml" --include="*.env*" \
  | grep -vE "node_modules|venv|__pycache__|\.min\.js|package-lock|\.bak"
```

**误报过滤**：`site-packages`（tencentcloud SDK models.py）、`plugin_daemon/cwd`（dify 插件模型清单 yaml）、`venv/` 直接排除——那是模型目录/依赖不是调用配置。

## Key 使用点分布（sk-ce1a8ba2...81f，2026-09-06 实测）

服务器仅 3 处：Hermes config.yaml/.env、ai_cs_package/.env、red-blue-method/server.py（硬编码默认值！）。Mac：~/.hermes/.env（DEEPSEEK_API_KEY 同值）。⚠️ Mac 的 OPENAI_API_KEY 与 SILICONFLOW_API_KEY 是同一把硅基 key——用 OPENAI_API_KEY 的 app 实际打硅基。
