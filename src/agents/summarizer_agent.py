"""Summarizer agent — uses LLM or fallback extraction to get AI insights from video content."""

import json
import logging
import re
from datetime import datetime, timezone
from src.agents.base_agent import BaseAgent
from src.models.schemas import ExtractedInfo, DigestEntry
from src.config import settings

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = """You are an AI research analyst. Analyze the video content below and extract key intelligence.
Focus on: AI tools, AI models, frameworks, key insights, latest news/updates.

Output ONLY valid JSON with this exact structure:
{
  "ai_tools": ["name of each AI tool mentioned"],
  "ai_models": ["name of each AI model mentioned"],
  "key_frameworks": ["frameworks/libraries"],
  "key_insights": ["each key takeaway as a bullet point"],
  "latest_news": ["specific news/updates/announcements"],
  "categories": ["content categories like: tool-review, model-release, news, tutorial, comparison"],
  "summary": "2-3 sentence concise summary",
  "relevance_score": 1-10
}

If no AI-relevant content found, set relevance_score to 1 and summary to 'No AI-relevant content detected'."""

KNOWN_AI_TOOLS = [
    "ChatGPT", "GPT-4", "GPT-4o", "GPT-5", "Claude", "Claude 3.5", "Claude 4",
    "Gemini", "Gemini 2", "Gemini 2.5", "Llama", "Llama 3", "Llama 4",
    "Mistral", "DeepSeek", "Qwen", "Command R+", "Grok",
    "Cursor", "Copilot", "GitHub Copilot", "Codeium", "Windsurf", "Replit",
    "v0", "bolt.new", "lovable", "Tempo", "Builder.io",
    "LangChain", "LangGraph", "LlamaIndex", "Haystack", "Semantic Kernel",
    "PyTorch", "TensorFlow", "JAX", "Transformers", "diffusers",
    "Ollama", "vLLM", "TGI", "TensorRT-LLM", "llama.cpp",
    "OpenAI", "Anthropic", "Google AI", "Meta AI", "Mistral AI",
    "Hugging Face", "Perplexity", "Midjourney", "DALL-E", "Stable Diffusion",
    "Runway", "Sora", "Pika", "HeyGen", "ElevenLabs",
    "AutoGPT", "CrewAI", "LangGraph", "AutoGen", "Dify",
    "RAG", "Agent", "Vector Database", "Chroma", "Pinecone", "Weaviate",
    "Fine-tuning", "LoRA", "RLHF", "RAG", "Agentic",
    "VibeCoding", "Cline", "Devin", "SWE-agent", "OpenHands",
]

KNOWN_AI_MODELS = [
    "GPT-4", "GPT-4o", "GPT-4o-mini", "GPT-5", "o1", "o3",
    "Claude 3.5 Sonnet", "Claude 3 Opus", "Claude 4", "Claude 4 Sonnet",
    "Gemini 2.0", "Gemini 2.5 Pro", "Gemini 2.5 Flash",
    "Llama 3.1", "Llama 3.2", "Llama 3.3", "Llama 4",
    "Mistral Large", "Mistral Small", "Mixtral",
    "DeepSeek-V3", "DeepSeek-R1", "DeepSeek-Coder",
    "Qwen2.5", "Qwen2.5-Coder", "Qwen-VL",
    "Command R+", "Command R7B",
    "Grok-2", "Grok-3",
    "Stable Diffusion 3", "SDXL", "Flux",
    "DALL-E 3", "Midjourney 6",
    "Sora", "Veo 2",
]


