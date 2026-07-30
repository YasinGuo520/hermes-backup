# Free Web Template Sources (Accessible from Tencent Cloud Server)

Tested 2026-07-31 from 43.138.221.174 (Tencent Cloud LightServer). All sites
with ✅ are accessible for direct download and preview.

## 🇨🇳 Chinese Sites

| Site | Status | Type | Notes |
|------|--------|------|-------|
| 17sucai.com | ✅ 200 | Free + VIP | Some free, some need credits |
| sc.chinaz.com | ✅ 200 | Free | 站长素材,国内知名 |

## 🌐 International Sites (preferred — no login, direct ZIP)

| Site | Status | Notes |
|------|--------|-------|
| html5up.net | ✅ 200 | **Best choice.** High quality, direct ZIP download |
| templated.co | ✅ 200 | Free responsive templates |
| tooplate.com | ✅ 200 | 200+ free templates |
| startbootstrap.com | ✅ 200 | Bootstrap-based, clean |
| themewagon.com | ✅ 200 | Free + premium |
| zerotheme.com | ✅ 200 | Bootstrap templates |
| colorlib.com | ✅ 200 | 500+ free, requires email |

## Direct Download Pattern (html5up)

```bash
# Template names are lowercase with hyphens
curl -sL https://html5up.net/[template-name]/download -o /tmp/name.zip
unzip -q /tmp/name.zip -d /tmp/name/
```

Popular tech/AI style templates from html5up:
- `stellar` — 科技蓝风,简洁大气
- `forty` — 暗色科技风,酷炫
- `paradigm-shift` — 现代极简
- `massively` — 现代杂志
- `dimensions` — 全屏科技

## Blocked Sites

These return 000/403 from this server:
- mobanwang.com (模板王) — **completely blocked**, no access at all
- themeforest.net — 403
- bootstrapmade.com — 403
- free-css.com — 000 (timeout)

## Workflow

1. User provides a reference URL or asks for a template
2. Check if the URL is accessible (curl -s --connect-timeout 8 -o /dev/null -w "%{http_code}" URL)
3. If from html5up: download ZIP directly, deploy on a temp port (8890-8899 range)
4. If from 17sucai/chinaz: open in browser to preview, user can download and send
5. Once user picks a template, copy its assets/ directory and index.html to the project
6. Modify the HTML content but keep the CSS/design intact — do NOT recreate from scratch
