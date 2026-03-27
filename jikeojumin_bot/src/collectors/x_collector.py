from __future__ import annotations

from datetime import datetime
from typing import Iterable

from src.collectors.base import BaseCollector
from src.models import PostRecord


class XCollector(BaseCollector):
    platform = "x"

    def collect(self, keywords: list[str], limit: int = 20) -> Iterable[PostRecord]:
        # TODO: X 검색 API 또는 Playwright 검색 구현으로 교체
        for i, keyword in enumerate(keywords[:limit], start=1):
            yield PostRecord(
                id=f"x-{i}",
                platform="x",
                url=f"https://x.com/example/status/{1000+i}",
                pc_url=f"https://x.com/example/status/{1000+i}",
                author_id="example_ko_user",
                is_domestic_account=True,
                detected_language="ko",
                created_at=datetime(2026, 3, 1, 9, 0, 0),
                is_2026_post=True,
                content_excerpt=f"{keyword} 관련 게시물 예시",
            )
