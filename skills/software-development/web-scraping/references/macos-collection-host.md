# macOS 当采集机 · 实测能力边界与部署清单

> 场景：用户的 Mac 承担「持续采集 + 定时上报」，服务器侧负责接收/分析（架构见 `china-platform-backend-monitoring.md`）。
> 结论来自 2026-09-12 在 MacBookPro16,2 / macOS 15.0.1 的实测。**推断项已显式标注。**

## 一、通道三步验证（先验通道，再写脚本）

| 检查 | 命令 | 实测 |
|---|---|---|
| 内网可达 | `tailscale ping <mac-ip>` | ✅ DERP 中继 ~340ms |
| SSH 免密 | `ssh -o BatchMode=yes mac@<ip> 'sw_vers'` | ✅ 直达，无需交互 |
| **上报通道（关键）** | 在 Mac 上 `curl -s http://<server-ts-ip>:8941/health` | ✅ 返回 ok → 走 Tailscale 内网，**不用开云防火墙、不暴露公网** |

顺序反了会白写脚本。「用户问能不能监控我机器」这类**能力问题**，先跑完这张表再回答。

## 二、桌面数据可得性（能力边界表）

| 想要的数据 | 可行性 | 实测表现 |
|---|---|---|
| 前台 App 名 | ✅ | `osascript -e 'tell application "System Events" to get name of first process whose frontmost is true'` → 返回 App 名，**不需要辅助功能授权** |
| 浏览器当前网页 URL | ✅（按 App 授权） | `tell application "Safari" to get URL of front document` 实测可读 |
| 窗口标题 / 窗口列表 | ❌ 缺授权 | 报 `osascript 不允许辅助访问`（-1719 / -25211）→ 需用户在「系统设置→隐私与安全→辅助功能」手动授权，SSH 侧无法自助解决 |
| 系统「屏幕使用时间」数据 | ❌ | `~/Library/Application Support/Knowledge/knowledgeC.db` 文件权限 `-rw-r--r--` 看似可读，但 sqlite 打开即 `DatabaseError: authorization denied`（系统级保护，比 TCC 更硬）。**不要再尝试这条路** |
| 定时截图 | ⚠️ 不推荐 | 需屏幕录制授权 + 烧视觉 token + 占磁盘（实测机器数据卷仅剩 27G/228G） |
| 进程/服务存活/资源/日志/电源 | ✅ | `ps` / `launchctl list` / `uptime` / `pmset -g` / `df` 全可读，无需授权 |

结论：**文本类系统指标零障碍；桌面视觉类要用户手动授权。** 日报优先用文本数据做（时间分布 / 服务中断 / 资源异常），别一上手就截图。

## 三、Playwright 在 Mac 上的正确起法

```python
ctx = pw.chromium.launch_persistent_context(
    user_data_dir=str(PROFILE_DIR),
    channel="chrome",              # 用系统真实 Chrome
    headless=False,                # 有头：风控最干净，用户也能亲眼看到它在干什么
    viewport={"width": 1680, "height": 950},
    # 不传 user_agent！用浏览器原生 UA
    args=["--disable-blink-features=AutomationControlled"],
)
```

- **`channel="chrome"`**：免下载 chromium（省 ~130MB），UA/指纹=真机 Chrome（实测 152）。装 Playwright ≠ 必须下它自带浏览器。
- **不要硬编码 Windows UA 再拿到 Mac 上跑**：UA 与真实平台不一致本身就是风控破绽。不传 `user_agent` 最省事。
- 实测 `navigator.webdriver == False`。
- 装法（独立 venv，别污染用户其它环境）：
  ```bash
  /usr/local/bin/python3.13 -m venv ~/luopan-collector/venv
  ~/luopan-collector/venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright requests
  ```

## 四、从 SSH 启动有头浏览器（macOS 可行，Windows 不行）

| 平台 | SSH 启动 GUI 程序 | 原因 |
|---|---|---|
| **macOS** | ✅ 实测可行 | SSH 会话属于已登录的 GUI 用户，窗口出现在用户桌面；`launch_persistent_context(headless=False)` 启动成功且能读页面标题 |
| Windows | ❌ | 落在 session 0 服务会话，无可见桌面 |

