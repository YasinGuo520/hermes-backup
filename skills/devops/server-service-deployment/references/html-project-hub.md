---
name: html-project-hub
description: "管理服务器上多个静态HTML项目——中央导航页 + 每项目独立HTTP端口 + Python构建脚本自动化。覆盖新增/删除/端口管理/导航页更新全流程。"
version: 1.0
author: Yasin + Agent
created_by: agent
---

# HTML 项目导航中心

在 VPS 上运行多个静态 HTML 页面，每个项目独立端口，中央导航页一键跳转。

## 架构

```
~/Desktop/hermes/hermes-hub/          # 导航中心目录
├── build_hub.py                      # 构建脚本（编辑数据列表 → 重新生成）
└── index.html                        # 生成的导航页面（静态HTML，不需要后端）

~/Desktop/hermes/<项目A>/             # 项目A目录
└── index.html

~/Desktop/hermes/<项目B>/             # 项目B目录
└── index.html
```

每个项目独立运行 `python3 -m http.server <端口>`，导航页聚合所有链接。

## 构建脚本模式（通用）

核心模式：**Python数据列表 → 渲染函数 → 静态HTML**

```python
PROJECTS = [
    {"port": 8900, "name": "🧰 工具箱", "desc": "...", "icon": "🧰", "color": "#6c5ce7", "tags": [...]},
]

def build():
    # 遍历数据 → 生成HTML卡片 → 输出index.html
    ...
```

**加新项目 = 编辑 `PROJECTS` 列表加一行 → `python3 build_hub.py`**

## ⚠️ 改导航页前必读（用户铁律，2026-08 血泪教训）

1. **先备份**：改 `build_hub.py` 前先 `cp build_hub.py build_hub.py.bak && cp index.html index.html.bak`。曾因直接重建覆盖了用户喜欢的深紫科技风版本（Forty风格是旧版，别覆盖成它）。
2. **只动导航页**：改导航页严禁连带重启/影响其他端口服务。曾因跑 `build_hub.py` + 手动拉服务把 10+ 个 background 服务搞挂，用户明确要求「改动导航页不要全部都挂」。
3. **服务挂了用保活**：全站服务由 `~/Desktop/hermes/scripts/keepalive.sh` 管理（crontab 每3分钟 + @reboot 自动恢复）。需要手动查状态用 `keepalive.sh check`，恢复用 `keepalive.sh start`，不要逐个手动起 http.server。
4. **端口映射现状**：8000 已删（爆款主图已弃，Docker down + socat 杀 + 导航删卡 + 保活移除）；8002=服小助AI客服；8897=Hermes Dashboard（nginx 反代到 8896，hermes serve 是 headless 无 UI 不能直接反代）。

## 端口分配规则

| 端口段 | 用途 |
|:------:|------|
| 8890-8899 | HTML项目（每个项目一个） |
| 8900 | 工具箱（专用） |
| 8920-8923 | AI 方法论落地页（红蓝/六分身/市场调研/行业调研，FastAPI 服务，见 ai-analysis-landing-pages skill） |
| 9000+ | 其他服务 |

**选口原则：**
- 先 `lsof -ti:<端口>` 检查是否被占用
- 避开已知已有的端口（8000/8080/8897/8898/8899/8900）
- 用 `terminal(background=true)` 启动，不要用 setsid/nohup

## 启动新项目服务器

```python
terminal(background=true, command="cd ~/Desktop/hermes/<项目名> && python3 -m http.server <端口> --bind 0.0.0.0")
```

**注意：** 用 `--bind 0.0.0.0` 绑定公网IP（云服务器防火墙控制访问），不要只绑 localhost。

## 删除项目流程

1. 杀掉服务器进程：`kill $(lsof -ti:<端口>)`
2. 删除项目目录：`rm -rf ~/Desktop/hermes/<项目名>`
3. 从 `PROJECTS` 列表删掉对应条目
4. 重新运行 `python3 build_hub.py`

## 导航页结构

