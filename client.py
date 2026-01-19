#!/usr/bin/env python3
"""
Simple client for testing the NovaSR upsampler API.

Usage:
    python client.py <audio_file>           # Save to upsampled.wav
    python client.py <audio_file> -o out.wav # Save to out.wav
    cat audio.mp3 | python client.py -        # Read from stdin
"""

import sys
import argparse
import requests
from pathlib import Path

API_URL = "http://localhost:10999/upsample"


def upsample(audio_path: str, output_path: str = "upsampled.wav", url: str = API_URL):
    """
    Upload audio file to API and save upsampled result.

    Args:
        audio_path: Path to input audio file, or "-" for stdin
        output_path: Path to save output WAV file
        url: API URL
    """
    if audio_path == "-":
        # Read from stdin
        print("Reading audio from stdin...", file=sys.stderr)
        files = {"file": ("audio.wav", sys.stdin.buffer, "audio/wav")}
    else:
        # Read from file
        path = Path(audio_path)
        if not path.exists():
            print(f"Error: File not found: {audio_path}", file=sys.stderr)
            return 1

        content_type = _get_content_type(path.suffix)
        print(f"Uploading {path.name} ({_get_file_size(path)} bytes)...", file=sys.stderr)
        files = {"file": (path.name, path.read_bytes(), content_type)}

    # Send request
    print(f"Sending to {url}...", file=sys.stderr)
    response = requests.post(url, files=files)

    if response.status_code != 200:
        print(f"Error: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        return 1

    # Save output
    output = Path(output_path)
    output.write_bytes(response.content)
    print(f"Saved to {output_path} ({_get_file_size(output)} bytes)", file=sys.stderr)
    print(f"  Content-Type: {response.headers.get('Content-Type')}", file=sys.stderr)

    return 0


def _get_content_type(ext: str) -> str:
    """Get MIME type for file extension."""
    types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".aac": "audio/aac",
    }
    return types.get(ext.lower(), "audio/wav")


def _get_file_size(path: Path) -> str:
    """Get human readable file size."""
    size = path.stat().st_size
    for unit in ["B", "KB", "MB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def main():
    parser = argparse.ArgumentParser(
        description="Test client for NovaSR upsampler API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("audio", help="Audio file path, or '-' for stdin")
    parser.add_argument("-o", "--output", default="upsampled.wav", help="Output file path")
    parser.add_argument("--url", default=API_URL, help=f"API URL (default: {API_URL})")

    args = parser.parse_args()

    url = args.url
    output = args.output

    return upsample(args.audio, output, url)


if __name__ == "__main__":
    sys.exit(main())