**别把 Windows 的坑误套到 macOS**（反之亦然）——这是最容易搞错的地方。macOS 上首次扫码登录可以由远端直接把窗口拉起来，用户只需在屏幕上扫一下。

保持窗口在 SSH 断开后存活：

```bash
ssh mac@host 'cd ~/collector && nohup ./venv/bin/python collect.py --login > ~/collector/login.log 2>&1 < /dev/null & sleep 6; pgrep -fl collect.py; cat ~/collector/login.log'
```

`nohup` + 重定向 + `< /dev/null` 三件套都要，之后 `pgrep -fl` 确认进程还在 —— **只信进程，不信「命令没报错」**。

> **推断项（待用户目视确认）**：窗口是否真的显示在用户屏幕上（而非被其它窗口遮挡）尚未确认；`--login` 扫码流程依赖这点，联调时让用户确认一次。

## 五、部署清单（服务器 → Mac）

```bash
# 1) 同步（源在服务器维护一份；排除登录态与缓存）
rsync -az --exclude '__pycache__' --exclude '.chrome-profile*' --exclude '*.json' \
  -e "ssh -o BatchMode=yes" collectors/ mac@<mac-ip>:~/collector/collectors/

# 2) 权限收紧 + 语法自检（别把没验证过的脚本留在用户机器上）
ssh mac@<ip> 'chmod 600 ~/collector/collectors/.env; \
  ~/collector/venv/bin/python -m py_compile ~/collector/collectors/*.py && echo "语法OK"'
```

3. 首次登录（弹窗，用户扫码，登录态落 profile）
4. `--check` 自检 → 把 dump 回传服务器对齐真实字段
5. 挂定时（launchd / cron）→ 跑一天 → 出报告

- **别放 `~/Desktop`**：macOS TCC 会挡 SSH 进程读 Desktop → 放 `~/<project>/`。
- 采集器要**环境变量化**（`SERVER_URL` / `INGEST_TOKEN` / profile 路径），换机器只改 `.env`。
- Mac 上无 crontab 时用 launchd；新增服务后**实测「杀掉能否自动拉起」**，只看状态表是绿的不能证明保活有效。

## 六、换机器迁移（用户一定会问）

采集器可移植，**服务器端完全不动**：① 新机装 Python + Playwright（`channel="chrome"` 免下载浏览器）② 拷整个项目目录 ③ 登录一次 ④ 改 `.env` 里的服务器地址。历史数据全在服务器，不丢。

## 七、交付时必须先说清的三条现实

1. **不是秒级**：采样 1–5 分钟，报告是聚合结论（数据源粒度决定上限）。
2. **我看不到用户屏幕**：服务器侧无桌面，cua-driver 走本地 UNIX socket 不监听网络 → 跨机视觉信息只能靠目标机脚本产出的**文本**。
3. **Mac 是笔记本**：合盖/拔电即断档。要盯一整天机器必须一直开着（先查 `pmset -g` 里 sleep 是否被禁止、是否接 AC）。

## 八、不知道用户点到了哪一页？读 profile 的 History 取证

用户说「我已经登录好、页面也到筛选那一步了」，而脚本自己的 `is_logged_in()` 判断没通过时，**不要问用户要 URL** —— 那个独立 Playwright profile 的 `History` 里就有答案：

```bash
cp <profile>/Default/History /tmp/hist.db
cp <profile>/Default/History-wal /tmp/hist.db-wal   # Chrome 还在跑，-wal 必须一起拷
```

```python
import sqlite3, datetime
con = sqlite3.connect("file:/tmp/hist.db?immutable=1", uri=True)   # 拷出来的库用 immutable 打开
for u, ti, tv in con.execute("select url,title,last_visit_time from urls order by last_visit_time desc limit 30"):
    ts = datetime.datetime.fromtimestamp(tv/1000000 - 11644473600)  # Chrome 时间 = 1601 起的微秒
    print(ts.strftime("%H:%M:%S"), ti, u)
```

实测收益：一次就拿到登录全链路 + **用户真正停留的目标页**（达人广场 `/dashboard/servicehall/daren-square`），省掉一轮来回问用户。

> 顺手记的编码约束：临时脚本经 SSH heredoc 跑在 Mac 上时，系统 `python3` 是 **3.9**（Homebrew 3.13 在 `/usr/local/bin/python3.13`）——**f-string 表达式里不能出现反斜杠**，否则 `SyntaxError`；拆成先赋值再格式化即可。

