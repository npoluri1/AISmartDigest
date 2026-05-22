"""Orchestrator — coordinates the full pipeline: URL → extract → summarize → store."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.agents.transcript_agent import TranscriptAgent
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.youtube_agent import YouTubeAgent
from src.agents.discovery_agent import DiscoveryAgent
from src.storage.database import Database
from src.models.schemas import DigestEntry, DigestReport
from src.config import settings

logger = logging.getLogger(__name__)


class Orchestrator(BaseAgent):
    def __init__(self, db: Optional[Database] = None):
        super().__init__("Orchestrator")
        self.db = db or Database(settings.database_url)
        self.transcript_agent = TranscriptAgent()
        self.summarizer_agent = SummarizerAgent()
        self.youtube_agent = YouTubeAgent()
        self.discovery_agent = DiscoveryAgent()

    async def discover_and_process(self, keywords: list[str], limit_per_platform: int = 5) -> list[DigestEntry]:
        self.log(f"Starting discovery for: {keywords}")
        discovery_results = await self.discovery_agent.discover(keywords, limit=limit_per_platform)
        
        all_urls = []
        for platform, urls in discovery_results.items():
            all_urls.extend(urls)
        
        unique_urls = list(set(all_urls))
        self.log(f"Discovered {len(unique_urls)} unique URLs. Starting digestion...")
        
        return await self.process_urls(unique_urls)

    async def start_monitoring(self, keywords: list[str], interval: int = 3600):
        """Continuous background monitoring for new content."""
        self.log(f"Agentic Monitoring Started. Interval: {interval}s | Keywords: {keywords}")
        while True:
            try:
                await self.discover_and_process(keywords, limit_per_platform=5)
                self.log(f"Monitoring cycle complete. Sleeping for {interval}s...")
            except Exception as e:
                self.log(f"Monitoring error: {e}", "error")
            
            await asyncio.sleep(interval)

    async def process_url(self, url: str) -> DigestEntry:
        self.log(f"Processing: {url}")

        if self.db.entry_exists(url):
            self.log(f"Already processed, skipping: {url}")
            entries = self.db.search_entries(url, limit=1)
            return entries[0] if entries else DigestEntry(url=url, platform="", title="", processed_at="")

        if self.youtube_agent.is_youtube_url(url):
            video_id = self.youtube_agent.extract_video_id(url)
            video_data = await self.youtube_agent.execute(url=url)
            if video_data.get("status") == "error":
                return DigestEntry(url=url, platform="youtube", title="", processed_at="", error=video_data.get("error"))
            platform = "youtube"
            metadata = video_data.get("metadata", {})
            transcript_text = video_data.get("transcript_text", "")
            title = metadata.get("title", "")
        else:
            result = await self.transcript_agent.extract(url)
            if result.get("status") == "error":
                return DigestEntry(url=url, platform="unknown", title="", processed_at="", error=result.get("error"))
            platform = result.get("platform", {}).get("name", "web")
            metadata = result.get("metadata", {})
            transcript_text = result.get("transcript_text", "")
            title = metadata.get("title", url)

        entry = await self.summarizer_agent.summarize(url, platform, title, transcript_text, metadata)
        if metadata.get("thumbnail_url"):
            entry.thumbnail_url = metadata["thumbnail_url"]
        self.db.save_entry(entry)
        self.log(f"Stored: {title[:60]}... | Score: {entry.relevance_score}/10")
        return entry

    async def process_urls(self, urls: list[str]) -> list[DigestEntry]:
        sem = asyncio.Semaphore(settings.max_concurrent)

        async def process_one(url: str) -> DigestEntry:
            async with sem:
                return await self.process_url(url)

        tasks = [process_one(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        entries = []
        for r in results:
            if isinstance(r, DigestEntry):
                entries.append(r)
            else:
                self.log(f"Task failed: {r}", "error")
        return entries

    def search(self, query: str) -> list[DigestEntry]:
        return self.db.search_entries(query)

    def get_stats(self) -> DigestReport:
        return self.db.get_stats()

    async def execute(self, **kwargs) -> dict:
        urls = kwargs.get("urls", [])
        action = kwargs.get("action", "process")

        if action == "process":
            entries = await self.process_urls(urls)
            report = self.get_stats()
            return {"entries": [e.dict() for e in entries], "report": report.dict()}
        elif action == "search":
            results = self.search(kwargs.get("query", ""))
            return {"entries": [e.dict() for e in results]}
        elif action == "stats":
            return {"report": self.get_stats().dict()}
        return {"status": "unknown_action"}
