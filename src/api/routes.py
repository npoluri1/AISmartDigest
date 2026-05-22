import json
import logging
import traceback
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.config import settings
from src.storage.database import Database
from src.models.schemas import DigestEntry, ExtractedInfo
from src.agents.orchestrator import Orchestrator
from src.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


class ProcessRequest(BaseModel):
    urls: List[str]


class DiscoverRequest(BaseModel):
    keywords: List[str]
    limit: int = 3


class SearchRequest(BaseModel):
    query: str
    limit: int = 20


def get_db() -> Database:
    return Database()


def get_orch() -> Orchestrator:
    llm = LLMClient()
    return Orchestrator(llm)


@router.get("/digests")
async def list_digests(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    platform: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "date",
):
    db = get_db()
    if search:
        entries = db.search_entries(search, limit=limit)
    else:
        entries = db.get_all_entries(limit=limit, offset=offset)

    if platform and platform.lower() != "all":
        entries = [e for e in entries if e.platform.lower() == platform.lower()]

    if sort == "score":
        entries.sort(key=lambda e: e.relevance_score or 0, reverse=True)

    total = len(entries)
    return {
        "entries": [e.dict() for e in entries],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/digests/{digest_id}")
async def get_digest(digest_id: int):
    db = get_db()
    entries = db.get_all_entries(limit=1000)
    for e in entries:
        if e.id is not None and str(e.id) == str(digest_id):
            return e.dict()
    raise HTTPException(status_code=404, detail="Digest not found")


@router.delete("/digests/{digest_id}")
async def delete_digest(digest_id: int):
    db = get_db()
    conn = db.connection
    conn.execute("DELETE FROM digests WHERE id = ?", (digest_id,))
    conn.commit()
    if conn.total_changes == 0:
        raise HTTPException(status_code=404, detail="Digest not found")
    return {"ok": True}


@router.post("/process")
async def process_videos(req: ProcessRequest):
    orch = get_orch()
    db = get_db()
    results = []

    for url in req.urls:
        url = url.strip()
        if not url:
            continue
        try:
            if db.entry_exists(url):
                entries = db.get_all_entries(limit=1000)
                existing = [e for e in entries if e.url == url]
                if existing:
                    results.append({"url": url, "status": "already_exists", "digest": existing[0].dict()})
                    continue

            entry = await orch.process_url(url)
            results.append({"url": url, "status": "success", "digest": entry.dict()})
        except Exception as e:
            logger.error(f"Error processing {url}: {e}\n{traceback.format_exc()}")
            error_entry = DigestEntry(
                url=url,
                platform="unknown",
                error=str(e),
                processed_at=datetime.utcnow().isoformat(),
            )
            db.save_entry(error_entry)
            results.append({"url": url, "status": "error", "error": str(e)})

    return {"results": results, "total": len(results)}


@router.post("/discover")
async def discover_content(req: DiscoverRequest):
    orch = get_orch()
    llm = LLMClient()
    from src.agents.discovery_agent import DiscoveryAgent
    from src.agents.browser_agent import BrowserAgent

    browser = BrowserAgent()
    discovery = DiscoveryAgent(llm, browser)
    all_discovered = []

    try:
        for keyword in req.keywords:
            urls = await discovery.discover(keyword, limit=req.limit)
            all_discovered.extend(urls)
    finally:
        try:
            await browser.close()
        except Exception:
            pass

    results = []
    db = get_db()
    for url in all_discovered:
        try:
            if db.entry_exists(url):
                entries = db.get_all_entries(limit=1000)
                existing = [e for e in entries if e.url == url]
                if existing:
                    results.append({"url": url, "status": "already_exists", "digest": existing[0].dict()})
                    continue

            entry = await orch.process_url(url)
            results.append({"url": url, "status": "success", "digest": entry.dict()})
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            results.append({"url": url, "status": "error", "error": str(e)})

    return {"results": results, "total": len(results), "discovered": len(all_discovered)}


@router.get("/stats")
async def get_stats():
    db = get_db()
    stats = db.get_stats()
    return stats


@router.get("/trending")
async def get_trending():
    db = get_db()
    report = db.get_stats()
    entries = db.get_all_entries(limit=100, offset=0)
    entries.sort(key=lambda e: e.relevance_score or 0, reverse=True)

    return {
        "top_tools": report.top_tools,
        "top_models": report.top_models,
        "top_categories": report.top_categories,
        "top_entries": [e.dict() for e in entries[:10]],
        "total_processed": report.total_processed,
        "error_count": report.total_errors,
    }


@router.get("/search")
async def search_digests(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    db = get_db()
    entries = db.search_entries(q, limit=limit)
    return {
        "entries": [e.dict() for e in entries],
        "total": len(entries),
        "query": q,
    }


@router.get("/tech-digests")
async def get_tech_digests(
    limit: int = Query(50, ge=1, le=200),
    min_score: int = Query(6, ge=1, le=10),
):
    db = get_db()
    entries = db.get_all_entries(limit=limit)
    tech_entries = [e for e in entries if e.relevance_score and e.relevance_score >= min_score]
    tools = set()
    for e in tech_entries:
        for t in e.ai_tools:
            tools.add(t)
    return {
        "entries": [e.dict() for e in tech_entries],
        "total": len(tech_entries),
        "unique_tools": sorted(tools),
        "filter": {"min_score": min_score},
    }


@router.post("/discover/run")
async def trigger_discovery(keywords: List[str] = Query(["AI development", "AI tools", "AI coding", "machine learning"]), limit: int = Query(3, ge=1, le=10)):
    orch = get_orch()
    try:
        entries = await orch.discover_and_process(keywords, limit_per_platform=limit)
        tools = set()
        for e in entries:
            for t in e.ai_tools:
                tools.add(t)
        return {
            "status": "success",
            "entries_processed": len(entries),
            "tools_found": sorted(tools),
            "keywords": keywords,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover/status")
async def get_discover_status():
    from src.api.app import _scheduler_active
    db = get_db()
    report = db.get_stats()
    return {
        "scheduler_active": _scheduler_active,
        "total_processed": report.total_processed,
        "unique_tools": len(report.top_tools),
        "last_entries": [e.dict() for e in report.entries[:5]],
    }
