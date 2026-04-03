from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationResult:
    major: str
    minor: str
    evidence: str
    score: float


RULES = [
    (["동반", "같이 갈"], "자살유발정보", "자살동반자 모집", 0.93),
    (["방법", "안 아프게", "어떻게"], "자살유발정보", "구체적 방법 제시", 0.9),
    (["판매", "도구", "번개탄"], "자살유발정보", "위해물건 판매/활용", 0.88),
    (["자해", "손목"], "자살유해정보", "자해 사진/동영상", 0.8),
    (["죽고싶", "끝내고싶"], "자살유해정보", "막연한 감정 표현", 0.75),
    (["약물자해", "쿨드림", "ㄷㅂㅈㅅ"], "자살유해정보", "자해에 대한 막연한 감정 표현", 0.82),
]


def classify_excerpt(text: str) -> ClassificationResult:
    normalized = (text or "").lower()
    for tokens, major, minor, score in RULES:
        if any(token in normalized for token in tokens):
            return ClassificationResult(major=major, minor=minor, evidence=text[:180], score=score)
    return ClassificationResult(major="미분류", minor="미분류", evidence=text[:180], score=0.2)
