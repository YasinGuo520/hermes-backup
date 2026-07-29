# 硅基流动（SiliconFlow）配置 Hermes 看图能力

## 适用场景

Hermes 主力模型不支持视觉（如 DeepSeek 系），需要为 `vision_analyze` 工具配一个辅助视觉模型。

## 方案：通过 OpenAI 兼容接口使用 SiliconFlow

SiliconFlow 提供 OpenAI 兼容 API，支持 Qwen3-VL 系列看图模型，国内网络直连。

### 配置步骤

#### 1. 获取 API Key

在 [siliconflow.cn](https://siliconflow.cn) 注册 → API 密钥 → 创建密钥

#### 2. 在 config.yaml 配置

用命令设置（推荐）：
```bash
hermes config set auxiliary.vision.provider openai
hermes config set auxiliary.vision.base_url https://api.siliconflow.cn/v1
hermes config set auxiliary.vision.model Qwen/Qwen3-VL-32B-Instruct
hermes config set auxiliary.vision.api_key sk-你的key
```

或手动编辑 config.yaml：
```yaml
auxiliary:
  vision:
    provider: openai
    base_url: https://api.siliconflow.cn/v1
    model: Qwen/Qwen3-VL-32B-Instruct
    api_key: sk-你的key
```

#### 3. 生效

需要新会话（`/reset`）使 auxiliary 配置生效。

### 验证

```bash
curl -s https://api.siliconflow.cn/v1/models \
  -H "Authorization: Bearer sk-你的key" | python3 -m json.tool | grep "VL"
```

### 可用模型（推荐排序）

| 模型 ID | 说明 |
|---------|------|
| `Qwen/Qwen3-VL-32B-Instruct` | 推荐，效果最好 |
| `Qwen/Qwen3-VL-8B-Instruct` | 轻量版，更快 |
| `Qwen/Qwen2.5-VL-7B-Instruct` | 旧版，兼容性尚可 |

### 注意事项

- ⚠️ `provider: openai` 配合 `base_url` 会替代默认 OpenAI API 地址
- ⚠️ 若 .env 已有 `OPENAI_API_KEY` 指向别处，在 config 中单独写 `api_key` 隔离，不污染全局
- 费用：SiliconFlow 按 Tokens 计费，注册通常有免费额度
