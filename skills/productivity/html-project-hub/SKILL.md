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

## 端口分配规则

| 端口段 | 用途 |
|:------:|------|
| 8890-8899 | HTML项目（每个项目一个） |
| 8900 | 工具箱（专用） |
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

# 验证导航页是否更新
grep -c '工具' ~/Desktop/hermes/hermes-hub/index.html
```

## 工具箱 vs 导航中心

| | 方法论工具箱 | 项目导航中心 |
|:--|:-----------|:-----------|
| 端口 | 8900 | 8895 |
| 数据源 | Hermes skills_list | VPS上运行的HTML项目 |
| 更新方式 | 编辑build_toolbox.py | 编辑build_hub.py |
| 用途 | 展示所有可调用工具 | 展示所有可访问网页 |

两个脚本共用相同的「数据列表+渲染→HTML」模式。

## 常见坑

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

## 参考文件

- `references/build_hub_template.py` — 完整可用的导航中心构建脚本（当前生产版）
