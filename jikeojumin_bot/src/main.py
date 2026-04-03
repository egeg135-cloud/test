from __future__ import annotations

import argparse
import hashlib
import csv
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.classifiers.ai_classifier import ai_draft_classification
from src.collectors.dcinside_collector import DCInsideCollector
from src.collectors.x_collector import XCollector
from src.models import PostRecord
from src.reporters.sims_draft import build_report_reason
from src.storage import get_conn, load_sims_ready_rows, upsert_posts
from src.utils.dedupe import make_duplicate_hash
from src.utils.lang_filter import detect_language
from src.utils.screenshot import capture_page

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
CONFIG_DIR = BASE_DIR / "configs"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "raw_posts" / "posts.sqlite3"


def load_keywords() -> list[str]:
    path = CONFIG_DIR / "keywords_ko.txt"
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_rules() -> dict:
    with (CONFIG_DIR / "rules.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_pc_url(url: str) -> bool:
    return "/m." not in url and "mobile" not in url.lower()


def pass_filters(post: PostRecord, rules: dict) -> bool:
    filt = rules["filters"]
    if post.detected_language != filt["language"]:
        return False
    if post.created_at.year != int(filt["post_year"]):
        return False
    if bool(filt["require_domestic_account"]) and not post.is_domestic_account:
        return False
    if bool(filt["require_pc_url"]) and not is_pc_url(post.pc_url):
        return False
    if not post.author_id:
        return False
    return True


def build_collectors(site: str):
    all_collectors = {
        "x": XCollector(),
        "dcinside": DCInsideCollector(),
    }
    if site == "all":
        return list(all_collectors.values())
    return [all_collectors[site]]


def collect(site: str, max_per_keyword: int, capture: bool = False) -> int:
    rules = load_rules()
    keywords = load_keywords()
    collectors = build_collectors(site)

    accepted: list[PostRecord] = []
    seen_hashes: set[str] = set()

    for collector in collectors:
        for post in collector.collect(keywords=keywords, limit=max_per_keyword):
            post.detected_language = detect_language(post.content_excerpt)
            if not pass_filters(post, rules):
                continue

            post.duplicate_hash = make_duplicate_hash(post.platform, post.pc_url, post.content_excerpt)
            if post.duplicate_hash in seen_hashes:
                continue
            seen_hashes.add(post.duplicate_hash)

            classify_input = f"{post.content_excerpt} {post.pc_url}"
            cls = ai_draft_classification(classify_input)
            post.risk_category_major = cls.major
            post.risk_category_minor = cls.minor
            post.evidence_text = cls.evidence
            post.report_reason_draft = build_report_reason(post)
            post.sims_ready = cls.major != "미분류"
            post.is_2026_post = post.created_at.year == 2026

            if capture:
                url_hash = hashlib.sha1(post.pc_url.encode("utf-8", errors="ignore")).hexdigest()[:12]
                image_name = f"{post.platform}_{url_hash}.png"
                image_path = DATA_DIR / "screenshots" / image_name
                try:
                    post.screenshot_path = capture_page(post.pc_url, str(image_path))
                    post.screenshot_source_url = post.pc_url
                except Exception:
                    post.review_memo = "screenshot_failed"

            accepted.append(post)

    with get_conn(DB_PATH) as conn:
        return upsert_posts(conn, accepted)


def export_csv(out_path: Path, links_out: Path | None = None) -> int:
    with get_conn(DB_PATH) as conn:
        rows = load_sims_ready_rows(conn)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    urls: list[str] = []
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "구분",
            "유형",
            "URL(PC)",
            "사이트명",
            "작성자",
            "작성일",
            "매체내신고",
            "설명문초안",
            "이미지경로",
            "캡처기준URL",
            "언어",
            "2026게시물",
            "국내계정후보",
        ])
        for r in rows:
            urls.append(r["pc_url"])
            writer.writerow([
                r["risk_category_major"],
                r["risk_category_minor"],
                r["pc_url"],
                r["platform"],
                r["author_id"],
                r["created_at"],
                "Y" if r["report_done"] else "N",
                r["report_reason_draft"],
                r["screenshot_path"] or "",
                r["screenshot_source_url"] or "",
                r["detected_language"],
                "Y" if r["is_2026_post"] else "N",
                "Y" if r["is_domestic_account"] else "N",
            ])
    if links_out is not None:
        links_out.parent.mkdir(parents=True, exist_ok=True)
        links_out.write_text("\n".join(urls), encoding="utf-8")

    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="지켜줌인 반자동화 MVP")
    sub = parser.add_subparsers(dest="command", required=True)

    collect_cmd = sub.add_parser("collect", help="게시물 수집 및 분류 초안")
    collect_cmd.add_argument("--site", choices=["x", "dcinside", "all"], default="x")
    collect_cmd.add_argument("--max-per-keyword", type=int, default=10)
    collect_cmd.add_argument("--capture", action="store_true", help="스크린샷 캡처 실행")

    export_cmd = sub.add_parser("export", help="SIMS 입력용 CSV 내보내기")
    export_cmd.add_argument("--out", default=str(DATA_DIR / "exports" / "review_queue.csv"))
    export_cmd.add_argument("--links-out", default=str(DATA_DIR / "exports" / "risky_links.txt"))

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "collect":
        count = collect(site=args.site, max_per_keyword=args.max_per_keyword, capture=args.capture)
        print(f"collect 완료: {count}건 upsert")
    elif args.command == "export":
        out_path = Path(args.out)
        links_out = Path(args.links_out)
        count = export_csv(out_path, links_out=links_out)
        print(f"export 완료: {count}건 -> {out_path} / 링크목록 -> {links_out}")


if __name__ == "__main__":
    main()
