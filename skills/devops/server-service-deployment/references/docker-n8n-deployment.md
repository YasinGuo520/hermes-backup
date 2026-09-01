# N8N 部署 + Dify 硅基 401 排查 + 腾讯云防火墙端口实测（2026-09-01）

服务器：43.138.221.174（腾讯云轻量 2核/3.6G/69G），Docker 29.6.1 + Compose v5.3.1。

## N8N 单容器部署（实测可通过）

**结论：内存只剩 ~1G 时不要配 Postgres**（Dify 已吃掉大半内存），单容器 + SQLite 起步，跑通再考虑升级。

### docker-compose.yml（放 ~/Desktop/hermes/n8n/）

```yaml
services:
  n8n:
    image: docker.1ms.run/n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=43.138.221.174
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - N8N_ENCRYPTION_KEY=<openssl rand -hex 16>
      - GENERIC_TIMEZONE=Asia/Shanghai
      - TZ=Asia/Shanghai
    volumes:
      - ./n8n_data:/home/node/.n8n
```

注意：
- **镜像必须走 `docker.1ms.run/` 前缀**，官方镜像名 `n8nio/n8n`（国内直拉超时）。
- `N8N_ENCRYPTION_KEY` 必填（新版 n8n 要求，缺失会启动警告/失败）。
- 镜像约 1.5GB，`docker compose up -d` 拉取在腾讯云上要 5-8 分钟，用 background 跑别干等。
- `docker compose up -d` 会被 Hermes 终端判成长驻进程，必须 background=true。

### 验证

```bash
docker ps --filter name=n8n --format "{{.Names}} {{.Status}}"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5678/healthz   # 200
docker logs n8n --tail 5    # 应出现 "Editor is now accessible via: http://43.138.221.174:5678"
```

2026-09-01 实测版本：2.36.9。

### 公网访问前置：防火墙放行

容器起来 ≠ 公网能访问。**先测公网再让用户操作**：
```bash
curl -s -o /dev/null -w "%{http_code}" http://43.138.221.174:5678/   # 000 = 未放行
```
未放行时指引用户（一句话）：腾讯云控制台 → 轻量应用服务器 → 防火墙 → 添加规则 → TCP 5678 → 确定。
已放行端口全被占用时，改映射端口无意义（新口也未放行），唯一路径就是让用户加规则或 nginx 80 反代（80 空闲时）。

## Dify 模型供应商 401 排查（CredentialsValidateFailedError）

**现象**：Dify 控制台配 SiliconFlow key，保存报 `CredentialsValidateFailedError: status code 401 and response body {"code":30014,"data":null,"message":"Token is invalid."}`。

**结论链（快速定位）**：
1. `docker logs full-api-1 | grep -i "401\|30014"` —— 确认错误来自 Dify 的 key 校验。
2. **验证失败 Dify 不保存凭据**：`provider_credentials` 表为空/无该 provider 行 = key 根本没进去。
   ```bash
   docker exec full-db_postgres-1 sh -c 'psql -U postgres -d dify -t -c "SELECT provider_name, credential_name, updated_at FROM provider_credentials;"'
   ```
3. 用服务器 `.env` 的有效 key 独立验证，排除"服务端 key 坏"的可能：
   ```bash
   curl -s https://api.siliconflow.cn/v1/chat/completions \
     -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-ai/DeepSeek-V4-Flash","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
   ```
   200 = key 有效 → **结论：用户控制台里填的 key 是坏的**（复制错/旧 key/带空格），把有效 key 给用户重填。code 30014 = SiliconFlow 的 token invalid，与 DeepSeek 无关。

**⚠️ 验证 key 别用 `/v1/user/info`**：该端点已废弃，返回 410 `{"code":20092,"message":"This endpoint is deprecated..."}`，会误判。用 `/v1/models`（200 列表）或 `/v1/chat/completions`。

## 腾讯云防火墙端口实测（2026-09-01 逐口 curl 公网验证）

- **已放行且有服务监听**：80, 8001, 8002, 8850, 8894, 8895, 8897, 8899, 8900, 8910-8917（含 8913/8915）, 8920, 8921, 8922, 8923, 8931
- **本机在监听但公网 000（未放行）**：5678（N8N）, 8896（dashboard）, 8851（Dify API/443 映射）
- **本机未监听、放行与否未知**：8000, 8080, 8898, 8918, 8924+, 9001/9002（测试 000 不代表防火墙拒绝，可能是服务没起）
- **443**：裸 IP `https://43.138.221.174` 000（SNI/证书），域名 `https://midage.icu` 200（nginx 443 走域名）

**方法可复用**：判断"防火墙是否放行"必须**先确认本机在监听**（`ss -tlnp` 有该端口），再 curl 公网。本机没监听时公网 000 无法判断放行与否；本机在监听但公网 000 = 确定未放行。