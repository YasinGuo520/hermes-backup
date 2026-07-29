---
name: find-skills
description: 自动搜索并安装社区最佳Skill，连接Skill.sh和Agent Skills生态，通过自然语言描述需求找到最匹配的Skill。
---

# FindSkills（Skill搜索引擎）

当用户需要某个功能但不确定具体Skill名称时，搜索并推荐最佳Skill。

## 搜索方式

| 方式 | 说明 |
|------|------|
| 自然语言 | "帮我找一个能做封面图的Skill" → 返回推荐列表 |
| 关键词 | 搜"tdd"、"前端设计"、"封面图" |
| 平台搜索 | 在Skill.sh / GitHub / 官方市场搜索 |

## 推荐流程

1. 理解用户需求
2. **先检查Hermes是否已有内置能力** — vision_analyze/memory/session_search/terminal/file等内置工具能否满足？能就直接用，不装
3. 搜索匹配的Skill
4. 对比推荐Top 3
5. 提供安装方式和说明

## 前置检查清单（必做）

在安装任何Skill前，逐项检查：
- ✅ Hermes内置工具（vision_analyze/terminal/file/web_search等）能否完成？
- ✅ 已有Skill列表（skills_list）是否有同名或同功能？
- ✅ 用户配置（config.yaml/.env）是否已开启对应能力？
- 以上任一✅ → 直接告知用户已有，不安装

## 常见陷阱

- ❌ 用户发来一个Skill推荐视频/文章时，不要直接安装——先检查内置能力
- ❌ Skill名称不同但功能相同的情况很多（如"长期记忆"类有多个），优先复用已有
- ✅ 用户偏好已记录在memory中：『先检查Hermes是否已有自带工具/能力实现相同功能』

## 辨别：单Skill vs. GitHub项目工具

搜索时注意区分两种来源：

| 类型 | 特征 | 处理方式 |
|------|------|----------|
| **单Skill** | 可单独安装的 Skill 包 | 用 `hermes skills install` 或本skill推荐 |
| **GitHub项目工具** | 仓库含 `skills/` + `plugins/` 目录 | ⭐ 用 `install-github-hermes-tools` skill处理：克隆→venv→软链技能/插件→验证 |

例如 `quant-trade` 有14个skill + 1个plugin，需要软链而不是 `hermes skills install` 安装。

## 安装命令格式参考

Hermes 支持多种安装 ID 格式，知道这些能省很多时间：

| 格式 | 示例 | 说明 |
|------|------|------|
| `official/<category>/<skill>` | `official/creative/pixel-art` | 官方可选 skill（与 Hermes 捆绑但不激活） |
| `github:<owner>/<repo>` | `github:Agents365-ai/drawio-skill` | 社区 GitHub 仓库（单 SKILL.md） |
| `skills-sh/<owner>/<repo>` | `skills-sh/ZeroPointRepo/youtube-skills/skills/youtube-full` | skills.sh 注册表格式 |
| 直接 URL | `hermes skills install https://raw.../SKILL.md --name <name>` | 任意 SKILL.md 直链 |
| Tap | 先 `hermes skills tap add <owner>/<repo>` 再安装 | 将整个 GitHub 仓库添加为源 |

**重要：** `hermes skills install` 会弹出确认提示。批处理时用 `echo "y" |` 管道自动确认：
```bash
echo "y" | hermes skills install official/creative/blender-mcp
```

## 多Skill仓库处理

有些 GitHub 仓库包含**多个独立的 SKILL.md**（如 `black-forest-labs/skills`），结构如下：
```
repo/
├── skills/
│   ├── skill-a/SKILL.md
│   └── skill-b/SKILL.md
├── packages/
└── ...
```

如果 `hermes skills install github:<owner>/<repo>` 找不到该仓库，采取以下步骤：

1. **先添加 Tap：**
   ```bash
   hermes skills tap add <owner>/<repo>
   # 然后尝试 hermes skills install <owner>/<repo>/skills/<skill-name>
   ```

2. **如果 Tap 安装也失败，手动克隆到 skills 目录：**
   ```bash
   git clone --depth 1 https://github.com/<owner>/<repo>.git /tmp/<temp-dir>
   # 将 skills/<skill-name>/ 整个目录复制到 ~/.hermes/skills/
   cp -r /tmp/<temp-dir>/skills/<skill-name> ~/.hermes/skills/<skill-name>
   rm -rf /tmp/<temp-dir>
   ```
   
   注意：手动复制的 skill 必须有**含 name 和 description 的 YAML frontmatter** 的 `SKILL.md` 文件才能被 Hermes 识别。

