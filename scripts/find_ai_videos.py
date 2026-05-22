"""Search YouTube for real AI development videos."""
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')

import yt_dlp
import json

ydl_opts = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
    "force_generic_extractor": False,
}

keywords = [
    "AI tools for developers 2025",
    "best AI coding tools",
    "Cursor AI tutorial",
    "Claude AI coding",
    "AI development news",
    "LangChain tutorial",
]

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for kw in keywords:
        print(f"\n=== Search: {kw} ===")
        try:
            results = ydl.extract_info(f"ytsearch10:{kw}", download=False)
            entries = results.get("entries", [])
            for i, entry in enumerate(entries[:5]):
                vid_id = entry.get("id", "?")
                title = entry.get("title", "?")
                uploader = entry.get("uploader", "?")
                views = entry.get("view_count", 0)
                url = f"https://www.youtube.com/watch?v={vid_id}"
                print(f"  {i+1}. {title[:70]}")
                print(f"     URL: {url}")
                print(f"     Channel: {uploader} | Views: {views}")
        except Exception as e:
            print(f"  Error: {e}")
