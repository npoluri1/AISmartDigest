"""Application configuration loaded from environment."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "AISmartDigest")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # LLM
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "llama3")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_api_base: str = os.getenv("LLM_API_BASE", "http://localhost:11434")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    llm_timeout: int = int(os.getenv("LLM_TIMEOUT", "120"))

    # Browser
    browser_headless: bool = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
    browser_slow_mo: int = int(os.getenv("BROWSER_SLOW_MO", "500"))
    browser_cookie_dir: str = os.getenv("BROWSER_COOKIE_DIR", "./cookies")

    # Storage
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/smart_digest.db")
    output_dir: str = os.getenv("OUTPUT_DIR", "./data/output")

    # Platform credentials (optional — for cookie-less API access)
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")

    # Processing
    max_concurrent: int = int(os.getenv("MAX_CONCURRENT", "3"))
    max_transcript_length: int = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "15000"))
    
    # Monitoring
    monitor_interval: int = int(os.getenv("MONITOR_INTERVAL", "3600")) # Default 1 hour


settings = Settings()
