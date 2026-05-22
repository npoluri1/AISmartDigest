"""Cookie setup helper — run this to export browser cookies for platforms."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.browser_agent import BrowserAgent
from src.utils.cookie_manager import CookieManager


async def setup(platform: str, login_url: str):
    agent = BrowserAgent()
    cm = CookieManager()

    print(f"\n🔐 Opening browser to {login_url}...")
    print("👉 Please log in manually, then press ENTER here to save cookies.\n")

    await agent.launch(headless=False)
    page = await agent._context.new_page()
    await page.goto(login_url, wait_until="networkidle")
    input("Press ENTER after logging in...")

    cookies = await agent._context.cookies()
    cm.save_cookies(platform, cookies)
    await agent.close()
    print(f"✅ Saved {len(cookies)} cookies for '{platform}'")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export browser cookies for a platform")
    parser.add_argument("platform", help="Platform name (instagram, facebook, tiktok)")
    parser.add_argument("--url", help="Login URL (auto-detected if not provided)")
    args = parser.parse_args()

    url = args.url or f"https://www.{args.platform}.com"
    asyncio.run(setup(args.platform, url))
