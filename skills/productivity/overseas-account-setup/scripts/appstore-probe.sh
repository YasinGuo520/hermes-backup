#!/usr/bin/env bash
# 查 App 在各区 App Store 的上架情况 / 价格 / 版本 / 最低系统要求。
# 数据源：Apple 公开接口 itunes.apple.com（境内服务器可直连，无需代理，实测可达）。
#
# 用法:
#   appstore-probe.sh id 6761538521 us cn hk tw jp
#   appstore-probe.sh search "LINE" us cn hk tw
# 默认地区: us cn hk tw jp
#
# 注：接口不给「内购/订阅档位」，那部分只能读商店页面或第三方 App 数据站；
#     同一 App 在 iOS 与 Google Play 上的定价/宣传可能互相矛盾（AB 测试），别当同一套。
set -u
export PYTHONIOENCODING=utf-8

MODE="${1:-}"
if [ -z "$MODE" ]; then
  echo "用法: $0 id <trackId> [country...] | $0 search <关键词> [country...]" >&2
  exit 2
fi
shift
KEY="${1:-}"
if [ -z "$KEY" ]; then echo "缺少 trackId / 关键词" >&2; exit 2; fi
shift

COUNTRIES=("$@")
if [ ${#COUNTRIES[@]} -eq 0 ]; then COUNTRIES=(us cn hk tw jp); fi

if [ "$MODE" = "id" ]; then
  TMPL='https://itunes.apple.com/lookup?id=%s&country=%s'
else
  TMPL='https://itunes.apple.com/search?term=%s&entity=software&limit=10&country=%s'
fi

Q=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$KEY")

for c in "${COUNTRIES[@]}"; do
  url=$(printf "$TMPL" "$Q" "$c")
  curl -s --max-time 25 "$url" | MODE="$MODE" KEY="$KEY" COUNTRY="$c" python3 -c '
import os,json,sys
mode=os.environ["MODE"]; key=os.environ["KEY"].strip().lower(); c=os.environ["COUNTRY"]
try:
    d=json.load(sys.stdin)
except Exception as e:
    print(c+": 拉取/解析失败 "+str(e)); sys.exit()
rs=d.get("results",[])
if not rs:
    print(c+": 无结果（该区未上架/搜不到）"); sys.exit()
if mode=="id":
    hit=rs[0]
else:
    hit=next((r for r in rs if r.get("trackName","").strip().lower()==key), None)
if hit is None:
    print(c+": 无同名精确匹配，前3个: "+" / ".join(r.get("trackName","") for r in rs[:3])); sys.exit()
parts=[hit.get("trackName"),hit.get("sellerName"),hit.get("formattedPrice"),
       "v"+str(hit.get("version")),"iOS "+str(hit.get("minimumOsVersion")),
       "评分 "+str(hit.get("averageUserRating"))+"("+str(hit.get("userRatingCount"))+")",
       "更新 "+str(hit.get("currentVersionReleaseDate"))[:10]]
print(c+": "+" | ".join(str(p) for p in parts))
'
done
