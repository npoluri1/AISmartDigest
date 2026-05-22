"""Process Facebook URLs with improved extraction."""
import asyncio
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_API_BASE"] = "http://localhost:11434"
os.environ["LLM_TIMEOUT"] = "10"

from src.agents.orchestrator import Orchestrator
from src.agents.transcript_agent import TranscriptAgent

fb_urls = [
    "https://www.facebook.com/share/r/18ULZYHGMn/",
    "https://www.facebook.com/share/v/14j9LJNZCQS/",
    "https://www.facebook.com/share/r/1AtahANup4/",
    "https://www.facebook.com/share/r/1E7qBHeCJ7/",
    "https://www.facebook.com/share/r/1FW2hmDqbe/",
    "https://www.facebook.com/share/r/1Liv7ebirB/",
    "https://www.facebook.com/share/r/1E2sBwBBiP/",
    "https://www.facebook.com/share/r/1EXhNjgAMZ/",
    "https://www.facebook.com/share/r/18Ry8JBJgH/",
    "https://www.facebook.com/share/r/1H4fkDBYrT/",
    "https://www.facebook.com/share/r/1DTmfNNQzA/",
    "https://www.facebook.com/share/r/1E6hopiieB/",
    "https://www.facebook.com/share/r/184za7SRra/",
    "https://www.facebook.com/share/r/18WkE88twW/",
    "https://www.facebook.com/share/r/1F26rqkCKc/",
    "https://www.facebook.com/share/r/1CuPDHTHe8/",
    "https://www.facebook.com/share/r/18seG66Sbh/",
]

async def test_extraction():
    agent = TranscriptAgent()
    for url in fb_urls[:3]:
        print(f"\n--- Testing: {url} ---")
        try:
            result = await agent.extract(url)
            status = result.get("status", "?")
            platform = result.get("platform", {})
            meta = result.get("metadata", {})
            text = result.get("transcript_text", "")
            print(f"  Status: {status}")
            print(f"  Platform: {platform.get('name', '?') if isinstance(platform, dict) else '?'}")
            print(f"  Title: {meta.get('title', 'N/A')}")
            print(f"  Desc: {meta.get('description', 'N/A')[:80]}")
            print(f"  Text length: {len(text)}")
        except Exception as e:
            print(f"  ERROR: {e}")

async def process_all():
    orch = Orchestrator()
    results = []
    for i, url in enumerate(fb_urls):
        print(f"\n[{i+1}/{len(fb_urls)}] {url}")
        try:
            entry = await orch.process_url(url)
            print(f"  Title: {entry.title[:60]}")
            print(f"  Platform: {entry.platform}")
            print(f"  Score: {entry.relevance_score}")
            tools = ", ".join(entry.ai_tools[:4]) if entry.ai_tools else "(none)"
            print(f"  Tools: {tools}")
            results.append(entry)
        except Exception as e:
            print(f"  ERROR: {e}")
    print(f"\nProcessed {len(results)}/{len(fb_urls)}")

async def main():
    print("=== Step 1: Test extraction ===")
    await test_extraction()
    print("\n=== Step 2: Process all ===")
    await process_all()

asyncio.run(main())
