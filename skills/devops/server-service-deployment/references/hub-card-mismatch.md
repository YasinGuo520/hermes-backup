# Hub 导航卡片内容↔链接错配排查（简历↔中年人生互换实录）

**用户症状**：「导航页 XX 和 YY 对应的网页不对啊 / 互换了」

## 根因模式

build_hub.py 有两处数据源，都可能与实际服务错配：
- `PROJECTS`（端口卡片）→ href 自动生成 `http://IP:<port>`，卡片名可能已过时
- `EXTERNAL_LINKS`（外链）→ 手写 url，名称可能已过时

**端口↔真实服务 的权威真相源是 nginx 配置，不是卡片文案、不是记忆。**

## 排查链（按序执行）

```bash
# 1. 对卡片里每个 href 直接 curl，看实际返回什么页面
curl -s http://127.0.0.1:<PORT>/ | head -8     # 看 title / meta refresh / redirect
#    <meta http-equiv="refresh" content="0;url=/test.html"> = 是中年人生测试页

# 2. nginx 定真相：端口谁在听？listen 哪台？root/proxy_pass 指向哪？
ss -tlnp | grep -E ':<PORT>'
grep -rE 'listen|server_name|root|proxy_pass' /etc/nginx/sites-available/midlife-test

# 3. 打开 build_hub.py 对照 PROJECTS + EXTERNAL_LINKS 两条数据源，找出 name↔href 错配
```

**判定案例（2026-09-02 实测）**：
- `https://midage.icu` 实际 = portfolio（nginx root → ~/Desktop/hermes/portfolio）
- `8894` 实际 = 中年人生（nginx midlife-test：root /var/www/midlife-test/frontend + proxy_pass 8001）
- Hub 当时写成「个人简历→8894」「中年人生→midage.icu」→ 全反了

## 修复（改源码，不改生成物）

```bash
# 1. 改 build_hub.py：
#    PROJECTS 里 8894 卡片 name 改回「中年人生」，desc 同步
#    EXTERNAL_LINKS 里 midage.icu 外链 name 改回「个人简历」
# 2. 重跑生成 + 验证
cd ~/Desktop/hermes/hermes-hub && python3 build_hub.py
grep -B2 -A4 'href="http://43.138.221.174:8894"' index.html   # 卡片名应对上
grep -B2 -A4 'href="https://midage.icu"' index.html           # 外链名应对上
```

**铁律：永远改 build_hub.py 再重新生成 index.html——直接编辑 index.html 会被下次 build 覆盖。**

## 当前正确映射（2026-09-02 后）

| 入口 | 真实服务 |
|------|---------|
| 8894 | 中年人生（nginx midlife-test，API 在 8001） |
| midage.icu (80/443) | 个人简历 portfolio（nginx root） |