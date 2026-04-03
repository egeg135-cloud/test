from __future__ import annotations

from src.classifiers.keyword_rules import ClassificationResult, classify_excerpt


def ai_draft_classification(text: str) -> ClassificationResult:
    """MVP에서는 규칙 기반을 사용하고, 이후 LLM 호출로 교체."""
    return classify_excerpt(text)
