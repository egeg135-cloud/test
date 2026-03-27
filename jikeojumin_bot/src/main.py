from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from src.classifiers.ai_classifier import ai_draft_classification
from src.collectors.dcinside_collector import DCInsideCollector
from src.collectors.x_collector import XCollector
from src.models import PostRecord
from src.reporters.sims_draft import build_report_reason, to_sims_row
from src.utils.dedupe import make_duplicate_hash
from src.utils.lang_filter import detect_language

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "configs"
EXPORT_DIR = BASE_DIR / "data" / "exports"


def load_keywords() -> list[str]:
    path = CONFIG_DIR / "keywords_ko.txt"
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_rules() -> dict:
    with (CONFIG_DIR / "rules.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pass_filters(post: PostRecord, rules: dict) -> bool:
    filt = rules["filters"]
    if detect_language(post.content_excerpt) != filt["language"]:
        return False
    if post.created_at.year != int(filt["post_year"]):
        return False
    if bool(filt["require_domestic_account"]) and not post.is_domestic_account:
        return False
    if bool(filt["require_pc_url"]) and not post.pc_url:
        return False
    return True


def run(limit_per_platform: int = 10) -> pd.DataFrame:
    rules = load_rules()
    keywords = load_keywords()

    collectors = [XCollector(), DCInsideCollector()]
    approved_rows = []
    seen_hashes: set[str] = set()

    for collector in collectors:
        for post in collector.collect(keywords=keywords, limit=limit_per_platform):
            post.detected_language = detect_language(post.content_excerpt)
            if not pass_filters(post, rules):
                continue

            post.duplicate_hash = make_duplicate_hash(post.platform, post.pc_url, post.content_excerpt)
            if post.duplicate_hash in seen_hashes:
                continue
            seen_hashes.add(post.duplicate_hash)

            cls = ai_draft_classification(post.content_excerpt)
            post.risk_category_major = cls.major
            post.risk_category_minor = cls.minor
            post.evidence_text = cls.evidence
            post.report_reason_draft = build_report_reason(post)
            post.sims_ready = cls.major != "미분류"

            approved_rows.append(to_sims_row(post))

    df = pd.DataFrame(approved_rows)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = EXPORT_DIR / "sims_draft.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    df = run(limit_per_platform=10)
    print(f"완료: {len(df)}건 저장")
