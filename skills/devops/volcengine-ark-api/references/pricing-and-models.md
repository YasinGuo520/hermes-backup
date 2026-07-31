# 火山方舟 价格表与模型ID清单

> 数据核实日期：2026-07。价格以火山引擎官网为准，调用前复核。
> 用户账号 2106785487，ARK_API_KEY 在 ~/backend/.env。

## 视频生成价格（按量计费，元/秒）

| 模型 | 分辨率 | 单价 | 备注 |
|------|--------|------|------|
| Seedance 1.0 mini | 480P | 0.1 | 5秒=0.5元 |
| Seedance 1.0 mini | 720P | 0.2 | 5秒=1元 |
| Seedance 1.0 | 720P | 0.28 | |
| Seedance 1.0 | 1080P | 0.7 | |
| **Seedance 1.0 Pro-fast** | 720P | **0.08** | 日常带货首选，性价比最高 |
| Seedance 1.5 Pro | 720P 有声 | 0.344 | 质感档 |
| Seedance 1.5 Pro | 720P 无声 | 0.172 | |
| Seedance 2.0 | 720P | ~1.6-2.0 | 增强版 2元/秒，需充值开通 |
| 数字人 OmniHuman | - | 1.0 | |

一条 15 秒带货视频成本估算：
- Seedance 1.0 Pro-fast 720P：约 1.2元
- Seedance 1.5 Pro 720P 有声：约 5.2元
- Seedance 2.0：约 15-30元

## 新手套餐

- **基础体验版：¥100/月（1000算点）**——够测 20-50 条短视频，含 Seedream 画图 + ComfyUI
- 一个账号同时只生效一个套餐，不支持退订，谨慎选购
- 新用户一般有免费 token 额度

## 常用模型ID（2026-07 已确认存在）

### 视频生成
- `doubao-seedance-2-5-260628` — 最新（Seedance 2.5）
- `doubao-seedance-2-0-260128` — 2.0 增强版，支持多模态参考/编辑/延长
- `doubao-seedance-2-0-fast-260128` — 2.0 fast
- `doubao-seedance-2-0-mini-260615` — 2.0 mini
- `doubao-seedance-1-5-pro-251215` — 1.5 Pro 有声
- `doubao-seedance-1-0-pro-fast-251015` — 1.0 Pro-fast（最便宜）
- `doubao-seedance-1-0-pro-250528` — 1.0 Pro

### 图像生成
- `doubao-seedream-5-0-pro-260628` — 最新
- `doubao-seedream-5-0-260128`
- `doubao-seedream-4-5-251128`

### 豆包对话（LLM/VLM）
- `doubao-seed-2-1-pro-260628` / `doubao-seed-2-1-turbo-260628`
- `doubao-seed-2-0-pro-260215` / `doubao-seed-2-0-lite-260215`
- `doubao-seed-1-8-251228`
- 也托管 DeepSeek V4：`deepseek-v4-flash-260425`、`deepseek-v4-pro-260425`（100万上下文）

## 与硅基流动的边界

- 硅基流动 = 开源模型聚合站：Kimi K3、DeepSeek、Qwen、GLM、FLUX、Qwen-Image/Kolors 全有
- Kimi K3 在硅基流动有：输入 $3/M、输出 $15/M，模型ID `kimi-k3`
- 硅基流动**没有**：豆包系、即梦、Seedance（闭源）→ 这些走火山方舟
- GPT/Claude/Gemini 两家都没有 → 官方 API，墙内不稳

## 已知坑

1. 普通 API Key（无 ark- 前缀）调方舟接口 → 401；必须「方舟大模型专用 API Key」
2. 视频生成接口路径是 `generations` 不是 `generators`（拼错→404空body）
3. Seedance 开通前置：需先充值/购买资源包；豆包对话模型开通不需要充值
4. 生成的视频 URL 24h 过期，要及时转存本地
