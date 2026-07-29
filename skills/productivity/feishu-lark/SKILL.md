---
name: feishu-lark
description: "Configure, use, and troubleshoot Hermes Agent's Feishu/Lark integration — messaging, document tools, and API permissions."
version: 1.0.0
author: Hermes Agent
tags: [feishu, lark, messaging, document, configuration, permissions]
---

# Feishu / Lark Integration

Hermes connects to Feishu (飞书) / Lark as both a messaging platform and a document-drive tool integration. This skill covers setup, available tools, required API permissions, and troubleshooting.

## Prerequisites

- A Feishu app created at https://open.feishu.cn/app
- App ID, App Secret, Encrypt Key, Verification Token configured in Hermes
- WebSocket connection active

## Available Capabilities

### Messaging Platform (Gateway)

Feishu as a chat platform supports the full feature set:

| Feature | Supported |
|---------|-----------|
| Text messages | ✅ |
| Images | ✅ (via `MEDIA:` path in response) |
| Files/attachments | ✅ |
| Voice (TTS + STT) | ✅ |
| Threads (topics) | ✅ |
| Emoji reactions | ✅ |
| Typing indicator | ✅ |
| Streaming output | ✅ |
| Slash commands (/help, /model, etc.) | ✅ |
| Session persistence | ✅ |

### Document & Drive Tools

These are first-class tool calls the agent can make during a conversation, NOT chat features:

| Tool | Function | Status |
|------|----------|--------|
| `feishu_doc_read(doc_token)` | Read full document content as text | ✅ Active |
| `feishu_drive_list_comments(file_token)` | List all comments on a doc | ✅ Active |
| `feishu_drive_list_comment_replies(file_token, comment_id)` | View replies in a comment thread | ✅ Active |
| `feishu_drive_reply_comment(file_token, comment_id, content)` | Reply to a local (quoted-text) comment | ✅ Active |
| `feishu_drive_add_comment(file_token, content)` | Add a whole-document comment | ✅ Active |

**Toolsets**: `feishu_doc` and `feishu_drive` (see `toolsets.py` in Hermes source).

## Required Feishu API Permissions

Grant these at https://open.feishu.cn/app → your app → 权限管理. After adding, re-publish the app version and get admin approval, then `hermes gateway restart`.

### For messaging (chat):
| Permission | Why |
|------------|-----|
| `im:message` | Read and send messages in groups/DMs |
| `im:resource` | Download images/files from messages |

### For document tools (feishu_doc_read etc.):
| Permission | Why |
|------------|-----|
| `docx:document:readonly` | Read document content (sufficient for `feishu_doc_read`) |
| `drive:drive:readonly` | Read-only Drive access (needed for some doc metadata operations) |
| `drive:drive` | Full Drive access (if you need write in the future) |

### For drive comment tools (feishu_drive_*):
| Permission | Why |
|------------|-----|
| `drive:drive:readonly` | Read file info to locate documents |
| `drive:drive` | Full access (required for adding/reply comments on files) |

