"""AISmartDigest Streamlit Dashboard — browse digests, view stats, process videos."""

import asyncio
import os
import sys
from pathlib import Path

# Ensure project root is in path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

# Must be first Streamlit command
st.set_page_config(
    page_title="AISmartDigest",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.config import settings
from src.storage.database import Database
from src.models.schemas import DigestEntry

# ── Page config ──────────────────────────────────────────────────────

PAGES = {
    "Dashboard": "dashboard",
    "Digests": "digests",
    "Search": "search",
    "Trending": "trending",
    "Process": "process",
    "About": "about",
}


# ── Helpers ───────────────────────────────────────────────────────────

def get_db() -> Database:
    db_url = settings.database_url
    return Database(db_url)


def safe_get_stats(db: Database):
    try:
        return db.get_stats()
    except Exception as e:
        return None


@st.cache_data(ttl=10)
def get_entries_cached(limit=100, offset=0):
    db = get_db()
    return db.get_all_entries(limit=limit, offset=offset)


@st.cache_data(ttl=10)
def get_stats_cached():
    db = get_db()
    report = db.get_stats()
    entries = db.get_all_entries(limit=100, offset=0)
    entries.sort(key=lambda e: e.relevance_score or 0, reverse=True)
    return report, entries[:10]


@st.cache_data(ttl=10)
def search_entries_cached(query: str, limit=50):
    db = get_db()
    return db.search_entries(query, limit=limit)


def truncate(text: str, n: int = 60) -> str:
    return text[:n] + "..." if len(text) > n else text


# ── Sidebar ────────────────────────────────────────────────────────────

st.sidebar.image(
    "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png",
    width=48,
)
st.sidebar.title("AISmartDigest")
st.sidebar.caption("AI-powered video intelligence")

page = st.sidebar.radio("Navigate", list(PAGES.keys()))

st.sidebar.divider()
st.sidebar.caption(f"v{settings.app_version}")
provider = settings.llm_provider.upper()
st.sidebar.caption(f"LLM: {provider}")
st.sidebar.caption(f"DB: `{settings.database_url}`")

# Check DB
db = get_db()
try:
    stats_report = safe_get_stats(db)
    if stats_report:
        st.sidebar.metric("Total Digests", stats_report.total_processed)
        st.sidebar.metric("Errors", stats_report.total_errors)
    else:
        st.sidebar.warning("DB not initialized")
except Exception:
    st.sidebar.warning("Database unavailable")


# ── Pages ──────────────────────────────────────────────────────────────

def page_dashboard():
    st.title("📊 Dashboard")
    report, top_entries = get_stats_cached()

    if not report or report.total_processed == 0:
        st.info("No digests processed yet. Go to **Process** to add some, or run `python src/main.py process` from CLI.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Videos", report.total_processed)
    col2.metric("Errors", report.total_errors)
    col3.metric("Unique Tools", len(report.top_tools))
    col4.metric("Categories", len(report.top_categories))

    st.subheader("🏆 Top AI Tools")
    if report.top_tools:
        cols = st.columns(len(report.top_tools[:5]))
        for i, (tool, count) in enumerate(report.top_tools[:5]):
            cols[i].metric(tool, count)
    else:
        st.caption("No tools found yet.")

    st.subheader("🔥 Top Entries (by relevance)")
    for e in top_entries:
        with st.container(border=True):
            cc = st.columns([3, 1, 1])
            cc[0].markdown(f"**{e.title or 'Untitled'}**")
            cc[0].caption(f"{e.platform} · Score: {e.relevance_score}/10")
            tools = ", ".join(e.ai_tools[:4]) if e.ai_tools else "—"
            cc[1].markdown(f"*Tools:* {truncate(tools, 30)}")
            cc[2].markdown(f"*Models:* {truncate(', '.join(e.ai_models[:3]), 30)}" if e.ai_models else "—")
            with st.expander("Summary"):
                st.write(e.summary or "No summary")
                if e.key_insights:
                    st.markdown("**Key Insights:**")
                    for ins in e.key_insights[:5]:
                        st.markdown(f"- {ins}")


def page_digests():
    st.title("📋 Digests")

    col1, col2 = st.columns([4, 1])
    with col1:
        platform_filter = st.selectbox("Platform", ["All", "youtube", "instagram", "facebook", "tiktok"])
    with col2:
        sort_by = st.selectbox("Sort by", ["Date", "Score"])

    limit = st.slider("Entries", 10, 200, 50, step=10)
    entries = get_entries_cached(limit=limit, offset=0)

    if platform_filter != "All":
        entries = [e for e in entries if e.platform.lower() == platform_filter]
    if sort_by == "Score":
        entries.sort(key=lambda e: e.relevance_score or 0, reverse=True)

    if not entries:
        st.info("No digests found.")
        return

    st.caption(f"Showing {len(entries)} entries")
    for e in entries:
        with st.container(border=True):
            cc = st.columns([3, 1, 1, 1])
            cc[0].markdown(f"**{e.title or 'Untitled'}**")
            cc[1].markdown(f"`{e.platform}`")
            cc[2].markdown(f"**{e.relevance_score}/10**")
            cc[3].markdown(f"*{truncate(e.processed_at[:10] if e.processed_at else '—', 12)}*")
            with st.expander("Details"):
                st.markdown(f"**URL:** [{truncate(e.url, 60)}]({e.url})")
                st.markdown(f"**Summary:** {e.summary or '—'}")
                if e.ai_tools:
                    st.markdown(f"**Tools:** {', '.join(e.ai_tools)}")
                if e.ai_models:
                    st.markdown(f"**Models:** {', '.join(e.ai_models)}")
                if e.key_insights:
                    st.markdown("**Insights:**")
                    for ins in e.key_insights[:5]:
                        st.markdown(f"- {ins}")
                if e.error:
                    st.error(f"Error: {e.error}")


def page_search():
    st.title("🔍 Search")

    query = st.text_input("Search query", placeholder="e.g. langchain, GPT-4, Cursor...")
    if not query:
        st.info("Enter a search term to find digests.")
        return

    results = search_entries_cached(query)
    if not results:
        st.warning(f"No results for '{query}'")
        return

    st.success(f"Found {len(results)} results for '{query}'")
    for e in results[:50]:
        with st.container(border=True):
            cc = st.columns([3, 1, 1])
            cc[0].markdown(f"**{e.title or 'Untitled'}**")
            cc[1].markdown(f"Score: **{e.relevance_score}/10**")
            cc[2].markdown(f"`{e.platform}`")
            st.markdown(f"*{truncate(e.summary or 'No summary', 200)}*")
            if e.ai_tools:
                st.markdown(f"🧰 {', '.join(e.ai_tools[:6])}")


def page_trending():
    st.title("📈 Trending")
    report, _ = get_stats_cached()

    if not report or report.total_processed == 0:
        st.info("No data yet. Process some videos first.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔧 Top AI Tools")
        if report.top_tools:
            for tool, count in report.top_tools:
                st.markdown(f"- **{tool}**: {count} mentions")
        else:
            st.caption("No tools found")

    with col2:
        st.subheader("🧠 Top AI Models")
        if report.top_models:
            for model, count in report.top_models:
                st.markdown(f"- **{model}**: {count} mentions")
        else:
            st.caption("No models found")

    st.subheader("📂 Content Categories")
    if report.top_categories:
        cols = st.columns(len(report.top_categories))
        for i, (cat, count) in enumerate(report.top_categories):
            cols[i].metric(cat, count)
    else:
        st.caption("No categories found")


def page_process():
    st.title("⚙️ Process Videos")
    st.caption("Enter YouTube URLs to extract transcripts, summarize, and store.")

    urls_input = st.text_area(
        "URLs (one per line)",
        height=150,
        placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/...",
    )

    urls = [u.strip() for u in urls_input.splitlines() if u.strip()] if urls_input else []
    do_run = st.button("Process URLs", type="primary", disabled=not urls)

    if do_run and urls:
        progress_bar = st.progress(0, text="Initializing...")
        status_text = st.empty()
        results_container = st.container()

        async def run():
            from src.agents.orchestrator import Orchestrator
            orch = Orchestrator()
            results = []
            total = len(urls)
            for i, url in enumerate(urls):
                status_text.info(f"[{i+1}/{total}] Processing: {truncate(url, 60)}")
                progress_bar.progress((i) / total, text=f"Processing {i+1}/{total}")
                try:
                    entry = await orch.process_url(url)
                    results.append({"url": url, "success": True, "entry": entry})
                except Exception as e:
                    entry = DigestEntry(url=url, platform="unknown", title="", error=str(e), processed_at="")
                    results.append({"url": url, "success": False, "entry": entry})
                progress_bar.progress((i + 1) / total, text=f"Done {i+1}/{total}")
            status_text.success(f"Processed {total} URLs")
            return results

        results = asyncio.run(run())

        with results_container:
            for r in results:
                e = r["entry"]
                if e.error:
                    st.error(f"❌ {truncate(e.url, 50)} — {e.error}")
                else:
                    with st.container(border=True):
                        cc = st.columns([3, 1, 1, 1])
                        cc[0].markdown(f"**{e.title or 'Untitled'}**")
                        cc[1].markdown(f"Score: **{e.relevance_score}/10**")
                        cc[2].markdown(f"`{e.platform}`")
                        cc[3].markdown(f"🛠 {len(e.ai_tools)} tools")
                        if e.summary:
                            st.markdown(f"*{truncate(e.summary, 250)}*")
                        if e.ai_tools:
                            st.markdown(f"**Tools:** {', '.join(e.ai_tools[:8])}")
                        if e.ai_models:
                            st.markdown(f"**Models:** {', '.join(e.ai_models[:5])}")

    st.divider()
    st.subheader("ℹ️ How it works")
    st.markdown("""
1. Paste YouTube video URLs (one per line)
2. Click **Process URLs**
3. For each video, AISmartDigest extracts metadata & transcript
4. AI summarizes and extracts tools, models, and insights
5. Results are stored in the local database and displayed here
    """)


def page_about():
    st.title("ℹ️ About AISmartDigest")
    st.markdown("""
**AISmartDigest** is an AI agent that watches AI shorts and extracts key intelligence from YouTube and other platforms.

### Features
- **Multi-platform support**: YouTube, Instagram, TikTok, Facebook
- **Transcript Extraction**: Automatically extracts transcripts or page content
- **AI-Powered Summarization**: Uses LLMs (Ollama or OpenAI) to extract AI tools, models, insights, and news
- **Search & Stats**: Search through processed digests and view trending AI tools

### Configuration
Set environment variables or use Streamlit secrets:

| Secret | Description | Default |
|--------|-------------|---------|
| `LLM_PROVIDER` | `ollama` or `openai` | `ollama` |
| `LLM_API_KEY` | OpenAI API key | — |
| `LLM_API_BASE` | Ollama/OpenAI base URL | `http://localhost:11434` |
| `LLM_MODEL` | Model name | `llama3` |

### CLI Usage
```bash
# Process videos
python src/main.py process "https://youtube.com/watch?v=..."

# Discover new content
python src/main.py discover --keyword "AI" --limit 3

# Launch web dashboard
python src/main.py serve
```
    """)


# ── Router ─────────────────────────────────────────────────────────────

pages = {
    "Dashboard": page_dashboard,
    "Digests": page_digests,
    "Search": page_search,
    "Trending": page_trending,
    "Process": page_process,
    "About": page_about,
}

pages[page]()
