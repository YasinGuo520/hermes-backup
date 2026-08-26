# 服务器翻墙：Mac Clash 代理隧道（已弃用 2026-08-26）

> ⚠️ **结论先行：本方案已被实测推翻并弃用。** 服务器翻墙**不再借 Mac 代理**。
> 终案：git remote 整体切 gitcode 镜像（fetch+push），装依赖走腾讯内网源。

## 为什么弃用（实测证据）

Mac 的 **Clash Verge (mihomo) 实际走 TUN 模式**（虚拟网卡接管流量），**不监听 7897 端口**——虽然 Mac 系统代理设置（networksetup）显示 Server 127.0.0.1:7897，但 `lsof -iTCP:7897 -sTCP:LISTEN` 无输出（只有 clash-verge GUI 进程监听 33331 控制端口）。

因此：
1. 服务器 SSH 隧道（17897→Mac 7897）虽然建立（SSH ESTABLISHED、17897 在监听），但**转发到空端口**
2. 经隧道访问 Google/GitHub/YouTube 全部 000
3. Mac 本机测 `curl -sx http://127.0.0.1:7897` 也是 000

**"Mac 能翻墙" ≠ "Mac 提供代理端口"** —— TUN 模式只对 Mac 本机生效，服务器借不到。

## 曾尝试的配置路径（已全部撤回）

```bash
# ① 曾建的隧道（已杀）
ssh -L 17897:127.0.0.1:7897 -N -f -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes mac@100.80.117.5

# ② 曾配的 git 全局代理（已清）
git config --global http.proxy http://127.0.0.1:17897
git config --global https.proxy http://127.0.0.1:17897

# ③ 曾加的 keepalive start_tunnel()（已从 keepalive.sh 移除）
# ④ 曾加的 .bashrc proxy-on/proxy-off/proxy-test 函数（已从 .bashrc 移除）
```

## 弃用后的正确方案（当前生效）

```bash
# 1. git remote 整体切 gitcode 镜像（fetch + push 都改）
cd ~/.hermes/hermes-agent
git remote set-url origin https://gitcode.com/GitHub_Trending/he/hermes-agent.git
git remote set-url --push origin https://gitcode.com/GitHub_Trending/he/hermes-agent.git
# 验证：git remote -v 两条都应指向 gitcode

# 2. 装依赖：unset 代理 + 腾讯内网源（pip.conf 已配）
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
venv/bin/pip3.11 install -e ".[all]"
```

| 资源 | 直连可达性（腾讯云实测） |
|------|--------------------------|
| gitcode.com | ✅ 200 |
| mirrors.tencentyun.com（内网源） | ✅ 200 |
| github.com | ❌ 被墙（curl 可能通但 git 端点 reset） |

## 踩坑记录（供未来参考）

### 坑1：.bashrc 非交互 shell 不加载函数 → `command not found`

Ubuntu 默认 `.bashrc` 开头有：
```bash
case $- in
    *i*) ;;
      *) return;;
esac
```
**非交互**（`bash -c`、cron、python subprocess）source .bashrc 直接 return，函数定义不生效。
测试函数必须 `bash -i -c 'source ~/.bashrc; proxy-test'`，或直接用 execute_code/python 验证（`bash -n` 只查语法不验证函数存在）。

### 坑2：pgrep/pkill -f 匹配到自己的命令行 → 误判"隧道复活"

`pgrep -f "ssh -L 17897"` 会匹配到**当前诊断命令自己**（命令行里含同样字符串），看起来隧道一直"复活"杀不死。
- **中括号技巧**：`pgrep -f "[s]sh -L 17897"`（正则 `[s]` 只匹配 s，自己命令行里的字面 `[s]sh` 不会被匹配）
- 或 python 读 /proc/PID/cmdline 精确判断是不是真 ssh
- 诊断端口/隧道优先 `ss -tlnp`（看监听），不要 pgrep 进程名

### 坑3：隧道端口在听但 curl 全 000 → 目标端没代理

`ss -tnp` 看到 SSH ESTABLISHED + 17897 监听，但经隧道全 000。层定位：
```bash
# ① Mac 端代理本身
ssh mac@100.80.117.5 'curl -sx http://127.0.0.1:7897 -o /dev/null -w "%{http_code}" https://www.google.com'
# 000 + lsof 无监听 → Mac 端没起代理（TUN 模式场景）
# ② 隧道端口
ss -tlnp | grep 17897
# ③ 经隧道
curl -sx http://127.0.0.1:17897 -o /dev/null -w "%{http_code}" https://www.google.com
```

### 坑4：全局代理变量劫持 pip/uv

`.bashrc` 里 `export https_proxy=...` 会让 pip/uv 全部走代理；代理不通时报 `ProxyError('Cannot connect to proxy')` / `tunnel error: io error establishing tunnel`。
装依赖前 `unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY`（保留 GOPROXY，那是 go 专用）。
腾讯云机器 pip/uv 直连内网源 `mirrors.tencentyun.com` 即可（pip.conf 已配，无需改）。

## 恢复路径（如未来 Mac 改回端口代理模式）

如果未来 Mac Clash 不再用 TUN 而是正常监听混合端口（如 7897）：
1. 确认：`lsof -iTCP:7897 -sTCP:LISTEN` 有输出
2. 重新建隧道 + keepalive start_tunnel() + git 代理，见本文件开头已撤回的配置
3. 但 gitcode 镜像方案已生效且更简单——**优先保留 gitcode，隧道仅作备用**