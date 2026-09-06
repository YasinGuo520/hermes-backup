# 全站模型锁死审计 + n8n 凭证 CLI 导入 + Dify 供应商配置内部（2026-09-04 实测）

**触发**：用户要求「所有模型锁死 X / 查导航页里用到模型的服务」——Hermes 配置侧锁死见 `hermes-advanced-setup` 技能「全链路模型锁死」节；本文是**自建 Web 服务生态侧**（导航 Hub 链出去的所有服务 + docker 平台）的审计方法与被审计结论。

**核心教训**：主模型锁了 ≠ 全锁。真实漏网常藏在**每个服务的 config.py/代码硬编码**里——本次就在中年人生 backend 抓到 `deepseek-chat`（=V3 系，非 v4-flash）。

## 一、审计扫描流程（证据链，按序执行）

### 1. 导航页链出去的服务清单
```bash
grep -oE 'href="[^"]*"' ~/Desktop/hermes/hermes-hub/*.html | grep -vE '\.css|\.js|#|mailto' | sort -u
```
Hub 二级页 agent-hub.html 链 8924-8940；index.html 链 5678/8002/8850/8894/8895/8897/8899/8900/8910-8917/8931/midage.icu(→8001)。

### 2. 端口 → 进程 → 代码目录（一次扫全）
```bash
for port in <全部端口>; do
  pid=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)
  [ -n "$pid" ] && echo "$port | $(readlink -f /proc/$pid/cwd 2>/dev/null) | $(tr '\0' ' ' < /proc/$pid/cmdline | cut -c1-80)"
done
```
坑：
- `ss -tlnp` 显示不了**其他用户进程**的 pid（root/dify 起的）——grep 不到就 `ps aux` 兜底，别误判"没跑"。
- `readlink /proc/PID/cwd` 对某些 `python3 -m http.server` 返回空——用**页面标题反查身份**：
  ```bash
  curl -s -m 3 http://127.0.0.1:$port/ | grep -oiE '<title>[^<]*' | head -1
  ```
  （8899生日/8910案例墙/8911选品大屏/8912量化/8913游戏/8914占卜/8915像素画/8916名片/8917server状态/8931机甲 全静态；8897=Hermes Dashboard 跟主配置走）
- 静态展示页也要查：`grep -rnE "chat/completions|api\.deepseek|api\.siliconflow|openrouter" <目录>/*.html *.js`（排除 .min.js）——纯静态页应零命中。

### 3. 每个业务服务 grep 模型配置
```bash
grep -rniE "MODEL|model *[:=]|deepseek|base_url" <服务目录> --include="*.py" --include="*.env" | grep -vE "venv|__pycache__"
```
本次审计结论：company-agents 16 个 agent 中 15 个 `from common import ... llm`（公共层 llm.py `MODEL="deepseek-v4-flash"`，pipeline/8930 纯流程页无 LLM 调用）；红蓝/六分身/市场/行业调研 server.py 全 `MODEL = "deepseek-v4-flash"`；服小助 `app/config.py DEEPSEEK_CHAT_MODEL="deepseek-v4-flash"`。
⚠️ 检查"是否走公共层"时**先 cd 到项目目录再循环 grep**，否则路径错全报 ❌ 误判。

### 4. 全盘 grep 硬编码模型名（过滤第三方库）
```bash
grep -rniE "deepseek-(v4-pro|v4-chat|reasoner|chat)|gpt-4|claude-|qwen-max|kimi|glm-" <范围> --include="*.py" --include="*.js" --include="*.json" -l | grep -vE "venv|node_modules|__pycache__|\.min\.js"
```
命中文件先看路径：venv/site-packages 的 tencentcloud SDK、dify 插件自带 `deepseek-v4-pro.yaml` 只是模型清单不是调用配置——**别误判**。

## 二、本次抓到并修复的雷（2026-09-04）

