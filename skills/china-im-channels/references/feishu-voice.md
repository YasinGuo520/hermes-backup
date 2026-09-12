# 飞书语音：入站转写（说话）+ 出站语音气泡（回话）

> 场景：Yasin 想「直接语音跟我对话」——手机飞书按住说话，Hermes 听懂并用语音回。
> 2026-09-12 在腾讯云服务器（国内）上从零打通并实测。

## 先确认飞书支不支持语音（答案是支持）

| 证据 | 位置 |
|---|---|
| 平台能力矩阵 `Feishu/Lark \| ✅(Voice) \| ✅ \| ✅ \| ✅ \| ✅ \| ✅ \| ✅` | 官方 docs「Platform Comparison」 |
| Lark 原生 `audio` msg_type = 语音条 → 归类为 `MessageType.VOICE` → 网关自动转写 | `plugins/platforms/feishu/adapter.py` + 回归测试 `tests/gateway/test_feishu_voice_message_type.py` |
| 出站 `send_voice()`：飞书只收 **Opus**，非 opus 自动 ffmpeg 转码成语音条 | `plugins/platforms/feishu/adapter.py:2241` |
| 网关侧把 VOICE 当语音输入处理 → 调 `transcribe_audio(path, None, "gateway")`，失败再走 `transcribe_audio_local_fallback` | `gateway/run.py:26726` |

所以「飞书没有语音输入」通常是**用户端 UI**（电脑端飞书给机器人不一定放语音入口）或**服务端 STT 没配**，不是飞书不支持。

## 国内服务器上最容易踩的两个坑（都实测过）

1. **`stt.language` 默认 `en`** → 中文短语音会被转成英文/乱码。中文用户必须显式设 `zh`。
2. **没设 `stt.provider` 时会回退 local faster-whisper**，而本地模型要联网从 HuggingFace 拉权重 →
   国内服务器拉不动 → 转写**直接失败**：
   ```
   huggingface_hub.errors.LocalEntryNotFoundError: An error happened while trying to locate
   the files on the Hub and we cannot find the appropriate snapshot folder ...
   provider: None | 成功: False
   ```
   `faster_whisper` 包本身装着（`import faster_whisper` OK）也会挂在这一步——**别把「包装了」当成「能转写」**。

## 修法：STT 走硅基流动 Qwen3-ASR（中文优化、有 Key 就能用）

```bash
KEY=$(grep -m1 "^SILICONFLOW_API_KEY=" ~/.hermes/.env | cut -d= -f2- | tr -d '"'"'"' "'"')
hermes config set stt.provider openai
hermes config set stt.language zh
hermes config set stt.openai.model    "Qwen/Qwen3-ASR-1.7B"
hermes config set stt.openai.base_url "https://api.siliconflow.cn/v1"
hermes config set stt.openai.api_key  "$KEY"
hermes config set stt.openai.language zh
hermes config set tts.edge.voice zh-CN-XiaoyiNeural   # 默认是 en-US-AriaNeural，念中文很怪
```

- `openai` provider 就是「任意 OpenAI 兼容 STT 端点」的通用形状，`stt.openai.api_key/base_url` 直接写在 config.yaml
  （Mac 上已验证的那套就是这么配的，照抄即可）。
- 改前先 `cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-stt-$(date +%Y%m%d%H%M)`。
- **不用重启网关**：`tools/transcription_tools.py` 的 `_load_stt_config()` 每次调用都 `load_config()`（约 167 行），
  STT/TTS 配置即时生效。省掉在网关会话里重启自杀的风险（见 SKILL.md「重启网关」节）。

## 验收（无真人也能跑，30 秒出结论）

用 edge-tts 造一段中文，再喂给网关用的同一个函数：

```bash
cd ~/.hermes/hermes-agent && V=./venv/bin/python
$V -m edge_tts --voice zh-CN-XiaoyiNeural \
   --text "帮我看看今天抖音热榜有没有适合卖的新品" --write-media /tmp/zh_test.mp3
$V -c "
import sys; sys.path.insert(0,'/home/ubuntu/.hermes/hermes-agent')
from tools.transcription_tools import transcribe_audio
r = transcribe_audio('/tmp/zh_test.mp3', None, 'test')
print('provider:', r.get('provider'), '| 成功:', r.get('success')); print(r.get('transcript'), r.get('error'))
"
```

合格线：`provider: openai | 成功: True` + 转写文本与原文一致（实测字字对齐）。
修前同一条命令是 `成功: False` + LocalEntryNotFoundError——**A/B 对比就是证据**。

出站侧验收：`text_to_speech` 工具生成一条中文语音，看返回的 `provider: edge` + `voice_compatible: true`，
发给用户听。

## 用户侧怎么用

| 要什么 | 做什么 |
|---|---|
| 我发语音，Hermes 听懂 | 手机飞书输入框左侧「按住说话」（电脑端可能无此入口，让用户用手机） |
| 我发语音，Hermes 用语音回 | 聊天框发一条 **`/voice on`**（= `voice_only` 模式） |
| 所有回复都要语音 | `/voice tts`；关掉 `/voice off`；`/voice status` 查当前 |

语音模式设置**跨网关重启保留**。`/voice` 家族在 Telegram/Discord 文档里，飞书走同一套网关实现。