| 区域 | 内容 |
|:----|:----|
| **HTML 项目** | 带图标+描述+端口标签+标签的卡片，点击跳转 `http://IP:PORT` |
| **外部服务** | 轻量链接，指向其他端口上的Web服务（FastAPI/看板等） |
| **页脚** | 提示文案「新增项目 → 编辑 build_hub.py 加一行即可」 |

## 常用验证命令

```bash
# 验证所有服务器运行状态
for p in <端口列表>; do
  lsof -ti:$p > /dev/null 2>&1 && echo "$p ✅" || echo "$p ❌"
done
```bash
# 验证导航页是否更新
grep -c '工具' ~/Desktop/hermes/hermes-hub/index.html
```

**验证卡片别 grep 结构前缀** ⚠️：卡片实际格式是 `class="card" onclick="toggleCard(this)" data-tags="..."`（中间有 onclick），grep `'card data-tags'` 会返回 0 误判"没更新"。直接 grep 卡片名称最稳：

```bash
# 正确：grep 卡片中文名（出现≥1 次即已更新）
curl -s http://127.0.0.1:<端口>/ | grep -o '<卡片名>' | sort | uniq -c
# 计数验证：grep -c 'class="card"' index.html
```

## 工具箱 vs 导航中心

| | 方法论工具箱 | 项目导航中心 |
|:--|:-----------|:-----------|
| 端口 | 8900 | 8895 |
| 数据源 | Hermes skills_list | VPS上运行的HTML项目 |
| 更新方式 | 编辑build_toolbox.py | 编辑build_hub.py |
| 用途 | 展示所有可调用工具 | 展示所有可访问网页 |

两个脚本共用相同的「数据列表+渲染→HTML」模式。

### 工具箱卡片外链（url 字段）

`build_toolbox.py` 的 SKILLS_DATA 条目支持可选 `"url": "http://IP:PORT/"` 字段。带该字段的卡片展开后自动渲染「打开页面 →」链接按钮（新标签页打开，`event.stopPropagation()` 防止误触卡片展开/收起）。

**用法：** 某个工具方法论已有独立落地页面（如红蓝分析法 → 8920），在对应条目加 `"url"` 字段即可打通，无需改渲染逻辑：

```python
{"cat":"🚀 创业立项","name":"红蓝验证器","desc":"...","key":"project-recommendation-workflow",
 "path":"productivity/project-recommendation-workflow","url":"http://43.138.221.174:8920/"},
```

**重要：** 重跑 `python3 build_toolbox.py` 后**不需要重启** 8900 的 http.server——静态文件按请求实时读取，重新生成 index.html 立即生效。验证：`grep -n "card-link\|<端口>" index.html`。

**⚠️ 卡片链接是手写死的话，改数据源不生效（2026-08 实测）：** 如果工具箱 index.html 里的 `<a class="card-link" href="http://IP:PORT/">` 是**手工写死的**（不是 build_toolbox.py 渲染的），那加新落地页后卡片不会自动带链接。症状：卡片展开没有「打开页面 →」按钮。修复：直接在 index.html 里给对应卡片的 `card-meta` 后 patch 插入 `<a class="card-link" ...>打开页面 →</a>`（红蓝8920有、六分身8921/市场调研8922/行业调研8923 曾漏，就是这个坑）。

## 常见坑

### 0. 重建前必须备份原版 index.html ⚠️ 血泪教训

**教训（2026-08实测）：** 加了新项目后直接跑 `python3 build_hub.py`，把线上正在用的**深紫科技风** index.html 覆盖成了模板里的 **Forty 风格**（深蓝硬卡片），用户直接说「不好看，还是原来的好看」。没有备份=无法恢复，只能从 skill 模板反推重做。

**规则：**
1. **任何重建前先备份**：`cp index.html index.html.bak_$(date +%s)`（或先 git init 提交一次）
2. 确认当前线上 index.html 的样式版本，**别假设 build_hub.py 生成的样式 = 用户喜欢的样式**——线上可能被手工改过、或模板版本已过期
3. 改 build_hub.py 前先读完整文件 + 读 references 模板，判断哪个才是当前线上版本

### 0.1 导航页用户偏好（已定稿）

用户喜欢的导航 Hub 风格是**深紫科技风**，不是 Forty 深蓝硬卡片：
- 背景：深黑 `#0a0a0f` + **紫色网络节点 Canvas 粒子**（70节点+连线，粒子要明显不能太淡）
- 标题：紫色渐变 `linear-gradient(135deg,#a78bfa,#6c5ce7,#3b82f6)` 文字
- 卡片：圆角玻璃卡片 + 左侧 hover 发光条 + hover 上浮阴影
- 排版：**按分类分组**（🌐页面/🆕新项目/🔗外部服务），每类下卡片**多列网格**（`grid-template-columns:repeat(auto-fill,minmax(320px,1fr))`），**不要竖排直排**（用户原话「直排的不好看」）
- 分类标题带渐变分隔线（`::after` 横向渐变线）

