from __future__ import annotations

from datetime import datetime
from typing import Iterable

from src.collectors.base import BaseCollector
from src.models import PostRecord


class DCInsideCollector(BaseCollector):
    platform = "dcinside"

    def collect(self, keywords: list[str], limit: int = 20) -> Iterable[PostRecord]:
        # TODO: 디시 검색 페이지 파서로 교체
        for i, keyword in enumerate(keywords[:limit], start=1):
            yield PostRecord(
                id=f"dc-{i}",
                platform="dcinside",
                url=f"https://gall.dcinside.com/board/view/?id=example&no={2000+i}",
                pc_url=f"https://gall.dcinside.com/board/view/?id=example&no={2000+i}",
                author_id="dc_ko_user",
                is_domestic_account=True,
                detected_language="ko",
                created_at=datetime(2026, 3, 2, 10, 30, 0),
                is_2026_post=True,
                content_excerpt=f"{keyword} 맥락 게시물 예시",
            )
