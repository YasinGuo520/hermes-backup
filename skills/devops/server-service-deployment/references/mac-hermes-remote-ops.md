# Mac Hermes 远程运维修复配方（2026-09-06 实测）

**触发**：用户「修下 Mac 上的 Hermes」。Mac = 用户的本地备份机（Tailscale 100.80.117.5，SSH 用户 mac@），跑独立 Hermes 实例 + launchd 托管。服务器 Hermes 可 SSH 远程修，但**防自杀拦截照样作用于远程 gateway 操作**（见 SKILL.md「变通方案四」——操作写脚本 scp 过去 `bash` 执行）。

## 诊断顺序（先症状分类，别乱修）

1. **进程在不在**：`pgrep -fl "hermes_cli.main gateway"`；不在 → 查 launchd：`launchctl list | grep hermes`
2. **launchd 拉不起**：`launchctl list` 显示 `last exit code = 1` → 启动即崩。**先手动前台跑抓 traceback**（别反复 kickstart）：
   ```bash
   cd ~/.hermes && HERMES_HOME=/Users/mac/.hermes \
     /Users/mac/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace 2>&1 | head -30
   ```
   ⚠️ Mac 无 `timeout` 命令（zsh: command not found）——用后台 `&` + sleep + kill 抓日志。
3. **平台连接失败 ≠ Hermes 坏**：Mac 配置的平台（telegram/discord 等）在国内都要翻墙。`grep -E "connect timed out|NetworkError|httpx.ConnectError" ~/.hermes/logs/gateway.log` 全是网络层 → 查代理（见下）。

## 故障：venv 空壳 / 模块缺失（本次根因）

**症状**：gateway 崩循环（exit 1）。手动跑报 `ModuleNotFoundError: No module named 'yaml'` 或 `No module named 'hermes_cli'`。
**根因**：venv 几乎全空（`pip list | wc -l` 只有 4 个包）+ editable 安装的 .pth 关联丢失。

**修复两步：**
```bash
# 1. 补 editable 关联（.pth 指向源码树）
SP=$(ls -d /Users/mac/.hermes/hermes-agent/venv/lib/python*/site-packages | head -1)
echo "/Users/mac/.hermes/hermes-agent" > "$SP/hermes-src.pth"
# 2. 重装依赖（清华镜像，Mac 上 pip 直连 pypi 不稳）
PIP=/Users/mac/.hermes/hermes-agent/venv/bin/pip
$PIP install -e /Users/mac/.hermes/hermes-agent -i https://pypi.tuna.tsinghua.edu.cn/simple --no-input
# 验证
/Users/mac/.hermes/hermes-agent/venv/bin/python -c "import yaml, hermes_cli; print('OK')"
```
注意 venv 可能是 python3.13（路径 `lib/python3.13/site-packages`），别假设 3.11。

## 故障：key 不生效（改完 .env 没重启）

gateway 进程 env 是**启动时**加载的——`ps -o lstart -p <pid>` 与 `.env` 修改时间对比，gateway 早于 .env = 必须重启。重启走 launchd：
```bash
launchctl kickstart gui/$(id -u)/ai.hermes.gateway   # 用脚本文件方式执行（见 SKILL.md 变通方案四）
```
**⚠️ Mac .env 曾出现垃圾值**：第一行 `DEEPSEEK_API_KEY="hermes setup model"`（疑似某次 `hermes setup model` 把字面量写进 .env）——python 改该行，别 sed（值含引号）。config.yaml 主模型段用 `key_env: DEEPSEEK_API_KEY` 引用时，key 值以 .env 为准。

## Mac Hermes 平台网络（telegram/discord）

- Mac 用 Clash Verge（进程 `clash-verge` + `verge-mihomo`，mixed-port 通常 **7897**）。
- telegram 断连排查：直连必 000（被墙）；经代理 `curl -x http://127.0.0.1:7897 https://api.telegram.org` 也 000 → **节点全挂**（对照测 google：也 000 = 节点问题不是规则问题）。Clash 进程在跑 ≠ 代理通——需用户在 Clash Verge GUI 选节点/更新订阅，代理一通 gateway 自动重连 telegram，不用重启。
- 09:52 通 / 10:06 断这类时间线 = 节点中途失效，不是 Hermes 配置漂移。
