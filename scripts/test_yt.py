"""Test yt-dlp with different options."""
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')

import yt_dlp
import json

# Use options that help bypass YouTube restrictions
ydl_opts = {
    "quiet": False,
    "no_warnings": False,
    "extract_flat": False,
    "force_generic_extractor": False,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
    },
}

# Test with a VERY popular video that should always work
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - most reliable
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # First YouTube video ever
]

for url in test_urls:
    print(f"\n=== Testing: {url} ===")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "N/A")
            uploader = info.get("uploader", "N/A")
            duration = info.get("duration", 0)
            print(f"  SUCCESS! Title: {title}")
            print(f"  Uploader: {uploader}")
            print(f"  Duration: {duration}s")
    except Exception as e:
        print(f"  ERROR: {e}")
        print(f"  Type: {type(e).__name__}")
