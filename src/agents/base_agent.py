"""Base agent class with shared utilities."""

import logging
from abc import ABC, abstractmethod
from src.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.llm = LLMClient()

    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        ...

    def log(self, msg: str, level: str = "info"):
        getattr(logger, level)(f"[{self.name}] {msg}")
