# 域名 / 子域接入与「可演示托管」配方

> 2026-09-12 实测（腾讯云 43.138.221.174 + DNSPod + nginx 1.24）
> 触发场景：用户说「把地址换成我的域名」「IP:端口太难看了」「有没有市场/要拿出去演示」

---

## 一、本机实况（先照着这份对照，别重新摸）

| 项 | 实测值 |
|:--|:--|
| DNS 托管 | **DNSPod**（`arvin.dnspod.net` / `wire.dnspod.net`，腾讯云旗下，后台 dnspod.cn 或腾讯云控制台→云解析DNS） |
| `midage.icu` | → 43.138.221.174，80/443 均通 |
| `www.midage.icu` | → 43.138.221.174 |
| 主域内容 | 个人简历/博客（portfolio，`/home/ubuntu/Desktop/hermes/portfolio`，title「Yasin · 帮创业者少踩坑的实战派」） |
| 证书 | Let's Encrypt，`Certificate Name: midage.icu`，Domains = `midage.icu www.midage.icu`（**不含通配符**） |
| nginx 站点 | `sites-enabled/`：`midlife-test`（含 midage.icu 80+443 block）、`hermes-gateway`（listen 8897 → proxy 127.0.0.1:8896）、`red-blue`（空文件） |
| 8896 | **没进程**（8897 那个 nginx 块指着它，故 8897 恒 502）；8880-8900 在听：8894/8895/8897/8899/8900 |

**备案**：主域已备案（80 能服务即证明）；**子域继承主域备案，无需单独备案**。

---

## 二、子域接入标准流程

### Step 0 — 查四样（凭印象会白干）

```bash
dig +short NS <主域>                # 托管商 → 决定去哪操作、步骤怎么讲
dig +short A <主域> <子域>          # 主域解析到哪、子域是否已存在
curl -sI https://<主域>/ | head -3  # 是否已有 HTTPS
sudo certbot certificates           # 证书覆盖哪些域名 + 到期日
grep -rl '<主域>' /etc/nginx/        # 现有 server block 与 443 配置长什么样
```

### Step 1 — 用户加 DNS 记录（唯一需要他动手的一步）

| 后台格子 | 填 |
|:--|:--|
| 主机记录 / 子域名 | `<子域>`（如 `apex`） |
| 记录类型 | `A` |
| 记录值 | 服务器公网 IP |
| TTL | 默认不动 |

没有 DNSPod 通配符证书时**不要**顺手选 CNAME 到主域（证书不覆盖）。

### Step 2 — 签证书（80 通即自动验证）

```bash
sudo certbot --nginx -d <子域> --non-interactive --agree-tos -m <邮箱>
sudo certbot certificates | grep -A3 '<子域>'   # 确认新增一张证
```

通配符 `*.主域` **必须走 DNS-01**（要 DNS API 权限或手动加 TXT），成本高于逐个子域 HTTP-01 —— 除非要一次性挂十几个子域，否则别选。

### Step 3 — nginx server block + 静态直出

```nginx
# /etc/nginx/sites-enabled/<name>
server {
    listen 80;
    server_name <子域>;
    return 301 https://$host$request_uri;
}
server {
    listen 443 ssl;
    server_name <子域>;
    client_max_body_size 10M;

    ssl_certificate     /etc/letsencrypt/live/<子域>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<子域>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    add_header X-Robots-Tag "noindex, nofollow" always;   # 别被搜索引擎收录

    root /var/www/<name>;
    location / { try_files $uri $uri/ /index.html; }
}
```

```bash
sudo nginx -t && sudo nginx -s reload
```

### Step 4 — 静态产物由 nginx 直出（首选架构）

Next.js：`next.config.mjs` 加 `output: 'export'` → `npm run build` → `out/` 拷到 `root` 目录。
纯 HTML 项目：目录直接当 `root`。

| 好处 | 说明 |
|:--|:--|
| 0 常驻进程 | 不用加 keepalive.sh、不占内存、不怕网关重启 |
| 不用开安全组 | 只走已放行的 80/443 |
| HTTPS/缓存/压缩 | 交给 nginx |

⚠️ 静态导出后**连本地桥/后端的组件会失效**（如依赖 Mac 桥的对话面板）→ 演示版隐藏它或显示「演示模式」。自用版（全功能）与演示版（静态、给客户看）分开做，别混用一个 build。

