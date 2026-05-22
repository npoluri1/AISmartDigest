"""Cookie manager for browser-based platform authentication."""

import json
import logging
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)


class CookieManager:
    def __init__(self):
        self.cookie_dir = Path(settings.browser_cookie_dir)
        self.cookie_dir.mkdir(parents=True, exist_ok=True)

    def save_cookies(self, platform: str, cookies: list[dict]) -> Path:
        path = self.cookie_dir / f"{platform}.json"
        with open(path, "w") as f:
            json.dump(cookies, f, indent=2)
        logger.info(f"Saved {len(cookies)} cookies for {platform} to {path}")
        return path

    def load_cookies(self, platform: str) -> list[dict]:
        path = self.cookie_dir / f"{platform}.json"
        if not path.exists():
            logger.warning(f"No cookies found for {platform} at {path}")
            return []
        with open(path) as f:
            cookies = json.load(f)
        logger.info(f"Loaded {len(cookies)} cookies for {platform}")
        return cookies

    def has_cookies(self, platform: str) -> bool:
        return (self.cookie_dir / f"{platform}.json").exists()

    def list_platforms(self) -> list[str]:
        return [p.stem for p in self.cookie_dir.glob("*.json")]

    def delete_cookies(self, platform: str) -> None:
        path = self.cookie_dir / f"{platform}.json"
        if path.exists():
            path.unlink()
            logger.info(f"Deleted cookies for {platform}")
