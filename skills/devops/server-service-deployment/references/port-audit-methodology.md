# 全端口审计方法论

**触发场景：** 用户说"端口打不开"、"检测下所有端口"、"帮我弄清楚下"。

## 第一条规则：一次性扫全，别分步问

用户说"你自己弄清楚下" = 别逐个问"这是什么"、"那是什么"。一次性把所有端口列出来，附上项目名称、运行状态、可访问性。

## 标准审计流程

### 1. 全端口监听清单

```bash
ss -tlnp | grep -E 'LISTEN' | grep -v '127.0.0.53' | sort -n -t: -k2
```

输出示例：
```
LISTEN 0      5       0.0.0.0:8895    0.0.0.0:*   users:((\"python3\",pid=639568,fd=4))
```

### 2. Docker 容器（可能占用端口）

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

Docker 容器即使项目删了也不会自动停止。这是常见坑。

### 3. 外网可达性验证

对每个公网绑定的端口：
```bash
# 基本检测（不含重定向跟随）
curl -s --connect-timeout 3 -o /dev/null -w "HTTP %{http_code}" http://43.138.221.174:PORT/

# 带重定向跟随（处理 301/302/307 跳转——如 FastAPI 根路由配了 RedirectResponse）
curl -sL --connect-timeout 3 -o /dev/null -w "HTTP %{http_code}" http://43.138.221.174:PORT/

# 查看实际返回内容的前200字符
curl -s --connect-timeout 3 http://43.138.221.174:PORT/ | head -c 200
```

**⚠️ 注意：FastAPI 服务根路由可能是 307 重定向。** 服小助案例：根路由 `RedirectResponse("/static/index.html")` 返回 307，不带 `-L` 的 `-w %{http_code}` 只会显示 307 而非 200。**第一次检测总先用 `curl -sL` 跟随跳转。**

### 4. 端口→项目映射

对每个端口判断：
- **端口号特征**：800+ = 常见Web服务，88+ = 静态页面，80/443 = 标准Web
- **进程名**：`python3` = Python服务，`uvicorn` = FastAPI，`java` = Java服务，`nginx` = 反向代理
- **进程PID** → `ps -p <PID> -o cmd=` 看完整命令行
- **工作目录**：`lsof -p <PID>` 或 `pwdx <PID>` 找到项目文件
- **curl根路径返回**：JSON = API后端，HTML = 有网页界面

### 5. 输出格式

用表格呈现，项目按类型分组（HTML项目 / 后端服务），每项标注端口、状态、外网可达性。

如果多个项目共用一个域名（如 Nginx 反向代理），在表格中标注域名。

```
| 端口 | 项目名 | 状态 | 类型 | 外网可达 |
|:----:|:------|:----:|:----|:-------:|
| 8000 | 服小助AI客服 | ❌ 未运行 | API | - |
| 8001 | 中年人生诊断(127.0.0.1) | ✅ | API | ❌ 仅内网 |
| 8080 | ~~已删项目的Docker残留~~ | ⚠️ 需清理 | Docker | ✅ |
| 8894 | 个人简历 | ✅ | 静态页面 | ✅ |
```

### 6. Supervisor 管理的服务排查

部分项目通过 supervisor 管理（如中年人生诊断 FastAPI 后端），不会出现在普通进程列表里。

```bash
# 列出所有 supervisor 管理的程序
sudo supervisorctl status

# 查看具体配置（从中找到端口/绑定地址/工作目录）
cat /etc/supervisor/conf.d/<program-name>.conf

# 日志位置（配置中定义的）
tail -20 <stderr_logfile_path>
tail -20 <stdout_logfile_path>

# 修改配置后重新加载（重点：reread + update 两步缺一不可）
sudo sed -i 's/旧内容/新内容/' /etc/supervisor/conf.d/<program-name>.conf
sudo supervisorctl reread    # 让 supervisor 知道配置变了
sudo supervisorctl update    # 实际应用变化
sudo supervisorctl restart <name>
```

**典型问题：supervisor 配置绑了 127.0.0.1 导致外网访问不了**

```bash
# 改绑定地址
sudo sed -i 's/--host 127.0.0.1/--host 0.0.0.0/' /etc/supervisor/conf.d/<program>.conf
sudo supervisorctl reread && sudo supervisorctl update && sudo supervisorctl restart <name>

# 确认：ss -tlnp | grep <PORT> 应显示 0.0.0.0:<PORT>
```

**定位 supervisor 管理服务的完整流程：**
```bash
# 1. 从端口找到进程 → 2. 看完整命令行 → 3. 检查 supervisor 配置目录
lsof -ti:<PORT> | xargs -r cat /proc/{}/cmdline 2>/dev/null | tr '\0' ' '
ls /etc/supervisor/conf.d/
```

### 7. Docker 残留容器清理

**场景：** 用户项目已删但 Docker 容器还在跑，占用端口和资源。

```bash
# 找到 docker-compose 文件
find /home/ubuntu -maxdepth 3 -name "docker-compose*"

# 停掉并移除所有容器 + 网络 + 数据卷
cd <project-dir-with-docker-compose>
docker compose down -v
```

**`docker compose down -v` 的作用：** 停止容器 → 删除容器 → 删除网络 → **删除数据卷**（redis/postgres 持久化数据）。不加 `-v` 则保留数据卷。

**无 docker-compose 文件的清理：**
```bash
docker rm -f <container-name-1> <container-name-2>
docker network rm <network-name> 2>/dev/null || true
docker volume rm <volume-name> 2>/dev/null || true
```

### 8. 用户说"我是开启的啊"诊断

当用户说某个服务已经开了但端口没监听：

```
排查链条：
1. ss -tlnp | grep <PORT>  → 端口有没有被监听
2. docker ps | grep <PORT> → 是不是Docker跑着但端口没暴露
3. 查看项目目录下 .env / config → 是不是缺配置导致启动失败
4. 查看项目目录下 start.sh / 日志 → 启动脚本执行过没有
5. 检查 venv 是否存在 → 依赖是否安装
```

**常见原因：**
- 缺 `.env` 文件或环境变量 → 服务启动就崩了，用户以为正常
- venv 不存在 → 依赖没装
- 端口冲突（被其他进程占用了）→ 换个端口
- 只绑了 127.0.0.1 → `ss` 能看到但外网访问不了
- 用户之前用 docker run / tmux / screen 启动，重启后丢了