class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummarizerAgent")

    async def summarize(self, url: str, platform: str, title: str, transcript_text: str, metadata: dict) -> DigestEntry:
        now = datetime.now(timezone.utc).isoformat()

        if not transcript_text or len(transcript_text.strip()) < 50:
            return DigestEntry(
                url=url, platform=platform, title=title,
                summary="Insufficient content to summarize",
                processed_at=now,
                error="Content too short",
            )

        truncated = transcript_text[:settings.max_transcript_length]
        prompt = f"""Video Title: {title}
Platform: {platform}
Description: {metadata.get('description', '')[:500]}

Transcript Content:
{truncated}

Analyze the above video content and extract all AI-related intelligence."""

        try:
            raw = await self.llm.generate(prompt, SUMMARY_SYSTEM_PROMPT)
            data = self.llm.extract_json(raw)
            info = ExtractedInfo(**data)
        except Exception as e:
            self.log(f"LLM failed ({e}), using fallback extraction")
            info = self._fallback_extract(title, transcript_text, metadata)

        return DigestEntry(
            url=url,
            platform=platform,
            title=title,
            summary=info.summary,
            ai_tools=info.ai_tools,
            ai_models=info.ai_models,
            key_insights=info.key_insights,
            latest_news=info.latest_news,
            categories=info.categories,
            relevance_score=info.relevance_score,
            raw_text=transcript_text[:2000],
            processed_at=now,
        )

    def _fallback_extract(self, title: str, transcript: str, metadata: dict) -> ExtractedInfo:
        content = f"{title} {metadata.get('description', '')} {transcript}".lower()

        found_tools = []
        for tool in KNOWN_AI_TOOLS:
            if tool.lower() in content:
                found_tools.append(tool)

        found_models = []
        for model in KNOWN_AI_MODELS:
            if model.lower() in content or model.lower().replace(" ", "") in content.replace(" ", ""):
                found_models.append(model)

        found_tools = list(dict.fromkeys(found_tools))[:15]
        found_models = list(dict.fromkeys(found_models))[:10]

        desc = metadata.get('description', '')[:300]
        tag_str = " ".join(metadata.get('tags', []))[:200]
        author = metadata.get('author', metadata.get('uploader', ''))
        views = metadata.get('view_count', 0)

        summary_parts = []
        if title:
            summary_parts.append(title)
        if desc:
            summary_parts.append(desc)
        if found_tools:
            summary_parts.append(f"Mentions: {', '.join(found_tools[:5])}")
        if not summary_parts:
            summary_parts.append(f"Video by {author}" if author else transcript[:200])

        unique_cats = set()
        for tag in metadata.get('tags', []):
            tag_lower = tag.lower()
            if 'tutorial' in tag_lower or 'guide' in tag_lower:
                unique_cats.add('tutorial')
            elif 'review' in tag_lower:
                unique_cats.add('review')
            elif 'news' in tag_lower:
                unique_cats.add('news')
            elif 'comparison' in tag_lower:
                unique_cats.add('comparison')
        if not unique_cats:
            if found_tools:
                unique_cats.add('tool-review')
            if found_models:
                unique_cats.add('model-discussion')
        unique_cats.add('ai-development')

        relevance = 5
        if len(found_tools) >= 3:
            relevance = 8
        elif len(found_tools) >= 1:
            relevance = 6
        if len(found_models) >= 2:
            relevance = min(10, relevance + 2)
        if views > 50000:
            relevance = min(10, relevance + 1)

        insights = []
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        ai_sentences = [s for s in sentences if any(kw.lower() in s.lower() for kw in
                        ['ai', 'artificial intelligence', 'model', 'tool', 'framework', 'agent', 'llm', 'gpt', 'claude', 'gemini', 'neural',
                         'deep learning', 'machine learning', 'training'])]
        for s in ai_sentences[:5]:
            s = s.strip()
            if len(s) > 30:
                insights.append(s[:200])

        news = []
        news_sentences = [s for s in sentences if any(kw.lower() in s.lower() for kw in
                          ['announce', 'release', 'launch', 'new', 'update', 'introduc', 'beta'])]
        for s in news_sentences[:3]:
            s = s.strip()
            if len(s) > 30:
                news.append(s[:200])

        summary = ". ".join(summary_parts[:3])
        if len(summary) > 500:
            summary = summary[:497] + "..."

        return ExtractedInfo(
            ai_tools=found_tools,
            ai_models=found_models,
            key_frameworks=[],
            key_insights=insights,
            latest_news=news,
            categories=list(unique_cats),
            summary=summary,
            relevance_score=relevance,
        )

    async def execute(self, **kwargs) -> dict:
        url = kwargs.get("url", "")
        platform = kwargs.get("platform", "")
        title = kwargs.get("title", "")
        transcript_text = kwargs.get("transcript_text", "")
        metadata = kwargs.get("metadata", {})

        entry = await self.summarize(url, platform, title, transcript_text, metadata)
        return {"entry": entry.dict(), "status": "ok"}
