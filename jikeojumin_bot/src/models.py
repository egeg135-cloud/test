from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class PostRecord:
    id: str
    platform: str
    url: str
    pc_url: str
    author_id: str
    is_domestic_account: bool
    detected_language: str
    created_at: datetime
    is_2026_post: bool
    content_excerpt: str
    risk_category_major: str = "미분류"
    risk_category_minor: str = "미분류"
    evidence_text: str = ""
    report_reason_draft: str = ""
    report_done: bool = False
    sims_ready: bool = False
    screenshot_path: Optional[str] = None
    screenshot_source_url: Optional[str] = None
    duplicate_hash: Optional[str] = None
    review_status: str = "pending"
    review_memo: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data
