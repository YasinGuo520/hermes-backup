#!/usr/bin/env python3
"""Clone a live launchd plist into a throw-away sibling job.

Why this exists: on macOS an ssh- or terminal-started copy of a mic-reading script opens
sd.InputStream fine, prints "listening...", and then hears SILENCE - the microphone grant is
recorded for the binary as launched in the Aqua session. Neutrally acceptance-testing audio
code therefore requires a real launchd job.

    python3 make-test-launchd-job.py <src.plist> <label> [--arg X]... [--env K=V]... [--out /tmp/x.log]

    launchctl bootstrap gui/$(id -u) /tmp/<label>.plist
    ... play the audio / do the thing under test ...
    launchctl bootout  gui/$(id -u)/<label>
    rm /tmp/<label>.plist

Typical run - clone the wake-detector plist, add --verbose, neutralise the wake so it can
never raise the real window:

    --arg --verbose --env APEX_BRIDGE_WAKE=http://127.0.0.1:9/wake

then play the same audio twice, once as-is and once with `--env APEX_CLAP_IGNORE_MEDIA=0`, and
diff the logs: that A/B is the proof that the switch (not something else) changed behaviour.

Gotcha: plistlib.dump(value, fp) - reversed arguments raise
"'dict' object has no attribute 'write'".
"""
import os
import plistlib
import sys


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, label = argv[1], argv[2]
    args, env, out = [], {}, "/tmp/%s.log" % label
    rest, i = argv[3:], 0
    while i < len(rest):
        if rest[i] == "--arg":
            args.append(rest[i + 1]); i += 2
        elif rest[i] == "--env":
            k, _, v = rest[i + 1].partition("="); env[k] = v; i += 2
        elif rest[i] == "--out":
            out = rest[i + 1]; i += 2
        else:
            print("unknown option: %s" % rest[i]); return 2

    with open(src, "rb") as fh:
        d = plistlib.load(fh)
    d["Label"] = label
    d["ProgramArguments"] = list(d["ProgramArguments"]) + args
    d.setdefault("EnvironmentVariables", {}).update(env)
    d["StandardOutPath"] = out
    d["StandardErrorPath"] = os.path.splitext(out)[0] + ".err"
    d["KeepAlive"] = False          # a crashed test must not come back

    dst = "/tmp/%s.plist" % label
    with open(dst, "wb") as fh:
        plistlib.dump(d, fh)
    print("%s\n  args=%s\n  env=%s\n  log=%s" % (dst, d["ProgramArguments"], env, out))
    print("  launchctl bootstrap gui/$(id -u) %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
