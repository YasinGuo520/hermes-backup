# Curator 技能库清理工作流

## 为什么重要

Hermes 每次对话开头会枚举**所有 skill 的description**注入 system prompt。技能越多 → context 前缀越长 → 模型有效工作窗口越窄 → "变傻"感越明显。

本环境实际案例：138个skill → 181MB → 用户反馈"思维浮于表面"，清理后预期降到50-60个。

## Curator 安全原则

| 特性 | 值 |
|------|-----|
| 删除？ | ❌ 永不删除 |
| 操作方式 | 归档（移至 `.archive/` 目录，排除出prompt但可恢复） |
| bundled skill | 永不动。Hermes自带/随版本更新 |
| hub skill | 永不动。从skill.sh安装的 |
| agent-created | 仅归档长期未使用的 |
| 自动备份 | 每次 `curator run` 前自动 tar.gz 快照 |
| 回滚 | `curator rollback` 全量恢复 |

## 完整命令集合

### 查看状态
```bash
hermes curator status              # managed/unmanaged/archived 分布
hermes curator usage               # 所有skill的活跃数据（use/view/patch/act/last_activity）
hermes curator list-unmanaged      # 未被curator登记的技能（无provenance标记）
hermes curator list-archived       # 已归档的技能
```

### 注册未管理的skill
```bash
hermes curator adopt <name>        # 逐个登记给curator管理
```

### 触发审核/清理
```bash
hermes curator run                 # 立即审核：归档90天未用的skill
hermes curator prune --days 90     # 手动批量归档闲置超过N天的skill
```

### 启用LLM合并（关键！默认关闭）
默认 curator 只归档不合并（consolidate: off）。要减少skill数量必须手动开启：
```bash
hermes config set curator.consolidate true
```

### 安全网
```bash
hermes curator backup              # 手动创建tar.gz快照
hermes curator rollback            # 全量回滚（默认最新快照）
hermes curator restore <name>      # 恢复某个已归档的skill
hermes curator pin <name>          # 锁定不让curator自动归档
hermes curator unpin <name>        # 解锁
```

### 暂停/恢复
```bash
hermes curator pause
hermes curator resume
```

## ⚠️ 已知陷阱

| 陷阱 | 现象 | 修复 |
|------|------|------|
| **`adopt --all-unmanaged` 需要交互** | 直接跑会 abort，没实际执行 | 必须管道 yes：`echo "y" \| hermes curator adopt --all-unmanaged` |
| **`consolidate` 默认 off** | curator 只归档零使用技能，但**不会合并同类项**。140个skill→即使清理归档了也还是100+ | `hermes config set curator.consolidate true`，然后 `curator run` |
| **`curator run` 可能超时** | LLM合并需要调用辅助模型，深seek 响应慢时 120 秒 timeout | 超时后 `curator status` 检查执行结果，不影响已完成的步骤 |
| **`prune --days 90` 对刚adopt的skill无效** | 刚adopt的skill没有足够的历史闲置数据 | 改用 `for s in skill-a skill-b; do echo "y" \| hermes curator archive $s; done` |

## 归档清单 → Obsidian 可见性模式

curator 归档技能后，agent 不再知道它们存在。要解决"归档不失联"：

### 流程

```
curator archive skill-a skill-b skill-c
       ↓
运行 build-skill-manifest.py → 生成技能档案库.md（含所有活跃+归档技能清单）
       ↓
写入 Obsidian vault /.hermes/skills/.manifest/ （取决于环境）
       ↓
kb_summary.py 每4小时蒸馏到共享上下文
       ↓
新会话自动感知所有技能存在
       ↓
需要时 → hermes curator restore <name> → skill_view() 调用
```

### 关键设计

- 归档清单不进 system prompt（不涨 token），仅进共享记忆层
- 分节：活跃skill（按功能分类） + 归档skill表（含恢复命令）
- 描述归描述，不要塞 full SKILL.md 内容
- 每次 curator 清理后重新生成一次

### 适用场景

- 用户说"归档后我还是想调用"
- 技能库膨胀但用户不愿失去发现能力
- 多Agent实例共享同一份 skill 索引

详见 `scripts/build-skill-manifest.py`。