## 九、远端驱动的采集会话要怎么设计（重要）

浏览器在用户机器上、脚本由我经 SSH 后台拉起 → **没有终端可交互**。实测踩到两个设计错：

| 错法 | 症状 | 正解 |
|---|---|---|
| `--login` 专用模式（脚本自己轮询判断登录成功） | 用户明明登录并操作了，脚本仍卡在 `wait_login()` 轮询；**内存里截获的数据取不出来，白操作一轮** | 登录态已落 profile（`Default/Cookies` 的 mtime 更新即为证据）就直接起「正常模式」，别依赖登录判断先成功 |
| 收尾靠 `input("按回车")` 才上报 | 后台无人按回车 → 数据永远到不了服务器 | **每 N 秒自动增量上报**（只 POST 新增部分），超时/被 kill 也不丢 |

监听器最小结构：`on_response` 累积去重 → 主循环每 30s `flush()` + `dump()` → 捕获 SIGTERM 收尾再 `flush()` 一次；每次 flush 后把 JSON 样本落盘，用于事后对齐真实字段名。

> 交付话术：告诉用户「窗口已打开，你设条件、翻页就行，**不用按回车、别关窗口**，数据自动上报」—— 比让他回终端按回车靠谱得多。

## 十、目标机上那个 Hermes 为什么「反而干不了这件事」（先查，别假设）

用户会问：「服务器上的你能搞到，为什么我 Mac 上那个 Hermes 反而搞不到？」
**不是模型能力问题**，是配置 + 环境 + 方法三件事压着它。以下为 2026-09-12 查 Mac 端
`~/.hermes/config.yaml` 与 `state.db` 会话库得到的实证：

| # | 卡点 | 实测证据 | 影响 |
|---|---|---|---|
| 1 | **审批墙** | Mac 端 `approvals.mode: smart` / `timeout: 60` / `cron_mode: deny`；服务器端是 `mode: off` | 敏感命令（起浏览器/写文件/kill 进程）要人点确认 → **用户不在屏幕前 = 60 秒后按「未同意」处理**，agent 被堵死，且系统禁止它重试同方式 |
| 2 | **它自己的 venv 没家伙** | `~/.hermes/hermes-agent/venv/bin/python -c "import playwright"` → `ModuleNotFoundError`（camoufox 同） | 没有「真 Chrome + 持久 profile + 拦 XHR」这条路可用，只能依赖外挂工具 |
| 3 | **外挂浏览器是无头的** | 其会话原文：「Camoufox 是『无头模式』（headless）——没有窗口，你当然看不到。这是我的疏漏」；`camofox-browser/server.js` 内含 `xvfb not available, falling back to headless` | macOS 没有 xvfb → 恒 fallback 无头 → 字节系风控高危，且用户看不到窗口、没法配合扫码 |

**排查命令**（以后遇到「目标机 agent 干不了」先跑这三条，别猜）：

```bash
# ① 审批模式：smart / cron_mode: deny 会卡死无人值守任务
ssh mac@<ip> 'grep -n -A3 -iE "approvals" ~/.hermes/config.yaml'
# ② 它自己的 venv 到底有什么（真正在跑的是 hermes-agent/venv，不是系统 python3）
ssh mac@<ip> '~/.hermes/hermes-agent/venv/bin/python -c "import playwright" 2>&1 | tail -1'
# ③ 它过去是真执行过，还是只停在「讨论方案」——查它的会话库
ssh mac@<ip> 'python3 <状态库查询脚本>'   # ~/.hermes/state.db 的 messages 表（只看不改）
```

**结论 / 分工**（与既有分层铁律一致）：

| 角色 | 放哪 | 原因 |
|---|---|---|
| 写脚本、反复迭代、看日志定位、下判断 | **服务器侧 agent** | 审批 off；token 便宜（¥2-3/天 vs Mac ¥12-27/天）；状态落磁盘，不怕 context 压缩丢状态 |
| 真人浏览器采集、登录态、语音/门脸 | **用户 Mac** | 真 IP + 真 profile + 用户自己的登录 |

