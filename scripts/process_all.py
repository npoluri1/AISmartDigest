"""Process ALL videos - YouTube + Facebook with proper clean data."""
import asyncio
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_API_BASE"] = "http://localhost:11434"
os.environ["LLM_TIMEOUT"] = "10"

from src.agents.orchestrator import Orchestrator

all_urls = [
    # === AI YouTube Videos ===
    "https://www.youtube.com/watch?v=YESrXVkcCHY",   # Best AI Coding Tools 2025 (Tech With Tim)
    "https://www.youtube.com/watch?v=ocMOZpuAMw4",   # Cursor Tutorial for Beginners
    "https://www.youtube.com/watch?v=eMZmDH3T2bY",   # Claude Code Tutorial
    "https://www.youtube.com/watch?v=zt0JA5rxdfM",   # AI Trends 2026 (IBM)
    "https://www.youtube.com/watch?v=-VTiqivKOB8",   # AI Coding Tools 2026
    "https://www.youtube.com/watch?v=rM0xpwENa8I",   # Best AI Coding Tools (Codevolution)
    "https://www.youtube.com/watch?v=J02-39xtlt4",   # Google AI Updates
    "https://www.youtube.com/watch?v=BedAaB1RKgE",   # MCP vs ADK (IBM)
    "https://www.youtube.com/watch?v=nAmC7SoVLd8",   # LangChain Crash Course
    "https://www.youtube.com/watch?v=Xn-gtHDsaPY",   # Fireship - 7 AI tools
    "https://www.youtube.com/watch?v=fl1DSmwQKKY",   # What is Claude Code?
    "https://www.youtube.com/watch?v=RKbmqSRc0z0",   # Best AI Coding Tools 2026

    # === Facebook AI Reels ===
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

async def main():
    orch = Orchestrator()
    results = []
    for i, url in enumerate(all_urls):
        print(f"\n[{i+1}/{len(all_urls)}] {url[:70]}")
        try:
            entry = await orch.process_url(url)
            tools = ", ".join(entry.ai_tools[:4]) if entry.ai_tools else "(none)"
            print(f"  [{entry.platform}] Score={entry.relevance_score} | {entry.title[:60]}")
            print(f"  Tools: {tools}")
            results.append(entry)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"Total: {len(results)} videos processed")

    all_tools = {}
    for e in results:
        for t in e.ai_tools:
            all_tools[t] = all_tools.get(t, 0) + 1
    if all_tools:
        print(f"\nAI Tools found ({len(all_tools)} unique):")
        for tool, count in sorted(all_tools.items(), key=lambda x: -x[1])[:20]:
            print(f"  {tool}: {count}x")

asyncio.run(main())
