import sys
import os
import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.orchestrator import Orchestrator
from src.storage.database import Database
from src.config import settings

@pytest.mark.asyncio
async def test_full_pipeline_mocked_llm(tmp_path):
    # Setup a test database
    db_path = f"sqlite:///{tmp_path}/test_e2e.db"
    settings.database_url = db_path
    db = Database(db_path)
    
    orch = Orchestrator(db=db)
    
    # Mock LLM response
    mock_llm_response = """
    {
      "ai_tools": ["TestTool"],
      "ai_models": ["TestModel"],
      "key_frameworks": ["TestFramework"],
      "key_insights": ["Insight 1", "Insight 2"],
      "latest_news": ["News 1"],
      "categories": ["tutorial"],
      "summary": "This is a test summary from a mocked LLM.",
      "relevance_score": 9
    }
    """
    
    # Mocking YouTubeAgent and TranscriptAgent to avoid real network calls
    # OR we can let them try if we have internet, but safer to mock for CI-like test
    
    with patch("src.utils.llm_client.LLMClient.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_llm_response
        
        # We also need to mock transcript extraction if we don't want real network calls
        with patch("src.agents.youtube_agent.YouTubeAgent.execute", new_callable=AsyncMock) as mock_yt:
            mock_yt.return_value = {
                "status": "ok",
                "metadata": {"title": "Test Video", "description": "Test Description"},
                "transcript_text": "This is a test transcript about AI tools like TestTool."
            }
            
            # 1. Process a URL
            url = "https://www.youtube.com/watch?v=mock"
            entry = await orch.process_url(url)
            
            assert entry.url == url
            assert entry.title == "Test Video"
            assert "TestTool" in entry.ai_tools
            assert entry.relevance_score == 9
            
            # 2. Verify it's in the DB
            assert db.entry_exists(url) is True
            
            # 3. Search for it
            results = orch.search("TestTool")
            assert len(results) == 1
            assert results[0].title == "Test Video"
            
            # 4. Check stats
            stats = orch.get_stats()
            assert stats.total_processed == 1
            assert ("TestTool", 1) in stats.top_tools

if __name__ == "__main__":
    asyncio.run(test_full_pipeline_mocked_llm(Path("./data")))