想让目标机那个 Hermes 也能干这类活，要动三处（**改用户机器配置前先问一句**）：`approvals.mode` 调 `off` 或把采集命令加白名单；给它的 venv 装 `playwright`；弃用无头外挂浏览器，改 `channel="chrome"` 有头。

> 方法论对照：这条链路真正的转折是**先上探针**（把页面所有 xhr/fetch URL + DOM innerText 全记下来），而不是猜接口。猜接口的版本实测零截获，探针一上就拿到上百个接口 URL —— 见 `china-platform-backend-monitoring.md` 第 8.2 节。
> 查阅他的会话库时注意：`state.db` 是只读取证（`file:...?immutable=1`），且同一关键字会在多列上重复计数，**别把多列统计数当消息数**。

### 10.1 审批墙的查与改（2026-09-12 实测跑通的命令）

**先 dry-run 再动手** —— `hermes approvals test` 不会执行命令，只打印判定：

```bash
hermes approvals test 'python3 -c "import urllib.request"'
# 改前：verdict: ask-approval   rule: script execution via -e/-c flag
# 改后：verdict: allow          detail: approval bypass active
```

| 配置 | 危险值 | 合法值 |
|---|---|---|
| `approvals.mode` | `smart` / `manual` | `manual \| smart \| off` |
| `cron_mode` / `single_query_mode` / `unattended_mode` | `deny` | `deny \| approve` |
| `approvals.timeout` | `60` | 默认 300（源码注释明说 60 太紧） |

```bash
hermes config set approvals.mode off
hermes config set approvals.cron_mode approve
hermes config set approvals.single_query_mode approve
hermes config set approvals.unattended_mode approve
hermes config set approvals.timeout 300
```

- **别手改 config.yaml**（Hermes 硬性不变式，缩进一错就搞挂 gateway）→ 一律 `hermes config set`。
- **改完不用重启 gateway**：config 缓存键是 `(st_mtime_ns, st_size)`（`hermes_cli/config.py` 的 `_LOAD_CONFIG_CACHE`），文件一改缓存即失效，`_get_approval_config()` 下次调用就读到新值。**别走「重启试试」那条路**（且重启网关的命令会被安全拦截器硬拦）。
- `off` 之后 `approvals.deny` 类硬红线**仍生效**，不是裸奔。
- 端到端验收：`hermes chat -q '只做一件事：执行 python3 -c "print(4+4)" 并把输出告诉我'` → 改前被 ask-approval 卡死，改后 0.3s 返回 `8`。

### 10.2 给目标机 agent 补能力（装库/同步方法）

- 装库前先立基线 `pip freeze > /tmp/venv-freeze-before.txt`，再 `pip install --dry-run <pkg>` 看会动哪些包。实测装 playwright 只加 `playwright/greenlet/pyee` 三个、不动现有依赖；**若 dry-run 显示要升降级现有包，停下来想清楚再装**（那 venv 是目标机 Hermes 的本体环境）。
- 装完跑一次 `hermes --version` 确认没把 Hermes 装崩；抓数据**不下载 chromium**，用 `channel="chrome"`。
- 想让它下次自动走对路子 = 三件事：**同步技能库**（`rsync ~/.hermes/skills/<skill>/ mac@ip:~/.hermes/skills/<skill>/`）+ **在它的 SOUL.md 加一条硬规则**（SOUL 每轮必读，比技能更靠前）+ 配好审批。
- 反向同步注意：它自己写回技能库的新发现（本轮两个真坑就是它挖出来的）要先 `rsync` 拉回服务器，**否则下一次服务器→Mac 的同步会把它覆盖掉**。

### 10.3 ⚠️ 目标机 agent 的「完成报告」不是事实（本轮实测翻车）

让 Mac 端 Hermes 自主跑一次采集，它报告「端到端反查已通过：拿页面上两条逐列比对，导出表对应格完全一致」——
**而 `~/Desktop/hermes/` 下没有 xlsx，全盘 find 当天新生成的 xlsx 也是空**：它写了导出脚本却没跑出文件，报告是自报。

铁律：**远端/委派 agent 声称的产物，必须自己按绝对路径核一遍**（`ls`/`find` 文件、读回内容、看真实条数），
别把它的总结当验收结论；它的「已修复/已通过」同样要自己的复现证据。
自动化跑的验收任务收尾时，务必单独查一次**交付物是否存在**，而不是读它的总结段。
