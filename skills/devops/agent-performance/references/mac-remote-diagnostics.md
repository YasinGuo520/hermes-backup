# Mac Hermes 远程诊断清单

当用户反馈电脑端（本地 Mac 实例）的 Hermes 出现问题时，用于远程或脚本式诊断。

## 适用场景

- 用户说「电脑端 Hermes 变傻了/不深入/没思考就行动」
- 用户说「Mac 上的 Hermes 跟服务器上的不一样」
- 需要判断 Mac 实例的配置/SOUL/模型是否合理

## 必查三连（远程用户无SSH时）

让用户在 Mac 终端跑：

```bash
# 1. 检查 Hermes 存活
ps aux | grep -i "hermes\|gateway" | grep -v grep

# 2. 检查 SOUL.md（#1 行为异常原因）
cat ~/.hermes/SOUL.md | head -30

# 3. 检查模型配置
grep -A5 'default:' ~/.hermes/config.yaml | head -10
```

## 多实例 SOUL 设计原则

不同用途的 Hermes 实例需要**根本不同的 SOUL.md**：

| 实例类型 | 角色 | SOUL.md 特点 | 默认倾向 |
|---------|------|-------------|---------|
| 服务器 (24h 在线) | 副驾驶/执行者 | 行动优先、先做再说、推着走 | 先执行后思考 |
| Mac 本地 (坐桌前用) | 助手/创作工具 | 深度推理优先、先想后动、质疑再信 | 先思考后执行 |

**致命错误：** 把服务器 SOUL.md 直接复制到 Mac 端。服务器版强调「先做再说」「立刻执行」，Mac 端用了会变得不思考就冲。

**修改要点：**
- 服务器版 SOUL：「先做再说」「最小行动单元」「推着走」
- Mac 版 SOUL：「先想后动」「深度优先」「问清楚再干」
- Mac 版必须加「避免不思考直接搜索/命令/写代码」

## 完整诊断脚本（让用户跑一次）

```bash
cat <<'DIAG' > /tmp/mac-diag.sh
#!/bin/bash
echo "=== 1. 系统 ===" && sw_vers 2>/dev/null && echo "Arch: $(uname -m)"
echo "=== 2. Hermes 进程 ===" && ps aux | grep -i "hermes\|gateway\|lightclaw" | grep -v grep
echo "=== 3. Python ===" && which python3 && python3 --version
echo "=== 4. SOUL.md ===" && cat ~/.hermes/SOUL.md 2>/dev/null || echo "no SOUL.md"
echo "=== 5. 端口监听 ===" && lsof -iTCP -sTCP:LISTEN -P 2>/dev/null | head -15
echo "=== 6. 磁盘 ===" && df -h / | tail -1
echo "=== 7. 网络 ===" && curl -so /dev/null -w "github: %{http_code} (%{time_total}s)\n" https://github.com && curl -so /dev/null -w "feishu: %{http_code} (%{time_total}s)\n" https://www.feishu.cn -x '' --connect-timeout 5
echo "=== DONE ==="
DIAG
bash /tmp/mac-diag.sh
```

## 典型问题及修复

### 症状：回答浅，不思考就直接搜/写代码
**诊断：** `cat ~/.hermes/SOUL.md` — 是否包含「先做再说」「立刻做」等服务器版指令
**修复：** 替换为思考优先 SOUL，重启 Hermes

### 症状：搜索慢或搜不到
**诊断：** `grep -i "timeout\|quota\|error" ~/.hermes/logs/agent.log | tail -5`
**修复：** 检查搜索配置（AnySearch 额度 / DuckDuckGo 被限流）

### 症状：飞书消息收不到
**诊断：** `ps aux | grep gateway` 是否在跑
**修复：** 重启 Hermes 或重连飞书

## Tailscale 远程管理

如需 SSH 直接操控 Mac，推荐 Tailscale 组网（免费，无需公网 IP）：

1. Mac 安装 Tailscale → 登录 → 开远程登录（系统设置→通用→共享→远程登录）
2. 服务器安装 tailscale → `sudo tailscale up` → 同账号登录
3. 验证：服务器上 `tailscale status` 看到 Mac 的 IP
4. 测试：`ssh mac@<tailscale-ip>` 确认可达

⚠️ App Store 版 Tailscale 不支持 SSH 功能，需从官网下载。
