# Blocked-Page Recovery (merged from `blocked-page-recovery` skill)

When a page won't fetch — 403/429, Cloudflare "Just a moment...", a paywall, or a bot-detection interstitial — don't give up and don't loop on the same URL. Third-party services often hold a **copy** of the page. Work down this ladder, cheapest first.

## The ladder

```
1. Wayback Machine  — archive.org "available" API  (snapshot + timestamp)
2. archive.today    — domain rotation: archive.ph → .md → .li → .is
3. Jina Reader      — only if JINA_API_KEY is set  (live server-side render)
4. API-first pivot  — look for /api/, /graphql, .json, or RSS on the same host
5. Real browser     — browser tool as the last, most expensive resort
```

Run it in one shot: `python3 scripts/recover_page.py "https://example.com/blocked-article" --json`
(script lives in this skill's `scripts/`; tries each route in order, validates every body, prints the first genuine hit with provenance).

## Provenance discipline (non-negotiable)

| Route | Provenance | How to cite |
|-------|-----------|-------------|
| Wayback / archive.today | `snapshot` | Cite WITH the snapshot date: "as archived 2026-08-06". Never present a snapshot as the live page — it may be stale. |
| Jina Reader | `live` | Server-side re-render of the live page; cite normally. |
| Live fetch / browser | `live` | Cite normally. |

If the user needs *current* data (prices, availability, breaking news), a snapshot is context, not an answer — say so explicitly and note its age.

## Manual routes

### 1. Wayback Machine (best provenance, try first)

```bash
curl -sL "https://archive.org/wayback/available?url={URL}"   # discovery, returns closest snapshot
curl -sL "https://web.archive.org/cdx/search/cdx?url={URL}&output=json&limit=10"  # enumerate many snapshots
```

CDX intermittently returns 503 under load — fall back to the `available` API, don't retry-hammer it.
Works for: any publicly crawled URL. Fails for: robots-blocked sites, never-crawled URLs, JS-only SPAs.

### 2. archive.today (paywalls, deleted content)

Rate-limits aggressively (429) and rotates domains, so iterate:

```bash
for d in archive.ph archive.md archive.li archive.is; do
  curl -sL --max-time 20 "https://$d/newest/{URL}" -o /tmp/page.html -w "%{http_code}" && break
done
```

**Validate the body, not the status code** — a 429 still ships several KB of rate-limit HTML.

### 3. Jina Reader (requires JINA_API_KEY)

`r.jina.ai` re-renders the live page in a real browser server-side and returns markdown. Anonymous access is dead (401 → Turnstile); a key is required:

```bash
curl -s -H "Authorization: Bearer $JINA_API_KEY" "https://r.jina.ai/{URL}"
```

Skip this route entirely when the env var is unset.

### 4. API-first pivot

WAFs protect the HTML surface far more aggressively than the data endpoints behind it. After 2-3 blocked attempts on a site, stop fighting the HTML and look for:

- `/api/...`, `/graphql`, or `.json` variants of the page URL
- An RSS/Atom feed (`/feed`, `/rss`, `<link rel="alternate">` in any copy you did recover)
- A sitemap (`/sitemap.xml`) revealing canonical URLs that may not be gated

## Fake successes — routes that LIE

These return HTTP 200 with a plausible body that is NOT the page. The script rejects them automatically; reject them manually too:

- **Google Cache is dead** (since mid-2024). `webcache.googleusercontent.com` returns 200 + tens of KB, but it's a Google Search interstitial with a JS redirect, not a cache. Never use it.
- **AMP caches** (`*.cdn.ampproject.org`) mostly return a ~300-byte `<title>Redirecting</title>` meta-refresh stub pointing back at the original (blocked) URL → fetch loop.
- **Rate-limit bodies**: archive.today 429 pages are multi-KB HTML. Check for the target's actual content (title words, expected strings), not just size.

Detection heuristics: body under a per-route byte floor; meta-refresh/JS-redirect stubs whose target is the original host; interstitial titles ("Just a moment", "Redirecting", "Google Search", "Attention Required").

## Proxy relays: don't

Generic "web proxy" relays are man-in-the-middle by construction. Never send cookies or Authorization headers through one, and don't use them for anything the user will rely on — provenance is unverifiable. Prefer archives, which at least timestamp their copies.

## Related

- `grounded-citations` (bundled): when presenting recovered content, keep the provenance visible.
- This skill's main body: Scrapling/Playwright crawling — use the ladder here when those fetch attempts are blocked.