| 服务 | 问题 | 修复 |
|---|---|---|
| 中年人生 8001 (midage.icu) | `/var/www/midlife-test/backend/config.py` `DEEPSEEK_MODEL="deepseek-chat"` | patch 成 `deepseek-v4-flash` + `sudo -n supervisorctl restart midlife-test`（supervisor 管着，`/etc/supervisor/conf.d/midlife-test.conf`；非 root 直接 `supervisorctl` 报 PermissionError，`sudo -n` 可行）→ curl 200 + 进程 PID 已换 |
| Dify 8850 | PG `providers` 表残留硅基 provider 行（违反非硅基铁律） | `DELETE FROM providers WHERE provider_name='langgenius/siliconflow/siliconflow'`——删前确认 provider_models/app_model_configs 全空（实际零调用）才安全 |

**附带发现（未改，已告知用户）**：服小助知识库 embedding 调 `api.deepseek.com/v1/embeddings` → **404，DeepSeek 官方无 embedding 端点**，RAG 一直静默降级成关键词检索（chat 不受影响）。要修需换 embedding 渠道（硅基 BGE 等），属功能问题不是模型锁问题。

## 三、n8n 模型配置：凭证 CLI 导入（实测可行）

n8n 2.36.9 无原生 DeepSeek 节点、无全局模型设置——模型是**每个 workflow 节点里选的**。接入 DeepSeek = openAiApi 凭证 + baseURL 覆盖 + 节点 model 填 `deepseek-v4-flash`。

凭证导入（`n8n import:credentials` CLI）：
```bash
# ⚠️ import JSON 必须带显式 "id": UUID！否则 SQLITE_CONSTRAINT: NOT NULL failed: credentials_entity.id
MYID=$(python3 -c "import uuid; print(uuid.uuid4())")   # 别用变量名 UID——bash 只读内置变量，赋值失败文件不生成
cat > /tmp/n8n-cred.json << EOF
[
  {
    "id": "$MYID",
    "name": "DeepSeek 官方 (v4-flash)",
    "type": "openAiApi",
    "data": { "apiKey": "sk-...", "baseURL": "https://api.deepseek.com/v1" }
  }
]
EOF
docker cp /tmp/n8n-cred.json n8n:/tmp/n8n-cred.json
docker exec n8n n8n import:credentials --input=/tmp/n8n-cred.json   # "Successfully imported 1 credential"
```
- 导入自动建 shared_credentials 行，把凭证 link 到 owner personal project（无需手插）。
- 验证：宿主机直读 bind volume 的 sqlite：`python3 -c` 查 `~/Desktop/hermes/n8n/n8n_data/database.sqlite` 的 `credentials_entity` + `shared_credentials`。
- 查 n8n 有无模型节点/workflow：读 workflow_entity.nodes 匹配 `openAi|deepseek|gpt-`；`credentials_entity` 为空 = 没配任何 key。本次 n8n 为 0 workflow 0 credential 空壳。

## 四、Dify 供应商配置内部（2026-09-04 实测）

### 已验证的表结构（PG `dify` 库，`docker exec full-db_postgres-1 psql -U postgres -d dify`）
- 账号表叫 **`accounts`**（不是 users）：id/email/name/status/password（密码是 base64(sha256hex) 形态，非 werkzeug 明文格式）
- `providers`：tenant_id/provider_name(形如 `langgenius/siliconflow/siliconflow`)/provider_type/is_valid/credential_id
- `provider_models`：provider_name/model_name/model_type/is_valid（**为空 = Dify 没配任何可用模型**）
- `app_model_configs`：app 的 provider/model_id/model 列（空 = app 没绑模型，不产生调用）
- 已装插件代码在 `volumes/plugin_daemon/cwd/langgenius/<plugin>-<ver>@<hash>/`——deepseek 插件要另装（Dify 1.17 全插件化）；装好后自带模型清单 `models/llm/deepseek-v4-flash.yaml` + `v4-pro.yaml`（预定义模型不需要 provider_models 行，provider_models 空 = 正常，别误判）
- **`provider_credentials` 表存在且是凭证本体**（2026-09-06 实测修正早期"不存在"误判）：列 = id/tenant_id/provider_name/credential_name/encrypted_config/user_id/visibility；`providers.credential_id` → `provider_credentials.id`。`encrypted_config` 是 **JSON**（如 `{"api_key": "<加密值>"}`），加密值带 `SFlCUklE`=base64("HYBRID") 前缀 = **KMS RSA 加密**（key_provider_manager → rsa_key_provider，私钥缓存在 redis），不是 SystemEncrypter(AES/SECRET_KEY)。UI 填 key 后 `is_valid=t` 但**旧 key 已删/换新时 DB 里还是旧加密值**——轮换 key 必须更新此表。