---

## 三、⚠️ 路径前缀反代会被「fetch 绝对路径」打断

**现象**：`https://<主域>/agent/8924/` 反代到 `127.0.0.1:8924` → 页面能打开，**数据全空**。

**根因**：页面 JS 写的是 `fetch('/api/dashboard')`（前导斜杠 = 绝对路径）→ 前缀反代下打到 `https://<主域>/api/dashboard`，而不是 `/agent/8924/api/dashboard` → 全 404。

**动手前先查**（本次实测 8924/8935/8940）：

```bash
curl -s http://127.0.0.1:8924/ | grep -oE "fetch\([^)]{0,60}"          # '/api/' = 绝对路径（有坑）
curl -s http://127.0.0.1:8924/ | grep -oE '(src|href)="[^"]*"'        # 空 = 无外部资源
ls -la <页面目录>/static/ 2>/dev/null                                    # 无 static = 自包含单文件
```

实测结论：16 个 Agent 页 **全是单文件自包含 HTML（CSS/JS 内联、无外部资源）+ `fetch('/api/...')` 绝对路径**。

**三条路（按优先级）**：

| # | 做法 | 评价 |
|:--|:--|:--|
| 1 | 页面改相对路径 `fetch('api/...')`（去掉前导斜杠） | ✅ 标准做法。前缀反代下自动解析正确，一次改完永久有效。**必须配合尾斜杠** |
| 2 | nginx `sub_filter` 文本重写 `'/api/` → `/agent/$port/api/` | ⚠️ 能用但脆（文本级替换易误伤）；仅因页面自包含才安全 |
| 3 | 每个服务独立子域 | ✅ 最省脑，但要多条 DNS + 逐个子域证书，成本最高 |

**尾斜杠强制**（相对路径解析的基准，漏了会错一层）：

```nginx
location = /agent/8924 { return 301 /agent/8924/; }
location /agent/8924/ {
    proxy_pass http://127.0.0.1:8924/;      # 结尾斜杠 = 剥掉前缀
    proxy_set_header Host 127.0.0.1:8924;
    proxy_read_timeout 120s;
}
```

**别做的事**：不改页面直接上前缀反代 —— 页面能开、数据全空，**演示当天才发现最惨**。

---

## 四、需要用户去第三方后台操作时：三件套 + 零操作备选

用户不懂技术、会不耐烦（本次实录：给完步骤后追问「域名后台加记录是什么意思」，随后在我连续取证时打断「你干啥呢」）。

1. **先自查托管位置再给步骤** —— `dig NS` 查出来，直接说「你的域名簿子在 DNSPod」，不要讲「去你的域名服务商」这种废话
2. **类比 + 逐格对照表，不抛术语** —— 域名 = 电话簿，加记录 = 簿子上加一行；然后「后台格子名 | 填什么」逐格列出
3. **永远附一个「你零操作」的备选** —— 例：`主域/子路径`（不动 DNS，Agent 全包）。用户很可能直接选它
4. **取证要快** —— 用户问「怎么还没生效」时一条 `dig` 就够，别连做三四个调查

### DNSPod 高频误操作（2026-09-12 真实翻车）

| 用户做错的 | 正确的 |
|:--|:--|
| 点「**添加域名**」新建了一个域名条目 | 点**主域那一行右侧的「解析」**，在里面「添加记录」 |
| 子域拼错（`apex.midade.icu`，`de` ≠ `ge`） | 拼写必须对 |
| 以为「暂停」= 配置没生效 | 「暂停」= 该域名未通过所有权验证（把子域当独立域名添加时会这样） |

**判别**：`dig A <子域>` 返回空 + 后台状态「暂停」+ 记录数 0 = 记录没建对。**别在错的地方改，让他删掉重来。**

---

## 五、验收清单

```bash
dig +short A <子域>                                   # 有 IP
curl -s -o /dev/null -w '%{http_code}\n' https://<子域>/   # 200
curl -sI https://<子域>/ | grep -i x-robots            # noindex
curl -s https://<子域>/ | grep -o '<title>[^<]*'       # 是对的应用不是默认页
```

手机实测一次（客户视角）——桌面浏览器通不代表手机通。