3. **验证安装：** `hermes skills list | grep <skill-name>` 确认状态为 `enabled`

### ⚠️ 嵌套 SKILL.md 不被 `npx skills add` 识别

`npx skills add <owner>/<repo>` 会成功克隆仓库，但报告 `No valid skills found`，因为 skills CLI **只在仓库根目录找 SKILL.md**，不递归扫描 `skills/` 子目录。

```bash
# 这种写法会失败（即使仓库里有多个 SKILL.md）
npx skills add GoldLegendW80/llm-video-maker

# 正确方式：用 Hermes 的 tap 机制指定子路径
hermes skills tap add <owner>/<repo>
hermes skills install <owner>/<repo>/skills/<skill-name>
```

### 🌐 中国网络环境下的安装替代方案（重要）

在 GitHub 直连困难的情况下（克隆超时/unexpected disconnect），所有自动安装方式都可能不可靠。按优先级尝试以下方案：

1. **Tap（最轻量）：** `hermes skills tap add <owner>/<repo>` 通常能成功，但后续 `hermes skills install <owner>/<repo>/skills/<name>` 可能仍超时
2. **npx skills add（次选）：** 可能因嵌套 SKILL.md 结构失败（报告 "No valid skills found"）
3. **jsDelivr CDN 直拉文件（兜底，国内可用）：** jsDelivr CDN (`cdn.jsdelivr.net`) 在国内可直接访问，无需 VPN。格式：
   ```bash
   # 拉单个 raw 文件
   curl -sL "https://cdn.jsdelivr.net/gh/{owner}/{repo}@{tag}/{path}" -o {dest}
   
   # 示例：拉 skill 的 SKILL.md
   curl -sL "https://cdn.jsdelivr.net/gh/GoldLegendW80/llm-video-maker@main/skills/make-video/SKILL.md"
   
   # 示例：拉 schema.json 或脚本
   curl -sL "https://cdn.jsdelivr.net/gh/GoldLegendW80/llm-video-maker@main/skills/make-video/schema.json"
   ```
   拿到内容后用 `write_file` 写入 `~/.hermes/skills/<name>/SKILL.md`。**需要确保 YAML frontmatter 包含 name 和 description 字段，目录名与 name 一致。**
4. **web_extract 兜底（CDN 也失败时）：** 用 `web_extract` 从 `raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/SKILL.md` 拉取原始内容（web_extract 内部重试策略比 curl 多），然后用 `write_file` 直接写入。缺点：对大型文件可能截断（head+tail），需用 `read_file` 读取保存的完整文件再写入。
5. **ghproxy.net 镜像代理（git clone 可用）：** 当上述镜像全失败时，换 ghproxy.net：`git clone --depth 1 https://ghproxy.net/https://github.com/<owner>/<repo>.git /tmp/<target>`。镜像节点优先级：`ghproxy.net` > `ghproxy.com` > `mirror.ghproxy.com` > `hub.nuaa.cf`。

6. **纯手动创建 SKILL.md（最终方案）：** 当网络完全不可用时，通过 `web_search` 搜索项目 README，理解其功能和用法，直接编写适配版 SKILL.md 写入本地。不需要克隆仓库或拉文件。

**多脚本 skill 的注意事项：** 如果 skill 依赖多个脚本（如 `.mjs`、`.py`），用 jsDelivr CDN 逐个拉取并写入 `scripts/` 子目录：
```bash
curl -sL "https://cdn.jsdelivr.net/gh/{owner}/{repo}@{tag}/skills/{name}/scripts/{file}" -o ~/.hermes/skills/{name}/scripts/{file}
```

**中国网络环境下的其他工具配置：** 见 `hermes-china-setup` skill（浏览器自动化、图像生成、Web搜索、AI服务等）

## Tap 管理

```bash
hermes skills tap add <owner>/<repo>    # 添加 GitHub 仓库为源
hermes skills tap list                   # 列出已添加的 tap
# 注意：tap 命令不支持指定 URL 参数，只接受 owner/repo 格式
```

## 安装后确认

安装后务必用 `hermes skills list | grep <skill-name>` 检查状态。预期看到的列：
- 名称、分类、来源（official/builtin/community/local）、状态（enabled/disabled）

如果 status 是 disabled，用 `hermes skills config` 启用。

## 热门搜索源

- https://www.skills.sh - Vercel官方Skill排行榜
- https://github.com/topics/agent-skills - GitHub话题
- https://github.com/ZeroPointRepo/awesome-hermes-skills - 精选社区Skill目录（258个）
- 各Agent官方插件市场
