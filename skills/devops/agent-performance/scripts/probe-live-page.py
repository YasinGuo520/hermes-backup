#!/usr/bin/env python3
"""Read-only CDP probe of a live voice-UI page: what the left panel says, whether its input is
covered, and what the browser's own microphone capture actually returns.

Usage: python3 probe-live-page.py [http://127.0.0.1:9223]

Why it exists: on a macOS kiosk voice UI the decisive question is often "does the browser see
audio at all?" — this answers it with a number (rmsPeak) instead of an opinion, and confirms the
console panel renders / is clickable without needing to look at the screen.

Launch a Chrome with a debug port first (do NOT add one to the service's own flags):
  open -na "Google Chrome" --args --kiosk --user-data-dir=$HOME/.apex-kiosk \
    --remote-debugging-port=9223 --remote-allow-origins="*" http://127.0.0.1:3000
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
    covering = el ? (el.tagName + ' | same=' + (el === input)) : 'none';
  }
  const text = document.body.innerText || '';
  const notices = ['连不上桥', '转写失败', '麦克风权限', '录到的是静音', '没听到人声',
                   '太短了', '没答上来', '算太久了', '正在听', '对话中'].filter((k) => text.includes(k));
  return JSON.stringify({
    url: location.href, bodyChars: text.length, panelPresent: !!panel,
    panelRect: panelRect ? [Math.round(panelRect.left), Math.round(panelRect.top),
                            Math.round(panelRect.width), Math.round(panelRect.height)] : null,
    panelTail: panel ? panel.innerText.slice(-400) : '(no CONSOLE panel)',
    inputCoveredBy: covering, notices,
  });
})()
"""

MIC = r"""
(async () => {
  try {
    const s = await navigator.mediaDevices.getUserMedia({ audio: true });
    const t = s.getAudioTracks()[0];
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const an = ctx.createAnalyser();
    an.fftSize = 2048;
    ctx.createMediaStreamSource(s).connect(an);
    const buf = new Float32Array(an.fftSize);
    let peak = 0, sumAll = 0, n = 0;
    for (let i = 0; i < 20; i += 1) {
      await new Promise((r) => setTimeout(r, 100));
      an.getFloatTimeDomainData(buf);
      let sum = 0;
      for (let k = 0; k < buf.length; k += 1) sum += buf[k] * buf[k];
      const rms = Math.sqrt(sum / buf.length);
      peak = Math.max(peak, rms); sumAll += rms; n += 1;
    }
    s.getTracks().forEach((x) => x.stop()); await ctx.close();
    return JSON.stringify({ ok: true, label: t.label, muted: t.muted, state: t.readyState,
                            rmsPeak: Number(peak.toFixed(6)), rmsMean: Number((sumAll / n).toFixed(6)) });
  } catch (e) {
    return JSON.stringify({ ok: false, error: String(e), name: e && e.name });
  }
})()
"""


async def main() -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(CDP_HTTP + "/json/list") as resp:
            targets = await resp.json()
        pages = [t for t in targets if t.get("type") == "page" and "3000" in (t.get("url") or "")]
        if not pages:
            print("!! no page target with :3000")
            return 1
        page = pages[0]
        print("=== probing %s ===" % page["url"])
        async with session.ws_connect(page["webSocketDebuggerUrl"], max_msg_size=0) as ws:
            counter = 0

            async def call(method, params=None, timeout=45):
                nonlocal counter
                counter += 1
                mine = counter
                await ws.send_json({"id": mine, "method": method, "params": params or {}})
                while True:
                    msg = await ws.receive(timeout=timeout)
                    if msg.type != aiohttp.WSMsgType.TEXT:
                        continue
                    data = json.loads(msg.data)
                    if data.get("id") == mine and not data.get("method"):
                        return data

            await call("Runtime.enable")
            for label, expr, await_p in (("DOM", DOM, False), ("MIC (2 s)", MIC, True)):
                out = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True,
                                                     "awaitPromise": await_p})
                res = out.get("result") or {}
                print("%s: %s" % (label, (res.get("result") or {}).get("value")))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
