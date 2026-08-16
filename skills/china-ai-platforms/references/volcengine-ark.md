---
name: volcengine-ark-api
description: 火山引擎/火山方舟 API 调用全流程——Key类型、模型开通、视频/图像生成接口、价格表、常见坑。硅基流动调不到的闭源模型（豆包/即梦/Seedance）走这条线。
---

# 火山引擎 / 火山方舟 API

当用户要调**豆包/即梦/Seedance（字节系闭源模型）**——硅基流动覆盖不到的能力——走火山。视频生成（带货视频、产品动效）是主要场景。

## 关系图（先分清，别搞混）

```
火山引擎（字节云平台，类比阿里云）
 ├── 火山方舟 Ark   — 大模型API：豆包/K3/DeepSeek 对话、Seedance 视频、Seedream 图像
 ├── 即梦AI          — 产品线，API 走方舟接口
 ├── 语音技术        — TTS/ASR（独立开通）
 └── 云服务器/存储/GPU
```

- 一个火山账号，各产品线**分开开通、分开计费**
- 视频/图像/对话API 统一走方舟接口 `ark.cn-beijing.volces.com`

## 关键流程

1. **注册**火山引擎（个体户执照可实名）→ 控制台
2. **创建「方舟大模型专用 API Key」**（不是普通 API Key！）
   - 入口：访问控制页里蓝色链接「方舟大模型专用 API Key」
   - 格式：`ark-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-xxxx`
   - ⚠️ 普通 API Key（无 ark- 前缀）调方舟接口必 401
3. **开通模型**：方舟控制台 → 模型广场/开通管理 → 搜索模型ID → 开通
   - ⚠️ Seedance 视频模型开通前需**先充值或购买资源包**（免费额度开不了视频）
   - 开通本身不收费，按调用量计费
4. **配置**：写入 `~/backend/.env` 的 `ARK_API_KEY`（改前先 cp 备份）

## 接口速查

Base URL: `https://ark.cn-beijing.volces.com/api/v3`

| 功能 | 方法/路径 | 认证 |
|------|----------|------|
| 列出所有模型 | GET `/models` | Bearer |
| 对话 | POST `/chat/completions` | Bearer |
| 提交视频生成任务 | POST `/contents/generations/tasks` | Bearer |
| 查询视频任务状态 | GET `/contents/generations/tasks/{id}` | Bearer |
| 提交图像生成任务 | POST `/contents/generations/tasks` | Bearer |

⚠️ **路径是 `generations`（复数），不是 `generators`** —— 拼错返回 404 无 body，易误判为网络问题。

## 视频生成调用示例（curl）

```bash
ARK_KEY="ark-..."  # 从 ~/backend/.env 读

# 1. 提交任务（异步，返回 task id）
curl -s -X POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks \
  -H "Authorization: Bearer $ARK_KEY" -H "Content-Type: application/json" \
  -d '{"model":"doubao-seedance-1-0-pro-fast-251015","content":[{"type":"text","text":"一只橘猫从纸箱里探出头"}],"resolution":"720p","duration":5}'

# 2. 轮询任务状态，succeeded 后取 content.video_url（预签名24h，及时转存）
curl -s https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{id} \
  -H "Authorization: Bearer $ARK_KEY"
```

## 常见错误速查

| 错误 | 含义 | 解法 |
|------|------|------|
| 401 AuthenticationError | Key 无效/类型不对 | 换方舟专用 Key（ark- 开头） |
| ModelNotOpen / 404 "not activated" | 模型没开通 | 控制台开通该模型 |
| 404 空 body | 路径拼错 | 检查 `generations` 拼写 |
| ModelNotOpen (模型ID存在但没激活) | 账号未开通该模型 | 开通或充值（Seedance 需充值） |

## 配置与验证命令

```bash
# 验证 Key（最快：拉模型列表，200 = 通过）
curl -s https://ark.cn-beijing.volces.com/api/v3/models -H "Authorization: Bearer $ARK_KEY"

# 验证对话（需已开通该模型）
curl -s -X POST https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Authorization: Bearer $ARK_KEY" -H "Content-Type: application/json" \
  -d '{"model":"doubao-seed-2-1-lite-260428","messages":[{"role":"user","content":"你好"}],"max_tokens":10}'
```

## 生态对比（选型）

| 需求 | 平台 | 原因 |
|------|------|------|
| 开源模型（K3/Qwen/FLUX/DeepSeek） | 硅基流动 | 便宜、key已有 |
| 豆包/即梦/Seedance（闭源） | 火山方舟 | 硅基流动没有闭源 |
| GPT/Claude/Gemini | 官方API | 国内平台都调不到，且墙内不稳 |

价格表与模型ID清单见 `references/volcengine-pricing-models.md`。
