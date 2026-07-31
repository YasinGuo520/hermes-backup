# 火山引擎/方舟 API 接入手册（Seedance/即梦/豆包）

> 2026-07 实测。Yasin 已注册火山引擎，个体户执照可实名。
> 目标：产品图 → Seedance I2V → 带货短视频 流水线程序化接入。

## 平台结构

```
火山引擎（字节云全家桶，类比阿里云）
 ├── 火山方舟 Ark     — 大模型服务平台（豆包/K3/DeepSeek API、精调、RAG）
 ├── 即梦AI 产品线     — Seedream 图像 / Seedance 视频（同一账号单独开通）
 ├── 语音技术          — TTS/ASR（需单独开通，不在方舟）
 └── 云服务器/存储/GPU  — 传统云服务
```

## 三种凭证（最容易搞混）

| 凭证 | 用途 | 请求方式 |
|------|------|---------|
| **Access Key** (AK/SK) | 火山引擎云 API（服务器/存储/签名类） | 构造请求签名 |
| **普通 API Key** | 部分产品数据面接口（如 AI 生成类） | Bearer token |
| **方舟大模型专用 API Key** | 方舟大模型/即梦 contents 接口 | Bearer token |

**⚠️ 实测坑（2026-07）：** 在「访问控制」页面创建的**普通 API Key** 调方舟接口（`/api/v3/models`、`/api/v3/contents/generators/tasks`）**全部 401**：
```json
{"error":{"code":"AuthenticationError","message":"the API key or AK/SK in the request is missing or invalid"}}
```
必须点控制台提示框里的蓝色链接「**方舟大模型专用 API Key**」单独创建。key 本身格式正常（3段点分、158字符）≠ 权限正确。

## 配置位置

```bash
# /home/ubuntu/backend/.env  （字段已建，等正确 key 填入）
ARK_API_KEY=<方舟大模型专用API Key>
```

## API 端点

| 接口 | 方法 | URL |
|------|------|-----|
| 模型列表（验证 key） | GET | `https://ark.cn-beijing.volces.com/api/v3/models` |
| 即梦图/视频任务提交 | POST | `https://ark.cn-beijing.volces.com/api/v3/contents/generators/tasks` |
| 任务结果查询 | POST | `.../contents/generators/tasks/<id>` |
| 方舟 Chat（豆包/K3） | POST | `https://ark.cn-beijing.volces.com/api/v3/chat/completions` |

验证命令：
```bash
curl -s https://ark.cn-beijing.volces.com/api/v3/models \
  -H "Authorization: Bearer $ARK_API_KEY"
# 200 = key 正确；401 = key 类型错/无效
```

## 视频生成计费（算点制，1元≈10-12算点）

| 模型 | 分辨率 | 单价 | 15秒成本 |
|------|--------|------|---------|
| Seedance 1.0 Pro-fast | 480P/720P/1080P | 0.04/0.08/0.2 元/秒 | ≈1.2元（720P）|
| Seedance 1.0 | 480P/720P/1080P | 0.14/0.28/0.7 元/秒 | ≈4.2元 |
| Seedance 1.5 Pro 无声 | 480P/720P | 0.086/0.172 元/秒 | ≈2.6元 |
| Seedance 1.5 Pro 有声 | 480P/720P | 0.172/0.344 元/秒 | ≈5.2元 |
| Seedance 2.0 | − | ≈1 元/秒 | ≈15元 |
| OmniHuman 数字人 | − | 1 元/秒 | − |
| 智能生图 Seedream4.0 | − | 0.2 元/张 | − |

**新手路径：** 基础体验版 ¥100/月 = 1000 算点（仅可购一次），够测 20-50 条短视频 + Seedream 画图。按量计费也行（先充值小额）。

## 参考链接

- 即梦产品页：https://www.volcengine.com/product/jimeng
- 方舟文档：https://www.volcengine.com/docs/82379
- 计费文档：https://www.volcengine.com/docs/86081/1805689（视频/图像套餐表）
