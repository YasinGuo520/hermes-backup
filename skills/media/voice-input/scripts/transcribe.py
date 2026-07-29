#!/usr/bin/env python3
"""Transcribe audio file using faster-whisper.
Usage: transcribe.py <audio_file> [--model tiny|base|small|medium|large-v3]
Default model: tiny (fast, good enough for Chinese+English)
"""

import sys
import os
import argparse
from faster_whisper import WhisperModel

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio with faster-whisper')
    parser.add_argument('audio_file', help='Path to audio file (wav/mp3/m4a/ogg/aac...)')
    parser.add_argument('--model', default='tiny', choices=['tiny', 'base', 'small', 'medium', 'large-v3'],
                        help='Whisper model size (default: tiny)')
    parser.add_argument('--language', default=None,
                        help='Language code (e.g. zh, en). Auto-detect if omitted')
    parser.add_argument('--task', default='transcribe', choices=['transcribe', 'translate'],
                        help='transcribe=original language, translate=to English (default: transcribe)')
    args = parser.parse_args()

    if not os.path.exists(args.audio_file):
        print(f"ERROR: File not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading model '{args.model}'...", file=sys.stderr)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    print(f"Transcribing {args.audio_file}...", file=sys.stderr)
    segments, info = model.transcribe(
        args.audio_file,
        language=args.language,
        task=args.task,
        beam_size=5,
        vad_filter=True,
    )

    print(f"\nDetected language: {info.language} (p={info.language_probability:.2f})", file=sys.stderr)
    print(f"Duration: {info.duration:.1f}s\n", file=sys.stderr)

    full_text = []
    for segment in segments:
        print(f"[{segment.start:.1f}s -> {segment.end:.1f}s] {segment.text}", file=sys.stderr)
        full_text.append(segment.text)

    print("\n=== TRANSCRIPTION ===")
    print(" ".join(full_text).strip())

if __name__ == '__main__':
    main()
