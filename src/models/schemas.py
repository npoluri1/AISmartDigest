"""Pydantic data models for video content, summaries, and agent state."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PlatformInfo(BaseModel):
    name: str
    url: str
    video_id: str


class VideoMetadata(BaseModel):
    title: str
    description: str = ""
    duration_s: int = 0
    view_count: int = 0
    like_count: int = 0
    author: str = ""
    channel_url: str = ""
    thumbnail_url: str = ""
    published_at: Optional[str] = None
    tags: list[str] = []


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float


class RawContent(BaseModel):
    platform: PlatformInfo
    metadata: VideoMetadata
    transcript: list[TranscriptSegment] = []
    comments: list[str] = []
    raw_text: str = ""


class ExtractedInfo(BaseModel):
    ai_tools: list[str] = Field(default_factory=list, description="AI tools mentioned")
    ai_models: list[str] = Field(default_factory=list, description="AI models discussed")
    key_frameworks: list[str] = Field(default_factory=list, description="Frameworks/libraries")
    key_insights: list[str] = Field(default_factory=list, description="Key takeaways")
    latest_news: list[str] = Field(default_factory=list, description="News/updates mentioned")
    categories: list[str] = Field(default_factory=list, description="Content categories")
    summary: str = ""
    relevance_score: int = Field(default=5, ge=1, le=10)


class DigestEntry(BaseModel):
    id: Optional[str] = None
    url: str
    platform: str
    title: str
    summary: str = ""
    ai_tools: list[str] = []
    ai_models: list[str] = []
    key_insights: list[str] = []
    latest_news: list[str] = []
    categories: list[str] = []
    relevance_score: int = 5
    raw_text: str = ""
    processed_at: str = ""
    thumbnail_url: str = ""
    error: Optional[str] = None


class DigestReport(BaseModel):
    total_processed: int
    total_errors: int
    entries: list[DigestEntry]
    top_tools: list[tuple[str, int]] = []
    top_models: list[tuple[str, int]] = []
    top_categories: list[tuple[str, int]] = []
    generated_at: str = ""
