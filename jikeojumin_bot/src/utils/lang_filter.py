from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0


def detect_language(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"
