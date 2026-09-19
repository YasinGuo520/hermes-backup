# 语音转写（ASR/STT）链路的分层诊断与供应商切换

适用：任何「语音功能说没听清/反复要求重说/转写为空」的报障。**先定位在哪一层，再选供应商**——
麦克风层和转写层是两个完全不同的诊断路径，混着修是最贵的绕路。

## 一、分层判据（按顺序，别跳）

| 层 | 看什么 | 健康值 | 挂了的样子 |
|---|---|---|---|
| 采音 | 桥/客户端日志的 `speech=XXXXms`、`rms=0.0X` | 秒级 speech、rms 0.0x | `speech=0ms`、每次字节数恒定的「数字静音包」= 权限问题 |
| 转写 | provider 的 **HTTP 状态码 + 原始 body** | 200 + 文本 | 4xx/5xx；重试 3 次后放弃并播固定台词 |
| 后处理守卫 | 反幻觉/语速合理性判定 | 保留正常短句 | 误杀真实短句（分母用「检测到的人声时长」会偏小） |

**用户说的「她听不到我」经常是转写层**：台词（「没听清，再说一遍」之类）是程序里的固定常量，
只在转写全失败时才播。看到它就去查 provider，别顺着麦克风查权限/门限/浏览器。

## 二、抄原始响应体，别只看状态码

状态码只说类别，body 写明原因。用同一份线上配置打一发真实请求（**要真实语音样本**，
纯静音 WAV 会被回 `no audio segment found` 之类的假阴性）：

```bash
say -v Tingting -o /tmp/sp.aiff "帮我看下今天的抖音罗盘数据"   # macOS；Linux 用 ffmpeg flite
ffmpeg -y -i /tmp/sp.aiff -ar 16000 -ac 1 -c:a pcm_s16le /tmp/sp.wav
curl -s --max-time 25 -w '\nHTTP=%{http_code}\n' -X POST \
  -H "Authorization: Bearer $KEY" \
  -F "file=@/tmp/sp.wav;type=audio/wav" -F "model=$MODEL" \
  "$BASE_URL/audio/transcriptions"
```

已见过的 body 语义：

| body | 含义 | 处置 |
|---|---|---|
| `code 30001 Sorry, your account balance is insufficient`（HTTP 402 Payment Required） | 供应商账户余额/欠费 | 计费问题，与网络、音频格式、采样率无关；换通道或充值 |
| `code 20092 endpoint deprecated`（余额查询端点） | **别指望余额查询接口**：硅基 `/v1/user/info` 已废弃 | 余额只能从转写接口的回包确认 |
| `Token is invalid` / 401 | key 不对（常见于读到空值或读错了配置文件） | 确认 key 出自「服务真正在读的那份配置」 |
| `no audio segment found` | 音频里没人声（测试样本是静音） | 换真实语音重测，别下结论 |

## 三、配置只有一处，别找第二把 key

同一个 provider 配置常被多条链路共用（桌面端语音输入、独立语音 UI 的桥、飞书/微信语音条），
它们都从**同一份 Hermes `config.yaml` 的 `stt.<provider>` 段**取 `base_url`/`api_key`/`model`。
含义有两层：

1. **一次故障 = 多条链路同时瞎**。查一个渠道报障时，把同源渠道一起验，报告里点明影响面。
2. **测的时候用同一份配置打**。`~/.hermes/.env` 里的同名 key 可能与 config 里那把不是同一把，
   以「服务实际读的那份」为准（读桥/客户端的取配置函数，不要猜）。

## 四、通道对照（中国大陆可直连）

| 通道 | 接入 | 实测 | 代价 |
|---|---|---|---|
| 硅基流动 OpenAI 兼容转写（Qwen 系 ASR） | `base_url: https://api.siliconflow.cn/v1`，`model: Qwen/Qwen3-ASR-1.7B` 或 `FunAudioLLM/SenseVoiceSmall` | 正常时精度最好 | 按量计费；**欠费即 402，静默失败** |
| 智谱 `glm-asr` | `base_url: https://open.bigmodel.cn/api/paas/v4`，`model: glm-asr`，OpenAI 兼容文件上传 | HTTP 200、中文识别正确 | 有免费额度；额度耗尽同样静默失败 |
| 本地 faster-whisper | `stt.provider: local` + `stt.local.model: base/small`；模型来自 HF 缓存 | Intel CPU：base 载入 3.6s/转写 1.5s，small 3.9s/3.3s | **唯一不会因计费静默失效**；慢 1~2s、精度略逊 |

选型原则：**止血用本地（0 成本、离线、永不欠费），要精度再上云**。切通道是配置变更 →
先给用户「方案 + 推荐 + 代价」对照，拿到明确同意再改，别顺手改配置。

依赖自检（切 local 前）：
```bash
~/.hermes/hermes-agent/venv/bin/python -c "import faster_whisper;print(faster_whisper.__version__)"
ls ~/.cache/huggingface/hub | grep -i whisper      # 模型是否已在本地
```
