#!/usr/bin/env python3
"""Read-only probe of the live orb page over CDP.

  python probe-live-page.py http://127.0.0.1:9223

Answers with measurements instead of guesses:
  * does the left CONSOLE panel exist, what does it say, is anything covering its input?
  * which notice strings are on screen (bridge unreachable / transcription failed / no speech)?

Launch the instance it talks to with a dedicated profile, e.g.
  open -na "Google Chrome" --args --kiosk --window-position=-248,-1080 --window-size=1920,1080 \
      --user-data-dir=$HOME/.apex-kiosk --remote-debugging-port=9223 --remote-allow-origins=* \
      --no-first-run --no-default-browser-check http://127.0.0.1:3000
(the user's everyday Chrome often answers 404 on /json/*; use a fresh profile.)
"""
import asyncio
import json
import sys

import aiohttp

CDP_HTTP = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:9223"

DOM = r"""
(() => {
  const all = [...document.querySelectorAll('div')];
  const panel = all.find((d) => d.innerText && d.innerText.startsWith('CONSOLE'));
  const panelRect = panel ? panel.getBoundingClientRect() : null;
  const input = panel ? panel.querySelector('input') : null;
  let covering = null;
  if (input) {
    const r = input.getBoundingClientRect();
    const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    covering = el ? (el.tagName + '.' + (el.className || '') + ' | same=' + (el === input)) : 'none';
  }
  const text = document.body.innerText || '';
  const notices = ['连不上桥', '转写失败', '麦克风权限', '录到的是静音', '没听到人声',
                   '太短了', '没答上来', '算太久了', '正在听', '对话中'].filter((k) => text.includes(k));
  return JSON.stringify({
    url: location.href,
    bodyChars: text.length,
    panelPresent: !!panel,
    panelRect: panelRect ? [Math.round(panelRect.left), Math.round(panelRect.top),
                            Math.round(panelRect.width), Math.round(panelRect.height)] : null,
    panelTail: panel ? panel.innerText.slice(-400) : '(no CONSOLE panel)',
    inputCoveredBy: covering,
    notices,
  });
})()
"""


async def main() -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(CDP_HTTP + "/json/list") as resp:
            targets = await resp.json()
        print("=== CDP targets ===")
        for t in targets:
            print("  %-8s %-60s %s" % (t.get("type"), (t.get("url") or "")[:60],
                                       (t.get("title") or "")[:40]))
        pages = [t for t in targets if t.get("type") == "page" and "3000" in (t.get("url") or "")]
        if not pages:
            print("!! no page target with :3000 — the orb page is not open")
            return 1
        page = pages[0]
        print("\n=== probing %s ===" % page["url"])
        events = []
        async with session.ws_connect(page["webSocketDebuggerUrl"], max_msg_size=0) as ws:
            counter = 0

            async def call(method, params=None, timeout=40):
                nonlocal counter
                counter += 1
                mine = counter
                await ws.send_json({"id": mine, "method": method, "params": params or {}})
                while True:
                    msg = await ws.receive(timeout=timeout)
                    if msg.type != aiohttp.WSMsgType.TEXT:
                        continue
                    data = json.loads(msg.data)
                    if data.get("method"):
                        events.append(data)
                        continue
                    if data.get("id") == mine:
                        return data

            await call("Runtime.enable")
            await call("Log.enable")
            out = await call("Runtime.evaluate", {"expression": DOM, "returnByValue": True})
            res = out.get("result") or {}
            print("DOM:", (res.get("result") or {}).get("value"))
            if res.get("exceptionDetails"):
                print("   exception:", json.dumps(res["exceptionDetails"])[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
