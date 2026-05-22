"""Browser agent — uses Playwright to automate login and scrape content like a human."""

import asyncio
import logging
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.utils.cookie_manager import CookieManager
from src.config import settings

logger = logging.getLogger(__name__)


class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__("BrowserAgent")
        self.cookie_mgr = CookieManager()
        self._browser = None
        self._context = None

    async def launch(self, headless: Optional[bool] = None):
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=headless if headless is not None else settings.browser_headless,
            slow_mo=settings.browser_slow_mo,
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        self.log("Browser launched")

    async def login_with_cookies(self, platform: str) -> bool:
        cookies = self.cookie_mgr.load_cookies(platform)
        if not cookies:
            self.log(f"No cookies for {platform}", "warning")
            return False
        if self._context:
            await self._context.add_cookies(cookies)
            self.log(f"Loaded {len(cookies)} cookies for {platform}")
            return True
        return False

    @property
    def page(self):
        if not self._context:
            return None
        if not self._context.pages:
            return None
        return self._context.pages[-1]

    async def navigate(self, url: str, wait_until: str = "networkidle") -> str:
        if not self._context:
            await self.launch()
        
        # Ensure at least one page exists
        if not self._context.pages:
            await self._context.new_page()
            
        page = self.page
        try:
            await page.goto(url, wait_until=wait_until, timeout=30000)
            await page.wait_for_timeout(2000)
            content = await page.content()
            title = await page.title()
            self.log(f"Navigated to: {title}")
            return content
        except Exception as e:
            self.log(f"Navigation error: {e}", "error")
            return ""

    async def get_page_content(self, url: str) -> str:
        if not self._context:
            await self.launch()
        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            text = await page.inner_text("body")
            return text[:50000]
        except Exception as e:
            self.log(f"Page load error: {e}", "error")
            return ""
        finally:
            await page.close()

    async def scroll_and_collect(self, url: str, scrolls: int = 3) -> str:
        if not self._context:
            await self.launch()
        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            for i in range(scrolls):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(2000)
            return await page.inner_text("body")[:50000]
        finally:
            await page.close()

    async def close(self):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if hasattr(self, '_playwright'):
            await self._playwright.stop()
        self.log("Browser closed")

    async def execute(self, **kwargs) -> dict:
        action = kwargs.get("action", "navigate")
        url = kwargs.get("url", "")
        if action == "navigate":
            content = await self.get_page_content(url)
            return {"content": content, "url": url, "status": "ok"}
        return {"status": "unknown_action"}
