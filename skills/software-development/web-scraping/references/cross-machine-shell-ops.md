# 跨机作业的 shell 传输与超时（实测坑）

> 场景：在服务器上用 `ssh mac@<tailscale-ip>` 驱动另一台机器（部署、改配置、起采集器、看日志）。
> 下面每一条都是 2026-09-12 实际卡住过我的地方。

## 一、别用 inline SSH 引号跑复杂命令 —— 写脚本传过去

嵌套引号（中文提示词 + JSON + 双引号命令）会反复报 `unmatched "` / 参数被 zsh 吃掉。
**正解**：本地 `write_file` → `scp` 到目标机 → `ssh mac@ip 'bash /tmp/xxx.sh'` 跑。
脚本内部用 `bash` 执行（显式走 bash，避开 zsh 分词），要传中文/引号做参数时也从文件读。

## 二、zsh 专属坑（macOS 默认 shell）

| 写法 | 实际后果 | 正解 |
|---|---|---|
| `rm -f dir/Singleton*`（无匹配） | `zsh: no matches found` 且**该行不执行**（不报错退出但也没干活） | 写全文件名，或 `find … -delete` |
| `for kv in …; do set -- $kv; cmd $1 $2; done` | `hermes config set` **只打印了帮助文本、值没变**（静默失败，极易误判为“已改”） | 脚本里用 bash，或每条命令完整写出，不靠 `set --` 分词 |
| 非交互 SSH 下找不到命令 | PATH 缺 `~/.local/bin` | 脚本首行 `export PATH="$HOME/.local/bin:$PATH"` |

改配置类操作后**必须读回验证**：`hermes config get <key>` 看值真的变了，不看命令输出看着像成功就收工。

## 三、macOS 没有 GNU `timeout`

`timeout 200 bash xxx.sh` 在 Mac 上报 `timeout: command not found`。
要么装 `coreutils` 用 `gtimeout`，要么把超时交给调用层（Hermes 的 `terminal(timeout=…)`），脚本里不写 `timeout`。

## 四、长任务后台化三件套

```bash
nohup <cmd> > /tmp/task.log 2>&1 < /dev/null &
sleep 20; pgrep -fl "<脚本名>"          # 只信进程，不信「命令没报错」
```

读远程日志先去 ANSI（否则满是控制字符，没法读）：

```bash
sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' -e 's/\r/\n/g' /tmp/task.log | grep -v '^$' | tail -30
```

## 五、目标机 Python 版本要分清

| 解释器 | 版本 | 坑 |
|---|---|---|
| macOS 系统 `python3` | **3.9** | f-string 表达式里**不能有反斜杠** → `SyntaxError`（拆成先赋值再格式化） |
| Homebrew / 项目 venv | 3.13+ | 正常；跑目标机 Hermes 自己的代码要用它的 venv |

## 六、别用宽匹配 `pkill`（会误伤）

- `pkill -f "app.py"` 这类宽匹配可能命中网关/自己，且**从网关进程内杀进程会被安全拦截器硬拦**（SIGTERM 会传播）。
- 取 pid 用端口反查更准：`ss -tlnp 2>/dev/null | grep ':<port>' | grep -oP 'pid=\K[0-9]+'`。
- 服务进程的重启**交给 keepalive/cron 兜底**（服务器上 keepalive.sh 每 3 分钟扫一次端口，杀掉会在下个 tick 自动拉起），不要在会话里冒险杀。
  判断依据而不是猜测：“这个服务到底归谁管、多久拉一次” —— 去 `grep <端口> <keepalive 脚本>` + `crontab -l` 看。
