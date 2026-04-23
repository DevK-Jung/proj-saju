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
  "calendar_type": "solar"
}
```

**Response**
```json
{
  "data": {
    "year":  { "stem": "乙", "branch": "亥", "sipsung": "..." },
    "month": { "stem": "己", "branch": "卯", "sipsung": "..." },
    "day":   { "stem": "丙", "branch": "申", "sipsung": "..." },
    "hour":  { "stem": "壬", "branch": "午", "sipsung": "..." }
  }
}
```

### POST `/saju/analyze`

사주 계산 + RAG 검색 + LLM 해석.

**Request** — `/calculate`와 동일 + 추가 필드
```json
{
  "birth_date": "1995-03-15",
  "birth_time": "14:30",
  "gender": "M",
  "calendar_type": "solar",
  "question_type": "팔자",
  "question": "재물운이 궁금합니다"
}
```

**Response**
```json
{
  "saju_data": { ... },
  "answer": "..."
}
```

### POST `/saju/analyze/stream`

`/analyze`와 동일한 요청, SSE 스트리밍으로 응답.

```
data: 안녕하세요\n\n
data: 갑자일주는\n\n
data: [DONE]\n\n
```

## LangGraph Agent

```
START → calculate → rag → interpret → END
```

| 노드 | 역할 |
|------|------|
| `calculate` | ephem 기반 사주팔자 계산 |
| `rag` | pgvector 하이브리드 검색 (벡터 유사도 + 오행 필터) |
| `interpret` | OpenAI GPT로 최종 해석 생성 |

RAG 노드는 DB 미연결 시 graceful fallback (빈 컨텍스트로 LLM 해석 진행).

## 계산 엔진

`ephem` 라이브러리로 태양 황경을 계산해 절기를 산출합니다.

- 절기: 태양 황경 이분법 탐색 (`_find_solar_term_jd`)
- 일진: Julian Day Number 공식 `(JDN + 40) % 60`

검증 케이스:
```bash
uv run python scripts/verify_calculator.py
```
