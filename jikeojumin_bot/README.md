# 지켜줌인 반자동화 MVP

이 MVP는 **X + 디시인사이드** 대상의 반자동화 파이프라인 뼈대입니다.

- 한국어 게시물 필터
- 2026년 작성 게시물 필터
- 국내 계정 필터(수집기 메타데이터 기반)
- 규칙/AI 초안 분류
- SIMS 입력용 CSV 초안 생성

## 실행

```bash
cd jikeojumin_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

출력 파일: `data/exports/sims_draft.csv`

## 주의

- 현재 수집기는 샘플 데이터를 반환하도록 구현되어 있어, 실제 배포 전 각 플랫폼별 API/크롤러로 교체해야 합니다.
- 자동 판정은 초안이며 최종 판정/신고/등록은 사람이 수행해야 합니다.