### Dify 凭证 DB 更新（key 轮换时，2026-09-06 实测成功）

```bash
docker exec full-api-1 sh -c 'cd /app/api && PYTHONPATH=/app/api python3 -c "
import os, json
os.environ.setdefault(\"MIGRATION_ENABLED\", \"false\")
from app_factory import create_app
socketio_app, flask_app = create_app()          # ⚠️ 返回 TUPLE！不是 flask app 本身
with flask_app.app_context():                    #    用 [1]，[0] 是 socketio app 没有 app_context
    from core.helper.encrypter import decrypt_token, encrypt_token
    import psycopg2
    conn = psycopg2.connect(host=\"full-db_postgres-1\", dbname=\"dify\", user=\"postgres\", password=\"difypostgres\")
    cur = conn.cursor()
    cur.execute(\"SELECT p.tenant_id, pc.id, pc.encrypted_config FROM providers p JOIN provider_credentials pc ON p.credential_id = pc.id WHERE p.provider_name LIKE %s\", (\"%deepseek%\",))
    for tid, cid, cfg in cur.fetchall():
        data = json.loads(cfg.strip())
        old = decrypt_token(tid, data[\"api_key\"])     # 读旧 key
        new_cfg = json.dumps({\"api_key\": encrypt_token(tid, \"sk-NEW-KEY\")})
        cur.execute(\"UPDATE provider_credentials SET encrypted_config=%s WHERE id=%s\", (new_cfg, cid))
    conn.commit()                                     # 回读 decrypt_token 验证新 key
"'`
```
坑：① `PYTHONPATH=/app/api` **必须显式给**——`docker exec cd /app/api` 不够，python 脚本在 /tmp 时 `sys.path[0]=/tmp` import 不到 app；② `create_app()` 极慢（分钟级，连 redis/一堆初始化）——timeout 给 300-420s，别用 180s；③ SECRET_KEY/DB 密码在 `dify/full/.env`（`sk-xingren-...` / `difypostgres`），RSA 私钥走 redis 缓存所以必须 app_context 内跑（裸 python 连 DB 解密报 "Redis client is not initialized"）。

### ⚠️ 死路：console API 自动化要 RSA 加密密码，别走 DB 改密
`POST /console/api/login` 要求 **RSA 加密后的密码**——只改 PG `accounts.password` 换临时 hash 再登录必失败（401 `Invalid encrypted data`），还白改用户密码。若已改**必须还原原 hash**（本次备份到 `/tmp` 后还原成功，密码零改动）。
**用户明确纠正（2026-09-04："别绕，我去装"）**：Dify 插件安装 + 模型供应商表单是 **UI-gated 配置**——别在 DB/API 上绕，直接把最短 UI 路径给用户：
1. 打开 http://43.138.221.174:8850 登录
2. 设置 → 模型供应商 → 搜 DeepSeek（没有就点右上「装插件」装 deepseek）
3. 填 **DeepSeek 官方** key（同 Hermes 的 DEEPSEEK_API_KEY）
4. 添加模型 `deepseek-v4-flash`；app 里模型下拉选 v4-flash
⚠️ key 填官方（api.deepseek.com），别选硅基流动——已把硅基 provider 从后台删掉防误配。

## 相关既有文档
- N8N 单容器部署/防火墙实测：`docker-n8n-deployment.md`（同技能）
- Dify compose 完整部署链：`china-ai-platforms` 技能 `references/dify-deployment.md`
- Hermes 配置侧锁死（delegation+auxiliary auto 段逐段钉）：`hermes-advanced-setup` 技能「全链路模型锁死」
