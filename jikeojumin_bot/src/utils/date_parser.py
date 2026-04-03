from datetime import datetime


def parse_date(raw: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"지원하지 않는 날짜 형식: {raw}")


def is_target_year(dt: datetime, year: int = 2026) -> bool:
    return dt.year == year
