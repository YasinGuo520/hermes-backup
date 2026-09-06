# DeepSeek API Key 全生态轮换 SOP（2026-09-06 实测）

**触发**：怀疑 key 泄漏 / DeepSeek 控制台出现本地日志对不上的模型用量（尤其 pro）→ 重置 key 后把新 key 分发到全生态。核心签名：**控制台显示 v4-pro 用量、而服务器+Mac 两端 Hermes 日志逐条全是 flash（agent.log 里 `OpenAI client created ... model=` 计数）→ key 泄漏/外部盗刷，不是本机配置问题 → 立即轮换 key**。

**用户流程**：让用户在 platform.deepseek.com → API Keys 删旧建新，把新 key 发来。旧 key 立即 401（验证：`curl https://api.deepseek.com/user/balance -H "Authorization: Bearer <旧key>"` = 401；新 key = 200 + balance）。

## 全端清单（换 key 时逐项过）

| 端 | 文件/位置 | 读取时机 → 是否需重启 |
|---|---|---|
| Hermes 主配置 | `~/.hermes/.env` 的 `DEEPSEEK_API_KEY`（config.yaml 全用 `${DEEPSEEK_API_KEY}` 变量引用） | gateway **启动时**加载进进程 env → **必须重启 gateway** 才生效 |
| 16 公司 agents | `common/llm.py` `_key()` 每次调用现读（os.environ → ~/.hermes/.env → company-agents/.env） | **无需重启**，自动新 key |
| 研究落地页 8920-8923 | `server.py` 模块级 `API_KEY = os.environ or _env or 硬编码`（import 时执行） | **模块加载时读** → 需重启进程 |
| 服小助 | `ai_cs_package/.env` | 进程重启后生效 |
| 中年人生 | `/var/www/midlife-test/backend/.env` **+ supervisor conf 的 `environment=DEEPSEEK_API_KEY=...`** | 两处都改 + `supervisorctl reread && update && restart` |
| Mac Hermes | `~/.hermes/.env` | 重启 Mac gateway（launchd） |
| n8n | sqlite credential（加密存储） | 见下 |
| Dify | PG `provider_credentials.encrypted_config`（HYBRID 加密） | 见下 |

**⚠️ 最常见的坑——只改 .env 没重启进程**：gateway/服务进程 env 是启动时加载的，改完 .env 必须重启对应进程；反之 llm.py 这类调用级读取的不用重启。判断依据：grep 代码看 key 是模块级还是函数级读取。

**⚠️ supervisor conf 改完必须 `reread && update`**：`supervisorctl restart` 用的是 **supervisord 内存里的旧配置**（supervisord 只在启动/reread 时读 conf）。改了 `/etc/supervisor/conf.d/*.conf` 后：`sudo supervisorctl reread && sudo supervisorctl update`（会输出 stopped/updated）再确认进程 env（`tr '\0' '\n' < /proc/PID/environ | grep DEEPSEEK`）。

**⚠️ Mac .env 垃圾值坑**：曾发现 Mac `~/.hermes/.env` 第一行是 `DEEPSEEK_API_KEY="hermes setup model"`（疑似某次 `hermes setup model` 命令把字面量写进 .env）。症状：Mac Hermes 调 DeepSeek 全失败但服务器正常。改法：python 读改写该行，别用 sed（值含引号）。

## n8n credential 换 key

```bash
# 1. 删旧（shared_credentials 列名是 credentialsId 不是 credentialId！）
python3 -c "
import sqlite3
db = sqlite3.connect('<n8n_data>/database.sqlite')
for cid, nm in db.execute(\"SELECT id, name FROM credentials_entity WHERE type='openAiApi'\"):
    db.execute('DELETE FROM shared_credentials WHERE credentialsId=?', (cid,))
    db.execute('DELETE FROM credentials_entity WHERE id=?', (cid,))
db.commit()"
# 2. 导入新（CLI import 必须带 UUID id + 挂到 personal project 的 shared_credentials 由 import 自动建）
MYID=$(python3 -c "import uuid; print(uuid.uuid4())")
# 写 JSON: [{"id": MYID, "name": "DeepSeek 官方 (v4-flash)", "type": "openAiApi", "data": {"apiKey": "sk-新", "baseURL": "https://api.deepseek.com/v1"}}]
docker cp cred.json n8n:/tmp/ && docker exec n8n n8n import:credentials --input=/tmp/cred.json
```

n8n 无原生 DeepSeek 节点 → 用 openAiApi credential + baseURL 指向 api.deepseek.com/v1（OpenAI 节点选此凭证、model 填 `deepseek-v4-flash`）。

## Dify credential 换 key（DB 直改，免 UI 登录）

Dify console 登录密码走 RSA 加密（curl 明文必 401）——**UI 能做的事优先让用户在 UI 点，别死磕 API**（用户明确纠正过「别绕，我去装」）。但 key 轮换要改的是已存在 credential，DB 路径实测可用：

1. 加密结构：`provider_credentials.encrypted_config` = `{"api_key": "<base64 密文>"}`，base64 解出前缀 `HYBRID`，加密走 `extensions.ext_key_provider`（RSA key provider，私钥缓存 redis，按 tenant_id）。**不是** `core/tools/utils/system_encryption.py`（那是另一层 AES）。
2. 必须在 flask app context 内跑（否则 `Redis client is not initialized`）：
```bash
docker exec full-api-1 sh -c 'cd /app/api && PYTHONPATH=/app/api python3 - << EOF
from app_factory import create_app
socketio_app, flask_app = create_app()   # ⚠️ 用 app_factory，app.py 的 create_app 返回 tuple
with flask_app.app_context():
    from core.helper.encrypter import decrypt_token, encrypt_token
    # psycopg2 连 dify 库 → SELECT p.tenant_id, pc.id, pc.encrypted_config
    #   FROM providers p JOIN provider_credentials pc ON p.credential_id=pc.id WHERE provider_name LIKE "%deepseek%"
    # data = json.loads(cfg); old = decrypt_token(tid, data["api_key"])
    # new_cfg = json.dumps({"api_key": encrypt_token(tid, "<新key>")})
    # UPDATE provider_credentials SET encrypted_config=new_cfg WHERE id=cid
    # 回读 decrypt_token 验证
EOF'
```
3. create_app 很慢（连 redis/postgres/初始化）——前台易超 180s，用 terminal background + notify，或加大 timeout。
4. 验证：回读 decrypt 前缀 == 新 key 前 12 位。

## 收尾验证

- 全盘活跃配置无旧 key 残留：`grep -rl "<旧key>" <各 .env/config/conf>`（历史 logs/sessions 里的旧 key 不算，别扫全盘会超时——**限定文件清单逐个 grep**）
- 新 key 调 balance 200
- 提醒用户：控制台确认只剩新 key；以后 key 别明文发聊天/硬编码进代码（red-blue server.py 曾硬编码一把做 fallback——换成 `~/.hermes/.env` 读取，硬编码值只做占位）
