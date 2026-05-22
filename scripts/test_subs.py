"""Test yt-dlp subtitle extraction."""
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')

import yt_dlp
import json

ydl_opts = {
    "quiet": True,
    "no_warnings": True,
    "writesubtitles": True,
    "writeautomaticsub": True,
    "subtitleslangs": ["en"],
    "skip_download": True,
    "subtitlesformat": "vtt",
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info("https://www.youtube.com/watch?v=nAmC7SoVLd8", download=False)
    subs = info.get("subtitles", {})
    auto_subs = info.get("automatic_captions", {})
    print("Subtitles:", list(subs.keys()))
    print("Auto captions:", list(auto_subs.keys()))
    if "en" in auto_subs:
        for entry in auto_subs["en"][:3]:
            print(f"  Format: {entry.get('ext')} - URL: {entry.get('url','')[:80]}")
    if "en" in subs:
        for entry in subs["en"][:3]:
            print(f"  Sub: {entry.get('ext')} - URL: {entry.get('url','')[:80]}")
