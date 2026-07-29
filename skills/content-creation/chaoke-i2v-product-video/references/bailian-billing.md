# 百炼（DashScope）账单与成本追踪

## 核心事实

- 百炼是**后付费**模式：先调用，后出账，月初结算
- `bl usage stats` 需要 `bl auth login --console` 才能查询（API key 模式查不了用量统计）
- 欠费后 API **不会报错**——仍然返回 200，费用继续累积直到阿里云停服
- 账单需要在 [百炼控制台 - 计费管理](https://bailian.console.aliyun.com) 查看

## 常见模型单价（2026年7月）

| 模型 | 用途 | 单价 |
|------|------|------|
| happyhorse-1.1-i2v | 图生视频 | ¥0.06/次 |
| happyhorse-1.1-t2v | 文生视频 | ¥0.06/次 |
| wan2.2-i2v-flash | 图生视频（旧版） | ¥0.06/次 |
| qwen-image / wan2.7-image | 文生图 | ¥0.08/次 |
| qwen3-tts-flash | 语音合成 | ¥0.015/千字符 |
| bl file upload | 文件上传 | 免费（48h有效期） |

## 对比：百炼 vs 硅基（SiliconFlow）

| 维度 | 百炼（DashScope） | 硅基（SiliconFlow） |
|------|-------------------|---------------------|
| I2V 模型 | happyhorse-1.1-i2v ¥0.06 | Wan2.2-I2V-A14B $0.29（≈¥2.1） |
| 命令行工具 | `bl` CLI | curl / SDK |
| 计费模式 | 后付费月结 | 预付费扣余额 |
| 适合场景 | 高频低成本批量出片 | 高质量单次生成 |

## 用户常见误解

- **"为什么走百炼不是硅基？"** — 因为 happyhorse 模型只有百炼有，硅基没有
- **"百炼欠费了是不是硅基的钱？"** — 两个平台独立计费，互不相干
- **"今天花了多少钱？"** — 无法从 CLI 查到精确数字，需要去控制台看

## 检查方法

### CLI 能查到的
```bash
bl auth status           # 检查 API key 是否有效
bl usage free --model happyhorse-1.1-i2v  # 查免费额度（需要console登录）
```

### CLI 查不到的
- 今天具体消费金额
- 当前欠费余额
- 历史账单明细

以上都需要去 [百炼控制台](https://bailian.console.aliyun.com) 查看。
