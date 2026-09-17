#!/usr/bin/env bash
# gemini-key-probe.sh — 一条命令判定一条 Gemini API key：能用 / 不能用 / 为什么不能用
#
# 用法:  bash gemini-key-probe.sh <API_KEY> [代理端口=7897]
#
# 环境铁律（本仓库实测约定）：
#   * 必须在「能访问 Google 的机器」上跑 = 用户 Mac + Clash Verge 代理。
#     Clash Verge 实测 mixed port 是 **7897**（7890 不通）；国内服务器直连 Google 全超时，跑不出结论。
#   * 跨机跑法：scp 本脚本到 Mac 后 `ssh mac@<IP> 'bash /tmp/gemini-key-probe.sh <KEY> 7897'`。
#
# 判定要点（本脚本存在的理由）：**能列出模型 ≠ 能调用**。
#   key 有效但项目被封时：/models 返回 200，generateContent 返回 403 PERMISSION_DENIED
#   "Your project has been denied access" → 是项目级问题（地区/试用未完成/风控），不是 key 写错。
set -uo pipefail

KEY="${1:?用法: gemini-key-probe.sh <API_KEY> [代理端口]}"
PORT="${2:-7897}"
P="http://127.0.0.1:${PORT}"
BASE="https://generativelanguage.googleapis.com/v1beta"

echo "== 0) 代理连通性 (${P})"
code=$(curl -s -o /dev/null -w '%{http_code}' -m 15 -x "$P" https://www.google.com)
if [ "$code" = "000" ]; then
  echo "   ❌ 代理 ${P} 不通 —— 先解决节点/端口再谈 key（Clash Verge mixed port 实测 7897）"
  exit 2
fi
echo "   google.com = $code"

echo "== 1) 认证 + 列模型（200 = key 本身有效）"
curl -s -m 20 -x "$P" "$BASE/models?key=$KEY" -o /tmp/gk_models.json -w '   http=%{http_code}\n'
python3 - <<'PY'
import json
p='/tmp/gk_models.json'
try:
    d=json.load(open(p))
except Exception:
    print('   ⚠️ 响应不是 JSON（多半是网络/代理问题，不是 key 问题）'); raise SystemExit
d=d if isinstance(d,dict) else {}
if 'error' in d:
    e=d['error']; msg=(e.get('message') or '')
    print(f"   ❌ {e.get('code')} {e.get('status')}: {msg[:160]}")
    if 'API_KEY_INVALID' in msg or 'API key not valid' in msg:
        print('      → key 本身无效（复制错 / 已删除 / 不是 Gemini 的 key）')
    raise SystemExit
names=[m['name'].replace('models/','') for m in d.get('models',[])
       if 'generateContent' in m.get('supportedGenerationMethods',[])]
print(f'   ✅ key 有效，可调用模型 {len(names)} 个')
pref=['gemini-3.8-flash','gemini-3.7-flash','gemini-3.6-flash','gemini-3.5-flash',
      'gemini-3.1-pro-preview','gemini-flash-latest']
pick=next((x for x in pref if x in names), None) or next((n for n in names if 'flash' in n), None)
open('/tmp/gk_pick.txt','w').write(pick or '')
print(f'   → 用 {pick} 做调用测试（2.5 系列已对新用户下线，别再用 gemini-2.5-flash）')
PY
MODEL=$(cat /tmp/gk_pick.txt 2>/dev/null)
[ -z "$MODEL" ] && { echo '❌ 列表里没有可调用的模型，停止'; exit 1; }

echo "== 2) 真实调用（200 = 真的能用）"
curl -s -m 60 -x "$P" -X POST "$BASE/models/$MODEL:generateContent?key=$KEY" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"只回复：OK"}]}],"generationConfig":{"maxOutputTokens":32}}' \
  -o /tmp/gk_gen.json -w '   http=%{http_code}\n'
python3 - <<'PY'
import json
d=json.load(open('/tmp/gk_gen.json'))
if 'error' in d:
    e=d['error']; msg=(e.get('message') or '')
    print(f"   ❌ {e.get('code')} {e.get('status')}: {msg[:200]}")
    if 'denied access' in msg:
        print('      → 项目级被封（不是 key 问题）：地区不受支持 / 试用未完成 / 风控')
        print('        官方口径：403 = 使用方式不符合 ToS，常见原因是所在地区不受支持')
        print('        下一步：aistudio.google.com 左侧 Projects 页看红色横幅；GCP 项目国家不可改')
    elif 'no longer available' in msg:
        print('      → 该模型已下线，换更新的 flash 模型名重试')
    elif 'RESOURCE_EXHAUSTED' in msg or e.get('code')==429:
        print('      → 额度用尽（免费层按天刷新，或已切付费结算）')
    raise SystemExit(1)
c=(d.get('candidates') or [{}])[0]
txt=''.join(p.get('text','') for p in c.get('content',{}).get('parts',[]))
print('   ✅ 调用成功:', txt[:80].replace('\n',' '))
print('   tokens:', (d.get('usageMetadata') or {}).get('totalTokenCount'))
PY
