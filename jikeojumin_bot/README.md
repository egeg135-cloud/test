# 지켜줌인 반자동화 MVP

활동가이드 기준의 반자동화 흐름(매체 선택 → 검색어 입력 → 맥락 검토 → 캡처 → 매체 내 신고 → 보고서 등록)에 맞춘 MVP입니다.

## 반영된 핵심 규칙

- 한국어 게시물만 1차 통과
- 2026년 작성 게시물만 통과
- 국내 계정 후보만 통과(최종 확정은 수동)
- PC URL만 통과
- 자동 분류는 초안만 제공, 최종 판정은 사람 검토

## X(트위터) 우선 운영

- `collect` 기본값이 `--site x`로 설정되어 X 수집을 우선합니다.
- `export` 시 위험글 링크만 모은 `data/exports/risky_links.txt`를 함께 생성해 바로 복사/붙여넣기할 수 있습니다.

## 약물자해 키워드 반영

- `configs/keywords_ko.txt`에 `ㄷㅂㅈㅅ`, `약물자해`, `쿨드림`을 추가했습니다.
- 해당 키워드는 분류 시 `유해정보-자해에 대한 막연한 감정 표현` 후보로 우선 태깅됩니다.

## 구조

- `configs/keywords_ko.txt`: 검색어 사전
- `configs/sites.yaml`: 매체 설정(스타터)
- `configs/rules.yaml`: 필터/분류 규칙
- `data/raw_posts/posts.sqlite3`: 수집 결과 저장 DB
- `data/exports/review_queue.csv`: SIMS 입력용 검토 CSV
- `data/exports/risky_links.txt`: 위험글 PC URL 목록(복사용)
- `review_queue.csv`의 `캡처기준URL`: 실제 캡처 기준 URL 검증용

## 실행

```bash
cd jikeojumin_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env

# 기본값이 X 수집
python -m src.main collect --max-per-keyword 20

# 필요시 전체 매체
python -m src.main collect --site all --max-per-keyword 10

python -m src.main export --out data/exports/review_queue.csv --links-out data/exports/risky_links.txt
```

## 현재 버전 한계

- `x`, `dcinside` 수집기는 샘플/스타터 구현입니다. 실제 운영 전 사이트 구조에 맞춰 셀렉터/API 연동이 필요합니다.
- `domestic_account_candidate` 성격의 필드는 자동 확정이 아니며, 해외계정 반려 위험을 피하기 위해 사람이 최종 확인해야 합니다.
- `--capture`는 페이지 접근/로그인 상태에 따라 실패할 수 있습니다.
