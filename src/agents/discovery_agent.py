"""Discovery agent — searches social platforms for AI and VibeCoding content."""

import asyncio
import logging
from typing import List, Dict
from src.agents.base_agent import BaseAgent
from src.agents.browser_agent import BrowserAgent

logger = logging.getLogger(__name__)

class DiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__("DiscoveryAgent")
        self.browser = BrowserAgent()

    async def discover(self, keywords: List[str], platforms: List[str] = ["youtube", "tiktok", "instagram"], limit: int = 5) -> Dict[str, List[str]]:
        results = {}
        for platform in platforms:
            self.log(f"Searching {platform} for keywords: {keywords}")
            urls = []
            for kw in keywords:
                if len(urls) >= limit:
                    break
                
                found = await self._search_platform(platform, kw, limit - len(urls))
                urls.extend(found)
            
            results[platform] = list(set(urls))[:limit]
        
        await self.browser.close()
        return results

    async def _search_platform(self, platform: str, keyword: str, limit: int) -> List[str]:
        if not self.browser._context:
            await self.browser.launch(headless=True)

        keyword_encoded = keyword.replace(" ", "+")
        urls = []

        if platform == "youtube":
            search_url = f"https://www.youtube.com/results?search_query={keyword_encoded}+shorts"
            await self.browser.navigate(search_url)
            page = self.browser.page
            if not page:
                return []
            
            # Wait for content to load
            try:
                await page.wait_for_selector("a#video-title", timeout=10000)
            except:
                self.log("Timeout waiting for YouTube search results", "warning")
            
            links = await page.query_selector_all("a[href*='/shorts/'], a[href*='/watch?v=']")
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    full_url = f"https://www.youtube.com{href}" if href.startswith("/") else href
                    if full_url not in urls:
                        urls.append(full_url)
                if len(urls) >= limit:
                    break

        elif platform == "tiktok":
            search_url = f"https://www.tiktok.com/search?q={keyword_encoded}"
            await self.browser.navigate(search_url)
            page = self.browser.page
            if not page:
                return []
            await asyncio.sleep(2) # Give it time to render
            
            links = await page.query_selector_all("a[href*='/video/']")
            for link in links:
                href = await link.get_attribute("href")
                if href and href not in urls:
                    urls.append(href)
                if len(urls) >= limit:
                    break

        elif platform == "instagram":
            search_url = f"https://www.instagram.com/explore/tags/{keyword_encoded.replace('+', '')}/"
            # Instagram often requires login for search, we'll try to use cookies if they exist
            await self.browser.login_with_cookies("instagram")
            await self.browser.navigate(search_url)
            page = self.browser.page
            if not page:
                return []
            await asyncio.sleep(2)
            
            links = await page.query_selector_all("a[href*='/reels/'], a[href*='/p/']")
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    full_url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                    if full_url not in urls:
                        urls.append(full_url)
                if len(urls) >= limit:
                    break

        return urls

    async def execute(self, **kwargs) -> dict:
        keywords = kwargs.get("keywords", ["AI", "VibeCoding"])
        platforms = kwargs.get("platforms", ["youtube", "tiktok", "instagram"])
        limit = kwargs.get("limit", 5)
        
        results = await self.discover(keywords, platforms, limit)
        return {"results": results, "status": "ok"}
