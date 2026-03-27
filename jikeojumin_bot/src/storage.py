from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from src.models import PostRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT NOT NULL,
    pc_url TEXT NOT NULL,
    author_id TEXT NOT NULL,
    is_domestic_account INTEGER NOT NULL,
    detected_language TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_2026_post INTEGER NOT NULL,
    content_excerpt TEXT NOT NULL,
    risk_category_major TEXT NOT NULL,
    risk_category_minor TEXT NOT NULL,
    evidence_text TEXT NOT NULL,
    report_reason_draft TEXT NOT NULL,
    report_done INTEGER NOT NULL,
    sims_ready INTEGER NOT NULL,
    screenshot_path TEXT,
    duplicate_hash TEXT,
    review_status TEXT NOT NULL,
    review_memo TEXT NOT NULL
);
"""


def get_conn(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(SCHEMA)
    return conn


def upsert_posts(conn: sqlite3.Connection, posts: Iterable[PostRecord]) -> int:
    sql = """
    INSERT INTO posts (
      id, platform, url, pc_url, author_id, is_domestic_account, detected_language,
      created_at, is_2026_post, content_excerpt, risk_category_major, risk_category_minor,
      evidence_text, report_reason_draft, report_done, sims_ready, screenshot_path,
      duplicate_hash, review_status, review_memo
    ) VALUES (
      :id, :platform, :url, :pc_url, :author_id, :is_domestic_account, :detected_language,
      :created_at, :is_2026_post, :content_excerpt, :risk_category_major, :risk_category_minor,
      :evidence_text, :report_reason_draft, :report_done, :sims_ready, :screenshot_path,
      :duplicate_hash, :review_status, :review_memo
    )
    ON CONFLICT(id) DO UPDATE SET
      risk_category_major=excluded.risk_category_major,
      risk_category_minor=excluded.risk_category_minor,
      evidence_text=excluded.evidence_text,
      report_reason_draft=excluded.report_reason_draft,
      screenshot_path=COALESCE(excluded.screenshot_path, posts.screenshot_path),
      duplicate_hash=excluded.duplicate_hash,
      review_status=excluded.review_status,
      review_memo=excluded.review_memo;
    """
    count = 0
    for p in posts:
        row = p.to_dict()
        row["is_domestic_account"] = int(p.is_domestic_account)
        row["is_2026_post"] = int(p.is_2026_post)
        row["report_done"] = int(p.report_done)
        row["sims_ready"] = int(p.sims_ready)
        conn.execute(sql, row)
        count += 1
    conn.commit()
    return count


def load_sims_ready_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    query = """
    SELECT risk_category_major, risk_category_minor, pc_url, platform, author_id, created_at,
           report_done, report_reason_draft, screenshot_path, detected_language,
           is_2026_post, is_domestic_account
    FROM posts
    WHERE sims_ready = 1
    ORDER BY created_at DESC
    """
    return list(conn.execute(query))
