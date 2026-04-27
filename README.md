# 설아 — AI 사주 오라클

> 오라클 캐릭터 **설아**가 당신의 사주팔자를 읽고, 운명의 흐름을 이야기합니다.


## 🎬 앱 미리보기

<img src="./app_demo.gif" width="400"/>

---

## 화면 구성 (9-Screen)

| # | 화면 | 설명 |
|---|------|------|
| 1 | 웰컴 | 설아 등장 + 타이핑 인사 |
| 2 | 정보 입력 | 이름·성별·생년월일·시간·음력·관계·질문(선택) |
| 3 | 로딩 | 오브 스피너 + 회전 메시지 |
| 4 | 오행 | 5원소 원형 시각화 + 균형 바 |
| 5 | 만세력 | 사주팔자 4기둥 그리드 + 대운 테이블 |
| 6 | 연운 | 5개 카테고리 점수 |
| 7 | 월운 | 카드 + 키워드 태그 |
| 8 | 질문 답변 | 타이핑 효과 답변 (질문 입력 시만) |
| 9 | 채팅 | 대화형 스트리밍 채팅 |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | FastAPI · LangGraph · pyswisseph · psycopg3 (Python 3.11, uv) |
| AI | OpenAI GPT-4o · KURE-v1 로컬 임베딩 |
| DB | PostgreSQL + pgvector + LangGraph Checkpoint |
| Frontend | React · TypeScript · Zustand · Tailwind CSS (Vite) |
| Infra | Docker Compose |

---

## 아키텍처

```
React (9 Screens)
  │  POST /saju/session  → SSE stream
  │  POST /saju/chat     → SSE token stream
  ▼
FastAPI
  ▼
LangGraph (PostgreSQL Checkpoint)
  ├── route ──────────────────────────────────┐
  │   ├── [saju_data 없음] calculate          │
  │   │       → ohaeng → yearly → monthly     │
  │   │         → [question] → END            │
  │   └── [saju_data 있음] chat → END         │
  └────────────────────────────────────────────┘

RAG: hybrid_search (pgvector HNSW + BM25)
     일주·천간·지지·오행 지식 청크
```

---

## 디렉토리 구조

```
saju-app/
├── backend/
│   ├── app/
│   │   ├── engine/       # 사주 계산 엔진 (pyswisseph 절기, JDN 일주)
│   │   │   ├── calculator.py
│   │   │   ├── solar_terms.py
│   │   │   └── constants.py
│   │   ├── rag/          # 임베딩 · 하이브리드 검색
│   │   ├── agent/        # LangGraph 그래프 · 노드 · 프롬프트 · 상태
│   │   │   ├── graph.py
│   │   │   ├── nodes.py
│   │   │   ├── prompts.py
│   │   │   └── state.py
│   │   └── api/          # FastAPI 엔드포인트
│   ├── scripts/
│   │   ├── setup_data.py        # 데이터 적재 파이프라인
│   │   ├── scrape.py            # 일주·천간·지지·오행 지식 수집
│   │   └── verify_calculator.py # 계산 엔진 검증
│   ├── data/
│   │   ├── chunks/       # RAG용 JSON 청크 (일주·천간·지지·오행)
│   │   └── raw/
│   └── alembic/          # DB 마이그레이션
├── frontend/
│   └── src/
│       ├── App.tsx        # 9-Screen 전체 UI
│       ├── store/
│       │   └── useSajuStore.ts  # Zustand + SSE 파싱
│       └── index.css      # 디자인 토큰 · 애니메이션
├── docker-compose.yml
└── README.md
```

---

## 실행 방법

### 사전 요구사항

- Docker Desktop
- Python 3.11+, [uv](https://github.com/astral-sh/uv)
- Node.js 18+
- OpenAI API Key

### 1. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
# OPENAI_API_KEY, DATABASE_URL 입력
```

### 2. DB 시작

```bash
docker compose up -d
```

### 3. 데이터 적재

```bash
cd backend
uv run python scripts/setup_data.py
```

> `--skip-scrape` : 스크래핑 건너뜀 (이미 완료된 경우)  
> `--skip-migrate` : 마이그레이션 건너뜀  
> `--only-ingest` : 적재만 실행

### 4. 백엔드 서버

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### 5. 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

→ `http://localhost:5173` 에서 확인

---

## API

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/saju/calculate` | 사주팔자 계산 (JSON) |
| POST | `/api/v1/saju/session` | 전체 분석 세션 (SSE 스트림) |
| POST | `/api/v1/saju/chat` | 채팅 메시지 (SSE 토큰 스트림) |

### SSE 이벤트 순서 (`/session`)

```
event: saju_data    → 만세력 JSON
event: ohaeng       → 오행 분석 텍스트
event: yearly       → 연운 분석 텍스트
event: monthly      → 월운 분석 텍스트
event: answer       → 질문 답변 텍스트 (질문 있을 때만)
event: done         → 완료 신호
```

---

## 사주 계산 엔진

`pyswisseph`(Swiss Ephemeris) 기반 고정밀 절기 계산 + JDN 기반 일진.

- **절기 계산**: `swe.calc_ut()` Moshier 내장 에페메리스 → 이분법 50회 수렴
- **일진 계산**: `(JDN − 2,445,733) % 60` — 기준일 1984-02-02 = 甲子日
- **야자시**: 23:xx → 다음날 子時 기준

검증된 기준 케이스:

| 생년월일 | 년주 | 월주 | 일주 |
|----------|------|------|------|
| 1984-02-02 12:00 | 甲子 | 甲寅 | 甲子 |
| 1990-02-04 14:00 | 庚午 | 甲寅 | — |
| 1995-03-15 | 乙亥 | 己卯 | 丙申 |
