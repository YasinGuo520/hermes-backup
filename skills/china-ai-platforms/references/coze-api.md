# Coze（扣子）API 调用实录（2026-09-01 实测）

字节 Coze 国内版。`星刃` = Yasin 的 Coze bot（已发布到飞书，不在服务器上）。

## 认证

- Base：`https://api.coze.cn`（国内版）
- Header：`Authorization: Bearer pat_xxx`（个人访问令牌 PAT）
- PAT 在 Coze 控制台生成：「头像→设置→API 授权/访问令牌」；**只完整显示一次，必须当时复制**
- PAT **有效期 1 个月**，到期需重生成（Yasin 明确要求到期提醒）
- 扣子改版后（界面自称"扣子Agent"），API 入口藏得深，在设置里搜"访问令牌/API"可定位

## 实测有效的端点

| 端点 | 状态 | 说明 |
|---|---|---|
| `POST /v3/chat` | ✅ 可达 | chat 主入口；body 需 `bot_id`+`user_id`+`additional_messages` |
| 老版 `/open_api/v3/chat` | ❌ 404 | 已迁移，别用 |
| 猜测的 `/v1/space/list` 等 | ❌ 4000/404 | 文档迁移后路径全变，**别盲猜端点** |

实测：传空 bot_id 到 /v3/chat 返回 `4200 bot_id=0 does not exist` = 认证已通过只缺 bot_id。这是验证 token 有效性的最快方法。

## 错误码（实测）

| 码 | 含义 |
|---|---|
| `4101` | token 错误/无效 |
| `4200` | bot_id 不存在（认证已过） |
| `4000` + "endpoint does not exist" | 路径不存在 |

注意：curl 返回 HTML `404 Not Found` = 路径不存在；返回 JSON 错误码 = 服务端在响应（路径有效）。

## bot_id 获取（别猜 API）

最可靠路径：**打开 Coze 控制台 → 进入 bot 页面 → 复制 URL，末尾那串数字就是 bot_id**（形如 `https://www.coze.cn/space/xxx/.../bot/123456789`）。官方文档页 `www.coze.cn/docs/developer_guides/*` 已迁移/404，别去翻。

## 登录自动化坑（字节风控）

- 无头浏览器登录 coze.cn：点击"发送验证码"触发**滑块验证码**（iframe 来自 `rmc.bytedance.com`、`verify.zijieapi.com`，请求带 `subtype=slide`）
- 暴露特征：请求 URL 里 `webdriver=true`
- 反检测 JS（`navigator.webdriver=undefined`、伪造 UA/plugins/languages）**不足以过字节风控**——别死磕自动化登录
- 验证码登录必须用户手机收短信：让用户配合发手机号+验证码，或直接让用户自己在手机/网页登录
- 判定发送是否成功的标志：按钮进入倒计时（如"60s"）；仍显示"发送验证码"=没发出去
- 协议复选框必须先勾选，否则发送/登录按钮是灰的

## 免费额度坑

- Coze 免费额度（豆包模型送的 token）**用完 bot 会哑火不回复**——不是配置问题，是额度问题
- 现象：用户说"之前能回，现在问它不回答了" → 大概率免费额度耗尽
- 这正好是给企业做 AI 落地时的谈预算话术：免费额度是钓钩，企业用 Coze 必须按月预算豆包 token 费

## 工作流坑（Yasin 纠正过）

- **用户已有可用 bot 时（如星刃在飞书），不要新建 demo**——直接调现有 bot 做作品集/演示，比从零建一个强十倍
- 申请 PAT 是正道，不用走用户名密码截图流程