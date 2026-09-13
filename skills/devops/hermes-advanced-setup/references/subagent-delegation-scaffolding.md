# 用 delegate_task 让子 agent 自己搭完整个项目

> 吸收自 `subagent-project-scaffolding`（curator 合并）。与父技能「分身（Profile / Bot Mode / 子 agent）」一节配套：这里讲的是把**整个项目搭建**委派出去，然后自己验收。

## When to Use

- 用户要一个“完整项目”，而技术决策已经定了
- 项目结构、技术栈、产出物都明确
- 你有 5 分钟以上不被打断的子 agent 时间
- 子 agent 不需要任何澄清（所有决策派发前已定稿）

## Brief 模板（每一节都重要——子 agent 没有你的上下文，从零开始）

1. **Project Overview（3-5 行）**：名字、架构概要、MVP 目标。
2. **Environment（必写）**：服务器 IP/OS、CPU/RAM/Disk、已装什么（python3/pip/git/nginx?）、可用端口。
3. **Tech Stack（钉死的决策）**：表格 层|选择|理由。**硬钉**——说“Vue3 但如果太复杂就用 HTML”，子 agent 会白纠结 20 分钟。
4. **Features（P0 / P1 分级）**：P0 = MVP 必带；P1 = stub/占位。
5. **File Structure（精确树）**：给出完整目录树，它会照字面建——漏写一个文件就是不存在。
6. **Design Decisions（不可协商）**：多租户 tenant_id、JWT+bcrypt、纯 HTML 前端、SQLite+SQLAlchemy 之类。
7. **Verification Steps**：`python -m app.main` 能起、`curl /health` 200、register→login→chat 通。

关键约束模板：

```text
- 所有代码文件在 ~/projects/<name>/
- 用 venv（不要全局安装）
- 不要使用 clarify——所有决策都在 brief 里
- 不要再调用 delegate_task（叶子角色）
- 回复语言：中文
```

## 验收（子 agent 的自述是线索不是证据）

1. `find ... | sort` 核文件树
2. `pip install -r requirements.txt`
3. `terminal(background=True)` 起服务，`watch_patterns=["Application startup complete"]`
4. 写小脚本打关键 endpoint
5. 修路径不一致（实际 `@router` 前缀/路径常与预期不同）

## 坑

| 坑 | 处理 |
|---|---|
| 子 agent 把 key 写成 `"«redacted:sk-…»"` | Hermes 密钥脱敏器干的——改回 `os.getenv("KEY")` |
| 模型名写错（`deepseek-chat`） | 建完 grep `config.py` 确认真实模型名 |
| 端口占用起不来 | `lsof -ti:8000 \| xargs kill -9` |
| API 路由与预期不同 | 逐个看 `api/*.py` 的 `@router` 前缀 |
| LLM 调用全部降级 | key 没进子进程：启动前 `export $(grep -v '^#' ~/.hermes/.env \| xargs)` |
| 验证脚本里 token 被脱敏 | 先写文件，再用 Python 读回 |
| 子 agent 沉默/卡在 todo | 直接手动接管建文件+起服务 |
| 文件被覆盖 | 看 write_file 返回的 `_warning` |

## 批量单文件 HTML 并行生成模式

触发：用户说“上面的都有兴趣，全部搞出来”——一次产出多个独立 HTML 单文件。

```
主会话（你）
├── delegate_task 批次1: 游戏 + 3D名片 + 像素画展厅  (并行3个)
├── delegate_task 批次2: 案例墙 + AI抽签 + 服务器状态  (并行3个)
└── 批次3 ...
    └── 主会话统一收尾: 更新导航Hub + 启动服务
```

- `delegate_task` 一次最多 3 个（配置限制），分多批次；第 1 批放复杂度低的；同批不要都用重资源库（Three.js/CDN）；端口连续便于 hub 管理。
- 每个子任务 context 必带：文件保存路径、单文件 HTML 限制（样式/脚本内嵌、零外部依赖）、关键视觉/功能要求、启动 HTTP 服务的完整命令（background=true）、启动成功后返回文件路径+端口。
- 收尾：查所有端口服务（`lsof -ti:<PORT>`）→ 未起的先查文件再手起 → 更新 hub PROJECTS + PORT_KEYS → 重生成导航 → 浏览器逐个验证。

## 相关

- `server-service-deployment`——服务部署运维、端口/防火墙/systemd
- 本技能 SKILL.md「分身」一节——Profile / Bot Mode / 子 agent 三层区别（别拿 delegate_task 当常驻分身用）
