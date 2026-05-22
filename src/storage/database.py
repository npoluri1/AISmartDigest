"""SQLite database layer for persisting digest entries."""

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from src.models.schemas import DigestEntry, DigestReport

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "./data/smart_digest.db"):
        # Handle sqlite:/// prefix if present
        clean_path = db_path.replace("sqlite:///", "")
        self.db_path = Path(clean_path)
        
        # Only try to create parent directories if it's not an in-memory database
        if clean_path != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
        return self._conn

    def _create_tables(self):
        conn = self.connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                summary TEXT,
                ai_tools TEXT DEFAULT '[]',
                ai_models TEXT DEFAULT '[]',
                key_insights TEXT DEFAULT '[]',
                latest_news TEXT DEFAULT '[]',
                categories TEXT DEFAULT '[]',
                relevance_score INTEGER DEFAULT 5,
                raw_text TEXT,
                thumbnail_url TEXT DEFAULT '',
                error TEXT,
                processed_at TEXT NOT NULL
            )
        """)
        try:
            conn.execute("ALTER TABLE digests ADD COLUMN thumbnail_url TEXT DEFAULT ''")
        except Exception:
            pass
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_platform ON digests(platform)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_processed_at ON digests(processed_at)
        """)
        conn.commit()

    def save_entry(self, entry: DigestEntry) -> int:
        conn = self.connect()
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute("""
            INSERT OR REPLACE INTO digests
                (url, platform, title, summary, ai_tools, ai_models,
                 key_insights, latest_news, categories, relevance_score,
                 raw_text, thumbnail_url, error, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.url, entry.platform, entry.title, entry.summary,
            json.dumps(entry.ai_tools), json.dumps(entry.ai_models),
            json.dumps(entry.key_insights), json.dumps(entry.latest_news),
            json.dumps(entry.categories), entry.relevance_score,
            entry.raw_text[:50000] if entry.raw_text else "",
            entry.thumbnail_url or "",
            entry.error, entry.processed_at or now,
        ))
        conn.commit()
        return cursor.lastrowid or 0

    def entry_exists(self, url: str) -> bool:
        conn = self.connect()
        row = conn.execute("SELECT 1 FROM digests WHERE url = ?", (url,)).fetchone()
        return row is not None

    def get_all_entries(self, limit: int = 100, offset: int = 0) -> list[DigestEntry]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT * FROM digests ORDER BY processed_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def search_entries(self, query: str, limit: int = 50) -> list[DigestEntry]:
        conn = self.connect()
        like = f"%{query}%"
        rows = conn.execute("""
            SELECT * FROM digests
            WHERE title LIKE ? OR summary LIKE ? OR ai_tools LIKE ? OR ai_models LIKE ?
            ORDER BY relevance_score DESC, processed_at DESC
            LIMIT ?
        """, (like, like, like, like, limit)).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def get_stats(self) -> DigestReport:
        conn = self.connect()
        entries = self.get_all_entries(limit=1000)
        total = len(entries)
        errors = sum(1 for e in entries if e.error)

        tool_counts: dict[str, int] = {}
        model_counts: dict[str, int] = {}
        cat_counts: dict[str, int] = {}
        for e in entries:
            for t in e.ai_tools:
                tool_counts[t] = tool_counts.get(t, 0) + 1
            for m in e.ai_models:
                model_counts[m] = model_counts.get(m, 0) + 1
            for c in e.categories:
                cat_counts[c] = cat_counts.get(c, 0) + 1

        return DigestReport(
            total_processed=total,
            total_errors=errors,
            entries=entries[:50],
            top_tools=sorted(tool_counts.items(), key=lambda x: -x[1])[:10],
            top_models=sorted(model_counts.items(), key=lambda x: -x[1])[:10],
            top_categories=sorted(cat_counts.items(), key=lambda x: -x[1])[:10],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> DigestEntry:
        return DigestEntry(
            id=str(row["id"]),
            url=row["url"],
            platform=row["platform"],
            title=row["title"] or "",
            summary=row["summary"] or "",
            ai_tools=json.loads(row["ai_tools"] or "[]"),
            ai_models=json.loads(row["ai_models"] or "[]"),
            key_insights=json.loads(row["key_insights"] or "[]"),
            latest_news=json.loads(row["latest_news"] or "[]"),
            categories=json.loads(row["categories"] or "[]"),
            relevance_score=row["relevance_score"] or 5,
            processed_at=row["processed_at"] or "",
            thumbnail_url=row["thumbnail_url"] or "",
            error=row["error"],
        )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
