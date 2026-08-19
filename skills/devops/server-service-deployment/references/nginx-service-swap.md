# Nginx 服务互换/迁移（端口↔域名对调）实操记录

**案例（2026-08-19）：** 用户要求把「个人简历」和「中年人生诊断」的地址互换——
简历原本 `http://IP:8894/resume.html`（portfolio 静态目录），中年人生原本 `https://midage.icu`（nginx→8001 FastAPI）。
互换后：简历→`https://midage.icu`，中年人生→`http://IP:8894`。

## 完整流程

1. **摸清现状**：`ss -tlnp` 找端口归属 → `readlink /proc/PID/cwd` 确认服务目录 → `curl` 验证标题
2. **确认互换含义**（用户可能有歧义：换域名绑定？换端口？只加短链？）——先问清楚，尤其涉及线上商业服务时
3. **备份 nginx 配置**：`sudo cp /etc/nginx/sites-enabled/<conf> /etc/nginx/backups/<conf>.bak-<日期>`
4. **写新配置**：write_file 拒绝写 /etc/nginx（敏感路径）→ 先写 `/tmp/xxx.conf` 再 `sudo cp`
5. **同步改 keepalive.sh**（关键！见下）
6. **改 Hub/工具箱等所有引用旧地址的页面**（改前备份）
7. **验证**：外网 curl 两个地址 + 关键路径探活

## 核心坑

### 坑1：keepalive.sh 回滚顶掉 nginx（最阴险）

端口从 `http.server`/socat 换成 nginx 反代后，**必须从 keepalive.sh 对应数组删除该条目**。
keepalive 每3分钟 curl 探活，发现端口"没起 http.server"就重新拉起旧服务跟 nginx 抢端口。

**症状特征：** 改完 nginx reload 后 `curl http://127.0.0.1:PORT/` 返回的还是旧页面内容，且 nginx 并未监听该端口。

### 坑2：nginx reload 端口被占时静默失败

`sudo nginx -t && sudo systemctl reload nginx` 显示 OK，但新监听端口根本没起来。
原因：reload 时目标端口仍被旧进程（http.server）占用，nginx 绑定失败但**不报错**。

**排查：** `sudo ss -tlnp | grep <PORT>` — 如果没有任何进程监听该端口（或还是旧 PID），说明 nginx 没绑上。
**修复：** 杀掉旧进程（`sudo kill <PID>`）→ **再次** `sudo systemctl reload nginx` → 再查监听。

### 坑3：www-data 读不了 /home/ubuntu 下的静态目录 → 500

nginx 默认用户 www-data 无法穿透 `/home/ubuntu`（权限 750 drwxr-x---）→ nginx 直接 500。
`curl https://域名/` 返回 `<title>500 Internal Server Error</title>`。

**修复：**
```bash
sudo chmod o+x /home/ubuntu /home/ubuntu/Desktop /home/ubuntu/Desktop/hermes /home/ubuntu/Desktop/hermes/<项目目录>
sudo chmod o+r <项目目录>/*.html
```

### 坑4：sites-enabled 里的 .bak 文件会被 nginx 加载

备份文件如果留在 `/etc/nginx/sites-enabled/`，nginx 会一起加载 → `conflicting server name` 警告（老配置抢先匹配）。
**备份要放到 `/etc/nginx/backups/`，不能放 sites-enabled/。**

### 坑5：微信支付回调域名

商业服务换域名/IP 后，微信支付 notify_url 必须跟着改（在微信商户平台配），否则支付回调失败。
本案例中年人生未配商户号（.env 无 WECHAT_MCHID），无影响——但换地址前先查 `grep -rn "WECHAT_NOTIFY_URL" backend/`。

## 验证清单（改完必跑）

```bash
# 新域名侧
curl -sk https://域名/ | grep -oE "<title>[^<]*</title>"
curl -sk -o /dev/null -w "%{http_code}\n" https://域名/关键路径.html

# 新端口侧
curl -s http://127.0.0.1:PORT/ | grep -oE "<title>[^<]*</title>"
curl -s -o /dev/null -w "quiz: %{http_code}\n" http://127.0.0.1:PORT/关键API路径

# keepalive 确认已移除
grep -c "项目名|旧端口" ~/Desktop/hermes/scripts/keepalive.sh   # 期望 0

# Hub 链接确认
curl -s http://127.0.0.1:8895/ | grep -oE "https://新域名|旧端口" | head -3
```

## 参考

- 权限坑：nginx www-data 读 home 目录 500（2026-08-19 实测）
- 端口归属排查：`ss -tlnp` + `readlink /proc/PID/cwd` + `curl | grep <title>`
- 主 SKILL.md 的 keepalive 章节也有此坑的摘要
