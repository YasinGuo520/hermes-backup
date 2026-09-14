#!/usr/bin/env python3
"""Is any app playing audio to the DEFAULT output device right now?

Measured on macOS 2026-09-13: quiet -> 0, `say` / `afplay` playing -> 1, stopped -> 0.
This is the signal behind the "she woke herself up and answered the video" class of bug:
media transients inside a clap band are indistinguishable from a double clap, so the wake
detector needs a CONTEXTUAL guard (is the machine making noise right now?) rather than a
different threshold.

    python3 coreaudio-media-probe.py                      # one shot
exit 1 = audio playing, 0 = silent, 2 = probe failed (so it composes with shell tests)

    while :; do python3 coreaudio-media-probe.py; sleep 1; done   # watch while you play a video

`pmset -g assertions` is NOT a substitute: the coreaudiod assertion that always persists on
this machine is the MICROPHONE-INPUT one, so it reads 1 even in a silent room.
"""
import ctypes
import struct
import sys

ca = ctypes.CDLL("/System/Library/Frameworks/CoreAudio.framework/CoreAudio")
# argtypes are mandatory: without them the 64-bit pointers get truncated and every call fails.
ca.AudioObjectGetPropertyData.argtypes = [
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p,
]
ca.AudioObjectGetPropertyData.restype = ctypes.c_int32


class Addr(ctypes.Structure):
    _fields_ = [("sel", ctypes.c_uint32), ("scope", ctypes.c_uint32), ("elem", ctypes.c_uint32)]


def fourcc(code: str) -> int:
    return struct.unpack(">I", code.encode())[0]


def prop(obj_id: int, selector: str):
    a = Addr(fourcc(selector), fourcc("glob"), 0)
    out = ctypes.c_uint32(0)
    n = ctypes.c_uint32(4)
    err = ca.AudioObjectGetPropertyData(ctypes.c_uint32(obj_id), ctypes.byref(a), 0, None,
                                        ctypes.byref(n), ctypes.byref(out))
    return out.value if err == 0 else None


def media_playing():
    """True / False / None(=probe failed)."""
    dev = prop(1, "dOut")       # kAudioObjectSystemObject = 1 -> default output device
    if not dev:
        return None
    run = prop(dev, "gone")     # kAudioDevicePropertyDeviceIsRunningSomewhere
    return None if run is None else run == 1


if __name__ == "__main__":
    v = media_playing()
    print("media_playing=%s" % ("probe-failed" if v is None else v))
    sys.exit(2 if v is None else (1 if v else 0))
