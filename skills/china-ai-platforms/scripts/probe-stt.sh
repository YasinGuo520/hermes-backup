#!/bin/bash
# 语音转写（ASR）链路探针：只读，不改配置，只回答「转写这一层通不通、不通是为什么」。
# 用法（在跑语音服务的机器上执行）：bash probe-stt.sh ["要合成的中文句子"]
# 配套说明：references/asr-stt-provider-triage.md
set -u

CONFIG="${HERMES_CONFIG:-$HOME/.hermes/config.yaml}"
TEXT="${1:-帮我看下今天的抖音罗盘数据}"
VENV="$HOME/.hermes/hermes-agent/venv/bin/python"
FFMPEG=/usr/local/bin/ffmpeg
command -v ffmpeg >/dev/null 2>&1 && FFMPEG="$(command -v ffmpeg)"

# 1) 造真实语音样本。纯静音 WAV 会被供应商回 "no audio segment found" —— 假阴性，别用它下结论。
WAV=/tmp/probe-stt.wav
if say -v Tingting -o /tmp/probe-stt.aiff "$TEXT" 2>/dev/null || say -o /tmp/probe-stt.aiff "$TEXT" 2>/dev/null; then
  "$FFMPEG" -y -i /tmp/probe-stt.aiff -ar 16000 -ac 1 -c:a pcm_s16le "$WAV" >/dev/null 2>&1
fi
ls -l "$WAV" 2>/dev/null || { echo "!! 没生成 $WAV（音色不在本机？ffmpeg 路径？）"; exit 1; }

# 2) 用服务真正在读的那份配置（Hermes 语音链路读 stt.<provider> 段）。
CFG=$("$VENV" - "$CONFIG" <<'PY'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
stt = cfg.get("stt") or {}
p = stt.get("provider") or ""
s = stt.get(p) or {}
print("\t".join([p, (s.get("base_url") or "").rstrip("/"),
                 s.get("api_key") or "", s.get("model") or ""]))
PY
)
IFS=$'\t' read -r PROVIDER BASE_URL API_KEY MODEL <<<"$CFG"
echo "provider=$PROVIDER  model=$MODEL  key=${API_KEY:0:6}***(len ${#API_KEY})"

# 3) local 通道不走 HTTP：直接验本地 faster-whisper（依赖/模型自检见 reference）。
if [ "$PROVIDER" = "local" ]; then
  "$VENV" - "$WAV" "${MODEL:-base}" <<'PY'
import sys, time
from faster_whisper import WhisperModel
t = time.time()
m = WhisperModel(sys.argv[2], device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], language="zh")
print("ASR: " + "".join(s.text for s in segs))
print("transcribe %.1fs" % (time.time() - t))
PY
  exit 0
fi

[ -n "$BASE_URL" ] || { echo "!! config.yaml 的 stt.$PROVIDER 段没有 base_url（上层会报 provider not configured）"; exit 1; }

# 4) 真打一发：状态码只说类别，body 写明原因（402 的 body 就是「余额不足」）。
echo "--- POST $BASE_URL/audio/transcriptions ---"
curl -s --max-time 25 -w $'\nHTTP=%{http_code}\n' \
  -X POST -H "Authorization: Bearer $API_KEY" \
  -F "file=@$WAV;type=audio/wav" -F "model=$MODEL" \
  "$BASE_URL/audio/transcriptions"
