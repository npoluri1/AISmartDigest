import asyncio
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.api.routes import router

logger = logging.getLogger(__name__)

_background_task = None
_scheduler_active = False


async def daily_discovery_loop():
    global _scheduler_active
    _scheduler_active = True
    logger.info("Daily discovery scheduler started (interval: 6 hours)")

    keywords = ["AI development", "AI tools", "machine learning", "deep learning",
                "large language model", "AI coding", "AI agent", "artificial intelligence"]

    while _scheduler_active:
        try:
            from src.agents.orchestrator import Orchestrator
            orch = Orchestrator()
            logger.info("Running scheduled discovery...")
            entries = await orch.discover_and_process(keywords, limit_per_platform=3)
            tools_found = set()
            for e in entries:
                for t in e.ai_tools:
                    tools_found.add(t)
            logger.info(f"Scheduled discovery complete: {len(entries)} new entries, {len(tools_found)} tools found")
        except Exception as e:
            logger.error(f"Scheduled discovery error: {e}")

        for _ in range(6 * 60):  # Check every minute if still active, up to 6 hours
            if not _scheduler_active:
                break
            await asyncio.sleep(60)

    logger.info("Daily discovery scheduler stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _background_task
    os.makedirs(settings.browser_cookie_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    data_dir = Path(settings.output_dir).parent
    os.makedirs(str(data_dir), exist_ok=True)
    logger.info(f"Application started - {settings.app_name} v{settings.app_version}")
    _background_task = asyncio.create_task(daily_discovery_loop())
    yield
    global _scheduler_active
    _scheduler_active = False
    if _background_task:
        _background_task.cancel()
        try:
            await _background_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Smart Digest - AI-powered video intelligence platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"Serving static files from {static_dir}")
else:
    logger.warning(f"Static directory not found at {static_dir}")
