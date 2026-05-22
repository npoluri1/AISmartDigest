"""YouTube agent — extracts metadata and transcripts from YouTube videos."""

import json
import logging
import re
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.models.schemas import VideoMetadata, TranscriptSegment, PlatformInfo

logger = logging.getLogger(__name__)

YOUTUBE_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)"
    r"([\w-]{11})"
)


class YouTubeAgent(BaseAgent):
    def __init__(self):
        super().__init__("YouTubeAgent")

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        match = YOUTUBE_REGEX.search(url)
        return match.group(1) if match else None

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        return bool(YOUTUBE_REGEX.search(url))

    async def get_metadata(self, video_id: str) -> Optional[VideoMetadata]:
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                return VideoMetadata(
                    title=info.get("title") or "",
                    description=(info.get("description") or "")[:2000],
                    duration_s=info.get("duration") or 0,
                    view_count=info.get("view_count") or 0,
                    like_count=info.get("like_count") or 0,
                    author=info.get("uploader") or "",
                    channel_url=info.get("uploader_url") or "",
                    thumbnail_url=info.get("thumbnail") or "",
                    published_at=str(info.get("upload_date") or ""),
                    tags=info.get("tags") or [],
                )
        except Exception as e:
            self.log(f"yt-dlp error: {e}", "error")
            return None

    async def get_transcript(self, video_id: str) -> list[TranscriptSegment]:
        segments = await self._get_transcript_ytdlp(video_id)
        if segments:
            return segments
        segments = await self._get_transcript_api(video_id)
        if segments:
            return segments
        return []

    async def _get_transcript_ytdlp(self, video_id: str) -> list[TranscriptSegment]:
        try:
            import yt_dlp
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "writesubtitles": False,
                "writeautomaticsub": False,
                "skip_download": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                auto_captions = info.get("automatic_captions") or {}
                captions = info.get("subtitles") or {}

                for lang in ["en", "en-US", "en-GB", "a.", "en-orig"]:
                    sources = auto_captions.get(lang) or captions.get(lang) or []
                    for entry in sources:
                        if entry.get("ext") == "json3":
                            import httpx
                            url = entry["url"]
                            resp = httpx.get(url, timeout=15, headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            })
                            if resp.status_code == 200:
                                data = resp.json()
                                events = data.get("events", [])
                                segs = []
                                for ev in events:
                                    segs_data = ev.get("segs", [])
                                    for seg in segs_data:
                                        text = seg.get("utf8", "").strip()
                                        if text:
                                            start = ev.get("tStartMs", 0) / 1000.0
                                            dur = ev.get("dDurationMs", 0) / 1000.0
                                            segs.append(TranscriptSegment(text=text, start=start, duration=dur))
                                if segs:
                                    self.log(f"Got {len(segs)} segments via yt-dlp json3")
                                    return segs
                            break
        except Exception as e:
            self.log(f"yt-dlp transcript error: {e}", "warning")
        return []

    async def _get_transcript_api(self, video_id: str) -> list[TranscriptSegment]:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()
            raw = api.fetch(video_id)
            return [TranscriptSegment(text=s.text, start=s.start, duration=s.duration) for s in raw]
        except Exception as e:
            self.log(f"Transcript API error: {e}", "warning")
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                api = YouTubeTranscriptApi()
                raw = api.fetch(video_id, languages=["en", "a.", "en-US", "en-GB"])
                segs = []
                for s in raw:
                    text = getattr(s, "text", str(s)).replace("\n", " ")
                    start = getattr(s, "start", 0)
                    duration = getattr(s, "duration", 0)
                    segs.append(TranscriptSegment(text=text, start=start, duration=duration))
                return segs
            except Exception as e2:
                self.log(f"Transcript API fallback also failed: {e2}", "warning")
        return []

    def transcript_to_text(self, segments: list[TranscriptSegment], max_chars: int = 10000) -> str:
        text = " ".join(s.text for s in segments)
        return text[:max_chars]

    async def execute(self, **kwargs) -> dict:
        url = kwargs.get("url", "")
        video_id = self.extract_video_id(url)
        if not video_id:
            return {"status": "error", "error": "Invalid YouTube URL"}

        metadata = await self.get_metadata(video_id)
        segments = await self.get_transcript(video_id)
        transcript_text = self.transcript_to_text(segments)

        return {
            "status": "ok",
            "platform": PlatformInfo(name="youtube", url=url, video_id=video_id).dict(),
            "metadata": metadata.dict() if metadata else {},
            "transcript_text": transcript_text,
            "transcript_segments": [s.dict() for s in segments],
        }