### 0.2 模板版本说明

`references/build_hub_template.py` 是深紫科技风模板（竖排列表版）。当前生产版 ~/Desktop/hermes/hermes-hub/build_hub.py 已是**分类网格版**（深紫科技+分类+多列网格）。新项目直接参考生产版 build_hub.py 的 PROJECTS 结构（带 cat 字段的分组列表），**不要用 references 模板直接覆盖**。

### 1. 端口被占用（OSError: Address already in use）

`python3 -m http.server` 绑定时如果端口被占会报错。先用 `lsof -ti:<端口>` 检查。

**解法：** 换一个端口，或者杀掉占用进程。

### 2. 背景进程退出后服务停掉

用 `terminal(background=true)` 启动的服务器如果中途退出（如端口冲突），服务就挂了。启动后立即验证：

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:<端口>/
```

返回 200 才确认上线。

### 3. IP硬编码

导航页链接写的是 `http://43.138.221.174:<端口>/` — 如果服务器IP变更需要全部更新。目前手动维护。

### 4. 改版已有项目前必须查部署方式 ⚠️

用户报"页面没反应"时，先查该端口现有部署是**纯静态还是 API 服务**。实测教训：红蓝页 8920 原本是 `python3 -m http.server` 纯静态服务，改版加了「输入想法→调 API」后点击没反应——静态服务器不认 POST，fetch 无人处理。

```bash
ss -tlnp | grep <端口>          # 找监听进程 PID
readlink /proc/<PID>/cwd        # 确认服务目录
curl -s -X POST http://127.0.0.1:<端口>/api/analyze -H "Content-Type: application/json" -d '{"idea":"test"}' | head -c 200
# 返回 404/501/405 → 纯静态，需换成 FastAPI 服务
```

改版前先确认，别假设端口上跑的是新版。

### 6. 网关重启会杀光所有 background http.server ⚠️ 批量恢复流程

**教训（2026-08实测）：** Hermes 网关重启/会话结束后，所有用 `terminal(background=true)` 启动的 `python3 -m http.server` 进程会**全部被带走**（同批启动的子进程随会话生命周期结束）。实测 15 个端口只剩 4 个活着（8915/8931/8895/8930），导航页所有卡片点击全挂——用户报「每个项目的跳转链接都没有了」。

**诊断命令（先扫全端口）：**
```bash
for p in 8000 8897 8900 8899 8894 8910 8911 8912 8913 8914 8915 8916 8917 8931 8895; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:$p/" 2>/dev/null)
  echo "$p -> $code"
done
# 000 = 死了；404 = 活着但根路径无内容（如API服务，正常）
```

**批量恢复：** 每个项目目录一个 `terminal(background=true)` 启动（一次性并行发多个）：
```bash
cd ~/Desktop/hermes/<项目目录> && python3 -m http.server <端口> --bind 0.0.0.0
```
项目目录→端口映射（实测生产）：
- 8900=toolbox, 8899=birthday-zeying, 8894=portfolio, 8910=cases-wall, 8911=product-dashboard, 8912=quant-board, 8913=game-zeying, 8914=fortune-wheel, 8915=pixel-gallery, 8916=particle-card, 8917=server-status, 8931=mecha3d/web

