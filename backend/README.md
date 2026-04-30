# Backend

FastAPI + LangGraph 기반 사주 AI Agent 서버.

## 구조

```
backend/
├── app/
│   ├── engine/         # 사주 계산 엔진
│   │   ├── calculator.py   # 年月日時 간지 계산
│   │   ├── constants.py    # 천간·지지·절기 상수
│   │   └── models.py       # Pillar, SajuData, SajuRequest
│   ├── rag/
│   │   ├── embedder.py     # KURE-v1 로컬 임베딩 (singleton)
│   │   ├── retriever.py    # pgvector 하이브리드 검색
│   │   └── ingester.py     # 청크 → DB 적재
│   ├── agent/
│   │   ├── graph.py        # LangGraph StateGraph 정의
│   │   └── nodes.py        # calculate / rag / interpret 노드
│   ├── api/v1/endpoints/
│   │   └── saju.py         # /calculate · /analyze · /analyze/stream
│   ├── core/
│   │   └── config.py       # pydantic-settings 환경 변수
│   └── main.py
├── scripts/
│   ├── setup_data.py        # 데이터 적재 파이프라인 (메인)
│   ├── scrape.py            # 지식 데이터 수집
│   └── verify_calculator.py # 계산 엔진 검증
├── data/
│   ├── chunks/     # RAG용 JSON 청크
│   └── raw/        # 원본 데이터
├── alembic/        # DB 마이그레이션
├── pyproject.toml
└── .env            # 환경 변수 (아래 참고)
```

## 환경 변수 (.env)

```env
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=saju_db
POSTGRES_USER=saju_user
POSTGRES_PASSWORD=saju_pass

EMBEDDING_MODEL_NAME=nlpai-lab/KURE-v1
EMBEDDING_DEVICE=cpu
EMBEDDING_DIMENSION=1024
```

## 실행

```bash
# 의존성 설치
uv sync

# DB 마이그레이션
uv run alembic upgrade head

# 데이터 적재 (스크래핑 → 마이그레이션 → pgvector 적재)
uv run python scripts/setup_data.py

# 서버 시작
uv run uvicorn app.main:app --reload --port 8000
```

### setup_data.py 옵션

```bash
uv run python scripts/setup_data.py               # 전체 실행
uv run python scripts/setup_data.py --skip-scrape  # 스크래핑 건너뜀
uv run python scripts/setup_data.py --skip-migrate # 마이그레이션 건너뜀
uv run python scripts/setup_data.py --only-ingest  # 적재만 실행
```

## API

베이스 URL: `http://localhost:8000/api/v1`

### POST `/saju/calculate`

사주팔자 계산만 수행.

**Request**
```json
{
  "birth_date": "1995-03-15",
  "birth_time": "14:30",
  "gender": "M",
  "calendar_type": "solar",
  "city": "Seoul"
}
```

- `calendar_type`: `"solar"` (양력) | `"lunar"` (음력)
- `city`: 출생지 도시명. 진태양시 보정에 사용. 기본값 `"Seoul"`. 한글(`"서울"`, `"인천"` 등)도 지원.

**Response**
```json
{
  "data": {
    "year_pillar":  { "gan": "乙", "zhi": "亥", "gan_kr": "을", "zhi_kr": "해", "gan_wuxing": "木", "zhi_wuxing": "水", "sipsung": "정인" },
    "month_pillar": { ... },
    "day_pillar":   { ... },
    "hour_pillar":  { ... },
    "daeun": [ ... ],
    "daeun_start_age": 6,
    "ohaeng_scores": { "wood": 2, "fire": 1, "earth": 2, "metal": 1, "water": 2 }
  }
}
```

### POST `/saju/session`

전체 분석 SSE 스트림 (9화면 앱용).

**Request**
```json
{
  "birth_date": "1995-03-15",
  "birth_time": "14:30",
  "gender": "M",
  "calendar_type": "solar",
  "city": "Seoul",
  "name": "홍길동",
  "relationship": "솔로",
  "question": "올해 이직해도 될까요?"
}
```

**SSE 이벤트 순서**
```
event: saju_data    → 만세력 JSON
event: personality  → 기질·성격 분석 텍스트
event: yearly       → 올해 운세 텍스트
event: monthly      → { 총운, 연애운, 재물운, 직업운, 사업운 }
event: answer       → 질문 답변 (question 있을 때만)
event: done         → { "thread_id": "..." }
```

### POST `/saju/chat`

기존 세션에 채팅 메시지 전송 (SSE 토큰 스트림).

**Request**
```json
{
  "thread_id": "...",
  "message": "내년 운세도 알려줘"
}
```

## LangGraph Agent

```
START → route_start
          ├─ (saju_data 없음)    → calculate → personality → yearly → monthly → [question] → END
          ├─ (saju_data + 메시지 없음) → personality → yearly → monthly → [question] → END
          └─ (saju_data + 메시지)  → chat → END
```

| 노드 | 역할 |
|------|------|
| `calculate` | sajupy 기반 사주팔자 계산 (진태양시 보정 포함) |
| `personality` | 기질·성격·직업 분석 |
| `yearly` | 올해 세운 분석 |
| `monthly` | 이번 달 월운 분석 |
| `question` | 선택 질문 답변 |
| `chat` | 채팅 응답 (체크포인트 복원) |

## 계산 엔진

만세력(년·월·일·시주)은 [sajupy](https://github.com/0ssw1/sajupy) 라이브러리의 사전 계산된 CSV 만세력을 사용합니다.

- **진태양시 보정**: 출생지 도시명 기준 경도로 표준시(KST)와의 차이를 분 단위 보정
- **절기**: pyswisseph 태양 황경 이분법 탐색 (대운 시작 나이 계산에 사용)
- **대운**: 월주 기준 순행/역행 8주 계산, 시작 나이 = 출생일~가장 가까운 절기 일수 ÷ 3 반올림

검증 케이스:
```bash
uv run python scripts/verify_calculator.py
uv run --extra dev python -m pytest tests/test_calculator.py -v
```

## 오픈소스 라이센스

이 프로젝트는 다음 오픈소스 라이브러리를 사용합니다.

| 라이브러리 | 라이센스 | 저작권 |
|---|---|---|
| [sajupy](https://github.com/0ssw1/sajupy) | MIT | Copyright (c) 2025 0ssw1 |

MIT License 전문은 [sajupy 저장소](https://github.com/0ssw1/sajupy/blob/main/LICENSE)에서 확인할 수 있습니다.
