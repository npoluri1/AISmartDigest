"""AISmartDigest CLI — process video URLs, search, and view stats."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to sys.path to allow running this script directly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.storage.database import Database
from src.agents.orchestrator import Orchestrator

app = typer.Typer(
    name="aisd",
    help="AISmartDigest — AI agent that watches AI shorts and extracts key intelligence",
)
console = Console()

logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(levelname)s | %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("yt_dlp").setLevel(logging.WARNING)


@app.command()
def process(
    urls: list[str] = typer.Argument(None, help="Video URLs to process"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to text file containing URLs (one per line)"),
    workers: int = typer.Option(3, "--workers", "-w", help="Concurrent workers"),
):
    """Process video URLs — extract transcripts, summarize, and store."""
    async def run():
        all_urls = list(urls) if urls else []
        if file:
            if not file.exists():
                console.print(f"[red]Error: File {file} not found.[/]")
                raise typer.Exit(1)
            with open(file, "r") as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                all_urls.extend(file_urls)

        if not all_urls:
            console.print("[yellow]No URLs provided. Pass them as arguments or use --file.[/]")
            raise typer.Exit()

        settings.max_concurrent = workers
        orch = Orchestrator()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task(f"Processing {len(all_urls)} videos...", total=None)
            entries = await orch.process_urls(all_urls)

        table = Table(title=f"Processed {len(entries)} videos")
        table.add_column("Title", style="cyan")
        table.add_column("Platform", style="magenta")
        table.add_column("Score", justify="right")
        table.add_column("Tools Found", style="green")
        table.add_column("Summary")

        for e in entries:
            if e.error:
                table.add_row(e.title or e.url[:40], e.platform, "—", "—", f"[red]{e.error}[/]")
            else:
                tools = ", ".join(e.ai_tools[:3]) or "—"
                table.add_row(e.title[:50], e.platform, str(e.relevance_score), tools, e.summary[:60])

        console.print(table)
        console.print(f"\n[bold green]Done![/] Top tools: {[t for t,_ in orch.get_stats().top_tools[:5]]}")

    asyncio.run(run())


@app.command()
def discover(
    keywords: list[str] = typer.Option(["AI", "VibeCoding"], "--keyword", "-k", help="Keywords to search for"),
    limit: int = typer.Option(3, "--limit", "-l", help="Limit per platform"),
):
    """Dynamically discover and process AI/VibeCoding content from social networks."""
    async def run():
        orch = Orchestrator()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(f"Hunting for content: {', '.join(keywords)}...", total=None)
            entries = await orch.discover_and_process(keywords, limit_per_platform=limit)

        table = Table(title=f"Discovered & Processed {len(entries)} videos")
        table.add_column("Title", style="cyan")
        table.add_column("Platform", style="magenta")
        table.add_column("Score", justify="right")
        table.add_column("Tools Found", style="green")

        for e in entries:
            tools = ", ".join(e.ai_tools[:3]) or "—"
            table.add_row(e.title[:50] if e.title else e.url[:40], e.platform, str(e.relevance_score), tools)

        console.print(table)
        console.print(f"\n[bold green]Discovery complete![/] Total in DB: [cyan]{orch.get_stats().total_processed}[/]")

    asyncio.run(run())


@app.command()
def monitor(
    keywords: list[str] = typer.Option(["AI", "VibeCoding", "Cursor AI"], "--keyword", "-k", help="Keywords to monitor"),
    interval: int = typer.Option(3600, "--interval", "-i", help="Check interval in seconds"),
):
    """Start autonomous AI agent to monitor social networks in the background."""
    async def run():
        console.print(f"[bold green]🚀 AISmartDigest Autonomous Agent Active[/]")
        console.print(f"Monitoring: [cyan]{', '.join(keywords)}[/]")
        console.print(f"Interval: [yellow]{interval}s[/]")
        console.print("[dim]Press Ctrl+C to stop the agent.[/]")
        
        orch = Orchestrator()
        await orch.start_monitoring(keywords, interval=interval)

    asyncio.run(run())


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-l"),
):
    """Search processed digests for AI tools, models, or keywords."""
    db = Database(settings.database_url)
    results = db.search_entries(query)

    if not results:
        console.print("[yellow]No results found[/]")
        raise typer.Exit()

    table = Table(title=f"Search results for: {query}")
    table.add_column("Title", style="cyan")
    table.add_column("Platform")
    table.add_column("Score")
    table.add_column("AI Tools", style="green")
    table.add_column("AI Models", style="blue")

    for r in results[:limit]:
        table.add_row(
            r.title[:50],
            r.platform,
            str(r.relevance_score),
            ", ".join(r.ai_tools[:3]) or "—",
            ", ".join(r.ai_models[:3]) or "—",
        )
    console.print(table)
    console.print(f"Found {len(results)} results")


@app.command()
def stats():
    """Show digest statistics and trending AI tools/models."""
    db = Database(settings.database_url)
    report = db.get_stats()

    console.print(f"\n[bold]📊 AISmartDigest Stats[/]")
    console.print(f"Total videos processed: [cyan]{report.total_processed}[/]")
    console.print(f"Errors: [red]{report.total_errors}[/]")

    if report.top_tools:
        table = Table(title="Top AI Tools Mentioned")
        table.add_column("Tool", style="green")
        table.add_column("Mentions", justify="right")
        for tool, count in report.top_tools:
            table.add_row(tool, str(count))
        console.print(table)

    if report.top_models:
        table = Table(title="Top AI Models Discussed")
        table.add_column("Model", style="blue")
        table.add_column("Mentions", justify="right")
        for model, count in report.top_models:
            table.add_row(model, str(count))
        console.print(table)

    if report.top_categories:
        table = Table(title="Content Categories")
        table.add_column("Category", style="magenta")
        table.add_column("Count", justify="right")
        for cat, count in report.top_categories:
            table.add_row(cat, str(count))
        console.print(table)


@app.command()
def setup_browser():
    """Launch browser to sign in and export cookies for a platform."""
    async def run():
        from src.agents.browser_agent import BrowserAgent
        from src.utils.cookie_manager import CookieManager

        platform = typer.prompt("Platform name (instagram/facebook/tiktok)", default="instagram")
        url = typer.prompt("Login URL", default=f"https://www.{platform}.com")
        
        # Ensure URL has a protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        console.print(f"[yellow]Opening browser to {url}...[/]")
        console.print("[yellow]Please log in manually in the browser window, then close it.[/]")

        agent = BrowserAgent()
        await agent.launch(headless=False)
        cm = CookieManager()

        page = await agent._context.new_page()
        await page.goto(url, wait_until="networkidle")
        console.print("[green]Browser is open. Please log in, then press Enter here when done...[/]")
        
        # Use to_thread to avoid blocking the event loop with input()
        await asyncio.to_thread(input)

        cookies = await agent._context.cookies()
        cm.save_cookies(platform, cookies)
        await agent.close()
        console.print(f"[bold green]✓ Saved {len(cookies)} cookies for {platform}[/]")

    asyncio.run(run())


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-H", help="Bind address"),
    port: int = typer.Option(8000, "--port", "-p", help="Port number"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Auto-reload on code changes"),
):
    """Launch the web dashboard — Apple-inspired UI for browsing digests."""
    import uvicorn
    console.print("[bold green]Starting AISmartDigest Web Dashboard...[/]")
    console.print(f"  Dashboard: [underline cyan]http://{host if host != '0.0.0.0' else 'localhost'}:{port}[/]")
    console.print(f"  API docs:  [underline cyan]http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs[/]")
    uvicorn.run("src.api.app:app", host=host, port=port, reload=reload, log_level="info")


@app.command(name="list")
def list_digests():
    """List all processed digests."""
    db = Database(settings.database_url)
    entries = db.get_all_entries(limit=50)

    if not entries:
        console.print("[yellow]No entries yet. Use 'aisd process' to add some.[/]")
        raise typer.Exit()

    table = Table(title="Recent Digests")
    table.add_column("ID")
    table.add_column("Title", style="cyan")
    table.add_column("Platform")
    table.add_column("Score")
    table.add_column("Processed")

    for e in entries:
        table.add_row(e.id, e.title[:45], e.platform, str(e.relevance_score), e.processed_at[:10])
    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
