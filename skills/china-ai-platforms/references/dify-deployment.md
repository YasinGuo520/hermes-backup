# Dify 完整版部署实录（2026-09-01 实测终案）

腾讯云轻量 3.6G 内存 / 2核 / 69G 磁盘跑通 Dify v1.17 完整版。入口 8850（nginx 容器）、API 内网 5001。

## ⚠️ 头号铁律：装 Open Source 软件直接官方完整版，别自作主张砍组件

**用户明确纠正（原话）**："你别精简啦。直接完整安装不行吗""别再删删减减啦"。

精简版砍掉 plugin-daemon → 模型供应商页面 401/500 连环故障（白屏转圈/SSR超时/日志堆满 ECONNREFUSED），修了三轮还在弹。**完整版一次跑通。**

**正确打开方式：**
```bash
# 1. 拉官方 docker 目录（GitHub 不通走 gh-proxy）
curl -sfL -o dify.zip "https://gh-proxy.com/https://github.com/langgenius/dify/archive/refs/heads/main.zip"
unzip -o -q dify.zip "dify-main/docker/*" -d dify_extract
cp -r dify_extract/dify-main/docker/* ./full/

# 2. envs 模板全部复制成实际配置（compose 引用的是非 .example 路径）
find envs -name "*.example" | while read f; do cp "$f" "${f%.example}"; done
cp security.env.example security.env 2>/dev/null || true

# 3. 根 .env 写关键项
EXPOSE_NGINX_PORT=8850
EXPOSE_NGINX_SSL_PORT=8851
NGINX_PORT=80
NGINX_SSL_PORT=443
CONSOLE_API_URL=            # ⚠️ 必须留空！走 nginx 同源
APP_API_URL=
SECRET_KEY=<随机长串>
POSTGRES_PASSWORD=difypostgres
DB_PASSWORD=difypostgres
REDIS_PASSWORD=difyredis
PLUGIN_DAEMON_URL=http://plugin_daemon:5002

# 4. 启动（必须带 --profile postgresql！）
#    ⚠️ profile 名是 postgresql，不是 db_postgres——写错数据库直接不起
docker compose --profile postgresql up -d
```

**镜像源**（`docker.1ms.run` 前缀，已验证）：`langgenius/dify-api:1.17.0`、`dify-web:1.17.0`、`dify-plugin-daemon:0.6.10-local`（**注意这个 tag 不是 latest**，latest 会 not found）、`dify-sandbox:0.2.15`、`dify-agent-backend:1.17.0`。

## 坑1：api+plugin_daemon 401 —— 密钥必须钉死

**现象**：进控制台后弹 "Failed to request plugin daemon, url: plugin/xxx/management/models"，api 日志 `PluginDaemonClientSideError: Client error '401 Unauthorized'`。

**根因**：api 连 daemon 用的是 `PLUGIN_DIFY_INNER_API_KEY` 这个共享变量，默认值两容器一致但环境注入后可能被 `envs/` 覆盖成不同值 → 401。**必须显式钉同一个值：**

```bash
# 根 .env 加一行（api 和 daemon 的 compose 都用 ${PLUGIN_DIFY_INNER_API_KEY:-默认}）
PLUGIN_DIFY_INNER_API_KEY=<同一串>
# 改完必须 --force-recreate 两个容器：
docker compose --profile postgresql up -d --force-recreate api plugin_daemon
```

**排查**（对比两容器实际值）：
```bash
docker exec full-api-1 sh -c 'echo "$INNER_API_KEY_FOR_PLUGIN"'
docker exec full-plugin_daemon-1 sh -c 'echo "$DIFY_INNER_API_KEY"'
```

## 坑2：web 500/白屏 = SSR 回环

- **CONSOLE_API_URL/APP_API_URL 留空**（走 nginx 同源），**不要写公网 IP**——web 容器内 SSR fetch 公网被腾讯云防火墙拦回环超时
- **也不要写 `host.docker.internal`**（浏览器端解析不了，白屏转圈）——留空最快
- 验证 SSR：`docker exec full-web-1 sh -c 'wget -q -O- http://api:5001/health'` 应返回 JSON

## 坑3：数据库没迁移 / setup 500

- `/console/api/setup` 报 500 且日志 `relation "dify_setups" does not exist` → 容器启动的自动迁移没跑成，手动：`docker exec full-api-1 sh -c "cd /app/api && flask db upgrade"`
- `curl /health` 200 **不代表能用**——它只探进程不查表，要看 `/console/api/setup`

## 坑4：setup 被废账号占用 = 别人没法注册

管理员只初始化一次。若用 curl 测试账号占了 setup，用户注册就 500。**重置数据库：**
```bash
docker compose --profile postgresql down
sudo rm -rf ./volumes/db/data    # ⚠️ 卷是 root 属主，必须 sudo，普通 rm 会 Permission denied 白删
docker compose --profile postgresql up -d
# 等 api healthy（最长90秒，期间 502 正常）
# curl /console/api/setup → {"step":"not_started"} = 可以注册
```

## 坑5：登录 API 不能 curl 明文密码

`POST /console/api/login` 用明文密码 → `{"code":"authentication_failed","message":"Invalid encrypted data"}` — Dify 1.17 要求 RSA 加密密码。**别猜加密逻辑，用 Playwright 走真实登录拿 cookie：**

```python
# server 上已装 playwright（market-research venv），chromium 1228 headless
page.goto("http://127.0.0.1:8850/signin")
page.fill("input[type='email']", EMAIL)
page.fill("input[type='password']", PASS)
page.get_by_text("登录").click()
# 登录成功后 cookie 里有 access_token / csrf_token / refresh_token
```

调 console API 时 header 要带全：`Authorization: Bearer <access_token>` + `X-CSRF-Token: <csrf_token>` + `Cookie: <全量cookie>` + `Origin/Referer`。只带 Bearer 会 401 CSRF missing。

## 验证与日常

```bash
docker ps --format "{{.Names}} {{.Status}}" | grep full-   # api healthy = 就绪
curl -s http://127.0.0.1:8850/console/api/setup            # {"step":"not_started"} 可注册 / finished 已注册
```

- 完整版容器全家：api / worker / worker_beat / web / db_postgres / redis / sandbox / local_sandbox / plugin_daemon / agent_backend / ssrf_proxy / nginx —— 都是 compose 管的，`restart: always` 自动拉起，**不要写进 keepalive.sh**
- 内存：3.6G 完整版跑完剩 1.5G 可用，OK
- 用户注册后，左侧菜单找不到"模型供应商"是正常的（1.17 新界面改版）→ 路径：**右上角头像 → 设置 → 模型供应商**，或新建应用选模型时出现
- Dify 1.17 的登录/页面 500 报错弹窗：先确认 api healthy + `/console/api/setup` 正常，再让用户 Ctrl+Shift+R 强刷（旧弹窗缓存），别急着改配置