**非纯静态服务的特殊处理：**
- **8000 = AI爆款主图生成器**（Docker Compose 栈，~/backend），`docker compose up -d`；compose 端口映射是 **8080:8000**（对外仍 8000 需 socat 转发：`socat TCP-LISTEN:8000,fork,reuseaddr TCP:127.0.0.1:8080`）
- **8002 = 服小助AI客服**（~/Desktop/hermes/ai_cs_package，独立 venv，`python -m app.main`，DeepSeek 驱动）——不是 8000！8000 是爆款主图生成器，导航链接曾错误指向 8000 显示 JSON API
- **Hermes 网关 8897 实际跑在 9119**（`hermes serve --port 9119`，仅绑 127.0.0.1）
- **8897 反代用 nginx 不要用 socat** ⚠️：socat 是纯 TCP 转发不改写 Host header，hermes 网关校验 Host 会返回 `Invalid Host header. Dashboard requests must use the hostname...` 400。正确做法是 nginx 反代并改写 Host：
```nginx
# /etc/nginx/sites-enabled/hermes-gateway
server {
    listen 8897;
    server_name 43.138.221.174;
    location / {
        proxy_pass http://127.0.0.1:9119;
        proxy_set_header Host 127.0.0.1:9119;   # 关键：改写 Host 通过校验
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }
}
```
- 服小助前端如果 HTTPS 页面调 HTTP 接口会 **mixed content 拦截**（浏览器 "Failed to fetch"）——前端 API 地址必须用相对路径 `const API = '';` 而不是硬编码 `http://IP`（实测 midage.icu 踩坑）。⚠️ 修完 JS 后 **nginx 静态缓存（expires 7d）会让用户端继续拿到旧文件**——浏览器强刷/重开仍报错。验证/临时绕过：URL 加版本参数 `?v=20260801`；用户端最终靠 `sudo nginx -s reload` + 浏览器硬刷。排查时先确认浏览器实际执行的 JS 内容（browser_console 读 script 文本），别信"我改了文件"——可能缓存里还是旧的。

**腾讯云轻量安全组**：新端口公网访问要在控制台防火墙加规则（如 8002），本地 200 但公网 000 = 安全组没开。

**根治建议：** 全部服务做开机自启/保活（systemd 或 supervisor），否则每次网关重启都要手动恢复。恢复后记得重新跑 `python3 build_hub.py` 刷新在线统计（alive() 会重新探测）。

**保活系统已上线（2026-08）：** `scripts/keepalive.sh` 是生产版保活脚本（已部署到 ~/Desktop/hermes/scripts/keepalive.sh + crontab `*/3 * * * *` + `@reboot`）。新机器部署时直接复制该脚本，改 STATIC_PROJECTS/FASTAPI_PROJECTS/SOCAT_PROJECTS 三个数组即可。crontab 配置：
```
*/3 * * * * /home/ubuntu/Desktop/hermes/scripts/keepalive.sh start >> /var/log/keepalive.log 2>&1
@reboot /home/ubuntu/Desktop/hermes/scripts/keepalive.sh start >> /var/log/keepalive.log 2>&1
```
验证幂等性：全在线时再跑一次 `start`，日志应 0 次"启动"（全部跳过）。

### 5. 长 HTML 修改用 Python 精确替换

patch 工具对**长 old_string + 页面重复结构**（卡片网格、重复的 card 块）会模糊匹配误报（"Found 7 matches"）。此时改用 Python 精确替换：

```python
s = open('index.html', encoding='utf-8').read()
assert s.count(old) == 1, f"期望1次，实际{s.count(old)}次"
s = s.replace(old, new)
open('index.html', 'w', encoding='utf-8').write(s)
```

多个卡片移动（剪切→插入）分两步：先插到目标位置，再删原位置（用正则 `[\s\S]*?` + 前瞻 `(?=<div class="card"...)` 匹配块）。

## 参考文件

- `references/build_hub_template.py` — 完整可用的导航中心构建脚本（当前生产版）
