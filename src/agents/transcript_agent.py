"""Transcript agent — extracts text content from any platform."""

import html
import logging
import re
from urllib.parse import urlparse
from src.agents.base_agent import BaseAgent
from src.agents.youtube_agent import YouTubeAgent
from src.agents.browser_agent import BrowserAgent
from src.models.schemas import PlatformInfo, VideoMetadata

logger = logging.getLogger(__name__)


class TranscriptAgent(BaseAgent):
    def __init__(self):
        super().__init__("TranscriptAgent")
        self.youtube = YouTubeAgent()
        self.browser = BrowserAgent()

    async def extract(self, url: str) -> dict:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if any(x in domain for x in ["youtube.com", "youtu.be"]):
            return await self.youtube.execute(url=url)

        platform_name = self._detect_platform(domain)
        if not platform_name:
            return {"status": "error", "error": f"Unsupported platform: {domain}"}

        title, description = "", ""
        if platform_name in ("facebook", "instagram", "tiktok"):
            meta = await self._fetch_page_metadata(url)
            if meta:
                title, description = meta

        if platform_name == "facebook":
            doc_url = self._facebook_share_to_direct(url)
            if doc_url:
                fb_meta = await self._fetch_page_metadata(doc_url)
                if fb_meta and fb_meta[0] and not title:
                    title, description = fb_meta

        if title:
            title = html.unescape(title).strip()
            if len(title) > 120:
                title = title[:117] + "..."
        if description:
            description = html.unescape(description).strip()

        self.log(f"Platform: {platform_name} | Title: {title[:50] if title else 'unknown'}")
        content = await self._try_browser_extract(url, platform_name)

        if content:
            platform = PlatformInfo(
                name=platform_name, url=url,
                video_id=self._extract_id_from_url(url)
            )
            return {
                "status": "ok",
                "platform": platform.dict(),
                "metadata": VideoMetadata(
                    title=title or url, description=description[:2000]
                ).dict(),
                "transcript_text": content[:15000],
                "transcript_segments": [],
            }

        if title or description:
            platform = PlatformInfo(
                name=platform_name, url=url,
                video_id=self._extract_id_from_url(url)
            )
            return {
                "status": "ok",
                "platform": platform.dict(),
                "metadata": VideoMetadata(
                    title=title or url, description=description[:2000]
                ).dict(),
                "transcript_text": f"{title} {description}",
                "transcript_segments": [],
            }

        return {"status": "error", "error": f"Could not extract content from {url}"}

    def _detect_platform(self, domain: str) -> str:
        domain = domain.lower()
        if "youtube.com" in domain or "youtu.be" in domain:
            return "youtube"
        if "facebook.com" in domain or "fb.com" in domain or "fb.watch" in domain:
            return "facebook"
        if "instagram.com" in domain:
            return "instagram"
        if "tiktok.com" in domain:
            return "tiktok"
        return ""

    async def _fetch_page_metadata(self, url: str) -> tuple:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                })
                if resp.status_code == 200:
                    html = resp.text
                    title = ""
                    desc = ""
                    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html, re.I)
                    if m:
                        title = m.group(1)
                    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.I)
                    if m:
                        desc = m.group(1)
                    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html, re.I)
                    if m and not desc:
                        desc = m.group(1)
                    if not title:
                        m = re.search(r'<title>([^<]+)</title>', html, re.I)
                        if m:
                            title = m.group(1).strip()
                    return (title, desc)
        except Exception as e:
            self.log(f"HTTP metadata fetch failed: {e}", "warning")
        return ("", "")

    def _facebook_share_to_direct(self, url: str) -> str:
        m = re.search(r'facebook\.com/share/(?:r|v)/([^/\s?]+)', url)
        if m:
            return f"https://www.facebook.com/plugins/video.php?href={url}"
        return ""

    async def _try_browser_extract(self, url: str, platform: str) -> str:
        try:
            if not self.browser._context:
                await self.browser.launch()
            else:
                try:
                    await self.browser.login_with_cookies(platform)
                except Exception:
                    pass
            content = await self.browser.get_page_content(url)
            if content and len(content.strip()) > 100:
                return content
        except Exception as e:
            self.log(f"Browser extract failed: {e}", "warning")
        return ""

    @staticmethod
    def _extract_id_from_url(url: str) -> str:
        patterns = [
            r"(?:instagram\.com/p/|reel/)([\w-]+)",
            r"(?:facebook\.com/.*?/videos/)(\d+)",
            r"(?:tiktok\.com/@[\w.-]+/video/)(\d+)",
            r"facebook\.com/share/(?:r|v)/([^/\s?]+)",
            r"fb\.watch/([\w-]+)",
        ]
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                return m.group(1)
        return ""

    async def execute(self, **kwargs) -> dict:
        url = kwargs.get("url", "")
        result = await self.extract(url)
        try:
            await self.browser.close()
        except Exception:
            pass
        return result
