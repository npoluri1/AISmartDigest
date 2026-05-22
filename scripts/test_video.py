"""Test YouTube video processing."""
import asyncio
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')

import yt_dlp

# Test with popular AI videos - Fireship, Two Minute Papers, etc.
test_urls = [
    ("Fireship - AI", "https://www.youtube.com/watch?v=rHq4ZXvyl5k"),
    ("Fireship - LangChain", "https://www.youtube.com/watch?v=C7pNliE22Nk"),
    ("AI Explained", "https://www.youtube.com/watch?v=2vVwUEOJbhg"),
    ("Matt Wolfe - AI News", "https://www.youtube.com/watch?v=EMpX9v-hrIk"),
]

for name, url in test_urls:
    print(f"\n=== Testing: {name} ===")
    print(f"URL: {url}")
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "N/A")
            duration = info.get("duration", 0)
            uploader = info.get("uploader", "N/A")
            views = info.get("view_count", 0)
            print(f"  Title: {title[:80]}")
            print(f"  Duration: {duration}s")
            print(f"  Channel: {uploader}")
            print(f"  Views: {views}")
        except Exception as e:
            print(f"  ERROR: {e}")
