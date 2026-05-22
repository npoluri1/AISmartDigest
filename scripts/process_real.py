"""Process real AI YouTube videos through the pipeline."""
import asyncio
import sys
sys.path.insert(0, 'D:\\WorkSpace\\Claude_Code\\AISmartDigest\\AISmartDigest')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_API_BASE"] = "http://localhost:11434"
os.environ["LLM_TIMEOUT"] = "10"

from src.agents.orchestrator import Orchestrator

# Real AI YouTube videos with high value content
urls = [
    "https://www.youtube.com/watch?v=YESrXVkcCHY",   # Tech With Tim - Best AI Coding Tools (177K views)
    "https://www.youtube.com/watch?v=ocMOZpuAMw4",   # Tech With Tim - Cursor Tutorial (992K views)
    "https://www.youtube.com/watch?v=eMZmDH3T2bY",   # Kevin Stratvert - Claude Code Tutorial (835K views)
    "https://www.youtube.com/watch?v=zt0JA5rxdfM",   # IBM Technology - AI Trends 2026 (392K views)
    "https://www.youtube.com/watch?v=-VTiqivKOB8",   # Tech With Tim - AI Coding Tools 2026 (79K views)
    "https://www.youtube.com/watch?v=rM0xpwENa8I",   # Codevolution - Best AI Coding Tools (154K views)
    "https://www.youtube.com/watch?v=J02-39xtlt4",   # Google AI Updates (56K views)
    "https://www.youtube.com/watch?v=BedAaB1RKgE",   # IBM Technology - MCP vs ADK (32K views)
    "https://www.youtube.com/watch?v=nAmC7SoVLd8",   # codebasics - LangChain Crash Course (642K views)
    "https://www.youtube.com/watch?v=Xn-gtHDsaPY",   # Fireship - 7 new open source AI tools (834K views)
    "https://www.youtube.com/watch?v=fl1DSmwQKKY",   # What is Claude Code? (839K views)
    "https://www.youtube.com/watch?v=RKbmqSRc0z0",   # Mikey - Best AI Coding Tools 2026 (85K views)
]

async def main():
    orch = Orchestrator()
    results = []
    for i, url in enumerate(urls):
        print(f"\n[{i+1}/{len(urls)}] Processing: {url}")
        try:
            entry = await orch.process_url(url)
            tools = ", ".join(entry.ai_tools[:5]) if entry.ai_tools else "(none)"
            models = ", ".join(entry.ai_models[:3]) if entry.ai_models else "(none)"
            print(f"  Title:   {entry.title[:70]}")
            print(f"  Score:   {entry.relevance_score}/10")
            print(f"  Tools:   {tools}")
            results.append(entry)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"Processed {len(results)} videos successfully!")

    all_tools = {}
    for e in results:
        for t in e.ai_tools:
            all_tools[t] = all_tools.get(t, 0) + 1
    if all_tools:
        print(f"\nAI tools found ({len(all_tools)} unique):")
        for tool, count in sorted(all_tools.items(), key=lambda x: -x[1])[:20]:
            print(f"  {tool}: {count}x")

asyncio.run(main())
