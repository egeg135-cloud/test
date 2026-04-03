from __future__ import annotations

from src.models import PostRecord


def build_report_reason(post: PostRecord) -> str:
    return (
        f"[{post.platform}] 게시물에서 '{post.risk_category_minor}' 유형 정황이 확인되었습니다. "
        f"근거: {post.evidence_text}. 매체 내 신고 완료 후 SIMS 등록용 초안입니다."
    )


def to_sims_row(post: PostRecord) -> dict:
    return {
        "구분": post.risk_category_major,
        "유형": post.risk_category_minor,
        "URL": post.pc_url,
        "사이트명": post.platform,
        "작성자": post.author_id,
        "작성일": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "매체내신고": "Y" if post.report_done else "N",
        "설명문초안": post.report_reason_draft,
        "이미지경로": post.screenshot_path or "",
    }