### Additional capabilities (opt-in):
| Permission | Unlocks |
|------------|---------|
| `docx:document` | Create and edit documents |
| `sheet:sheet` | Read/write spreadsheets |
| `bitable:app` | Create and manage Bitable (多维表格) — **required for any agent trying to write OKR tables, project plans, or structured data into Feishu** |
| `base:app:create` | Alternate scope for creating Bitables (use when `bitable:app` isn't available) |
| `drive:drive.metadata:readonly` | Search cloud drive files |
| `im:message:send_as_bot` | Bot proactively sends messages (not just replies) |
| `contact:contact:readonly` | Query user/group info |

## Troubleshooting

### "Tool not available"
Check if `feishu_doc` / `feishu_drive` toolsets are enabled:
```
hermes tools list
```
If disabled:
```
hermes tools enable feishu_doc
hermes tools enable feishu_drive
```
Then `/reset` to start a fresh session.

### Permission errors
Feishu API returns specific error codes:
- **Code 1069302** → Wrong comment type (use `feishu_drive_add_comment` for whole-doc, `feishu_drive_reply_comment` for local)
- **Code 99991663** → Missing `drive:drive` permission scope
- **Code 99991668** → Missing `docx:document:readonly` scope
- **Code 99991672** → Missing `bitable:app` or `base:app:create` scope. Go to https://open.feishu.cn/app → your app → 权限管理 → add the Bitable permission → re-publish app version → `hermes gateway restart`
- **Permission denied on docs** → App hasn't been added to the document's sharing scope, OR permission not re-published after adding

### Document not found
Ensure the app has been added as a collaborator (share → add the bot user) on the specific document.
### Gateway restart after permission changes

Permission changes require a re-published app version AND gateway restart:
```bash
hermes gateway restart
```

---

## Feishu 交互注意事项

### ❌ 不要用 `clarify` 工具的多选模式

在飞书环境下，`clarify` 工具的选择框（choices 参数）点击无响应。用这个工具等于让用户看到了选项却选不了。

**替代方案**：直接用文字问，让用户打字回复。举例：

```
❌ clarify(question="选哪个？", choices=["A方案", "B方案"])
✅ "选 A 方案还是 B 方案？直接打字告诉我。"
```

如有多个选项需要用户选择，在消息正文中一行一个列出，加上编号，让用户回复数字或关键词。

---

## Bitable (多维表格) API 工作流

当用户要求创建多维表格（OKR拆解、项目进度表、货盘表等），通过 Feishu Open API 直接操作。

### 前置条件

- 飞书开放平台后台已开通 **`bitable:app`** 或 **`base:app:create`** 权限
- 权限变更后需：重新发布应用版本 → 管理员审批 → `hermes gateway restart`
- 凭证在 `~/.hermes/.env` 中：`FEISHU_APP_ID` + `FEISHU_APP_SECRET`

### 核心 API 顺序

```
1. POST /auth/v3/tenant_access_token/internal  ─── 获取 token
2. POST /bitable/v1/apps                        ─── 创建多维表格本体
3. PATCH /bitable/v1/apps/{token}/tables/{id}   ─── 重命名默认表（PATCH,非PUT）
4. POST /tables/{table_id}/fields               ─── 添加字段（×N次）
5. POST /tables/{table_id}/records              ─── 插入记录（×N条）
```

### 完整 Python 工作流

参见 `references/bitable-api-workflow.py`，包含完整的函数封装。

### 📛 表名含 emoji 的正确做法

emoji 在 POST create-table 时会导致 JSON 解析失败。**必须两步走**：

```
# ❌ 失败
POST /tables  {"table": {"name": "📅 30天进度表"}}  → JSON parse error

# ✅ 正确
POST /tables  {"table": {"name": "30天进度表"}}      → 成功，返回 table_id
PATCH /tables/{id}  {"name": "📅 30天进度表"}         → 成功，加上emoji
```

### ⚠️ 字段 vs 记录 API 差异（易错）

| 操作 | 用字段名还是字段ID？ | 示例 |
|------|-------|-------|
| 创建字段 | 只需 `field_name` | `{'field_name': '目标', 'type': 1}` |
| 插入记录 | **用字段名作 key** | `{'fields': {'目标': '值', 'KR': '值'}}` |
| 更新记录 | 同上，用字段名 | `{'fields': {'状态': '已完成'}}` |

**插入记录时绝对不要用字段 ID**（如 `fldzK1JVVx`）作 key——会报 1254045 FieldNameNotFound。

### 常见错误码速查

| 错误码 | 含义 | 修复 |
|--------|------|------|
| `99991672` | 缺少 bitable 权限 | 权限管理→bitable:app→重新发布→重启网关 |
| `1254001` | WrongRequestBody | 创建表需 `{'table': {'name': ...}}` 包装 |
| `99992402` | field validation failed | 字段属性在顶层，不要 `{'field': {...}}` |
| `1254045` | FieldNameNotFound | 记录用字段名作key，不是字段ID |
| JSON parse error | 含 emoji / 响应非JSON | 表名先不带emoji创建再PATCH；检查响应体 |
