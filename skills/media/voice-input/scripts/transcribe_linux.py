#!/usr/bin/env python3
"""Transcribe audio file using faster-whisper on Linux.

Usage:
    python3 transcribe_linux.py <audio_file> [--model tiny|base|small|medium|large-v3] [--language zh|en|...]

Output: prints transcription to stdout. Metadata goes to stderr.
"""
import sys
import argparse
from faster_whisper import WhisperModel

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with faster-whisper (Linux)")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--model", default="tiny", help="Model size: tiny/base/small/medium/large-v3")
    parser.add_argument("--language", default=None, help="Force language (zh/en/ja etc.)")
    args = parser.parse_args()

    print(f"[STT] Loading model {args.model}...", file=sys.stderr)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    print(f"[STT] Transcribing {args.audio_file}...", file=sys.stderr)
    segments, info = model.transcribe(args.audio_file, language=args.language)

    detected_lang = info.language
    probability = info.language_probability
    print(f"[STT] Language: {detected_lang} (p={probability:.2f})", file=sys.stderr)

    full_text = ""
    for segment in segments:
        full_text += segment.text + " "

    print(full_text.strip())

if __name__ == "__main__":
    main()
