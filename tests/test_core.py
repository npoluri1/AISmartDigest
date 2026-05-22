"""Tests for AISmartDigest models and database."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.models.schemas import DigestEntry, ExtractedInfo, VideoMetadata, PlatformInfo
from src.storage.database import Database


class TestModels:
    def test_digest_entry_defaults(self):
        e = DigestEntry(url="https://youtube.com/watch?v=test", platform="youtube", title="Test", processed_at="2025-01-01")
        assert e.url == "https://youtube.com/watch?v=test"
        assert e.relevance_score == 5
        assert e.ai_tools == []
        assert e.error is None

    def test_extracted_info_defaults(self):
        info = ExtractedInfo(summary="Test summary")
        assert info.summary == "Test summary"
        assert info.ai_tools == []
        assert info.relevance_score == 5

    def test_video_metadata(self):
        m = VideoMetadata(title="AI Tools 2025", duration_s=300, view_count=1000)
        assert m.title == "AI Tools 2025"
        assert m.view_count == 1000

    def test_platform_info(self):
        p = PlatformInfo(name="youtube", url="https://youtube.com/watch?v=abc123", video_id="abc123")
        assert p.video_id == "abc123"


class TestDatabase:
    @pytest.fixture(autouse=True)
    def setup_db(self, tmp_path):
        self.db_path = str(tmp_path / "test.db")
        self.db = Database(self.db_path)

    def test_save_and_retrieve(self):
        entry = DigestEntry(
            url="https://youtube.com/watch?v=test123",
            platform="youtube",
            title="Test Video",
            summary="A test summary",
            ai_tools=["LangChain", "Ollama"],
            ai_models=["GPT-4"],
            categories=["tool-review"],
            relevance_score=8,
            processed_at="2025-01-01T00:00:00",
        )
        self.db.save_entry(entry)
        assert self.db.entry_exists(entry.url) is True

        entries = self.db.get_all_entries()
        assert len(entries) == 1
        assert entries[0].title == "Test Video"
        assert "LangChain" in entries[0].ai_tools

    def test_search(self):
        e1 = DigestEntry(url="https://youtube.com/watch?v=1", platform="youtube", title="LangChain Tutorial", ai_tools=["LangChain"], processed_at="2025-01-01")
        e2 = DigestEntry(url="https://youtube.com/watch?v=2", platform="youtube", title="OpenAI Updates", ai_tools=["OpenAI"], processed_at="2025-01-01")
        self.db.save_entry(e1)
        self.db.save_entry(e2)

        results = self.db.search_entries("LangChain")
        assert len(results) == 1
        assert results[0].title == "LangChain Tutorial"

    def test_stats(self):
        e1 = DigestEntry(url="https://youtube.com/watch?v=1", platform="youtube", title="Video 1", ai_tools=["ToolA"], categories=["news"], processed_at="2025-01-01")
        e2 = DigestEntry(url="https://youtube.com/watch?v=2", platform="youtube", title="Video 2", ai_tools=["ToolA", "ToolB"], categories=["tutorial"], processed_at="2025-01-01")
        self.db.save_entry(e1)
        self.db.save_entry(e2)

        report = self.db.get_stats()
        assert report.total_processed == 2
        assert ("ToolA", 2) in report.top_tools
