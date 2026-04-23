"""사주 AI LangGraph — PostgreSQL 체크포인트 기반

라우팅 로직:
  - saju_data is None → 분석 단계 (calculate → ohaeng → yearly → monthly → [question])
  - saju_data exists  → 채팅 단계 (chat)
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from .state import SajuState
from .nodes import (
    calculate_node,
    ohaeng_node,
    yearly_node,
    monthly_node,
    question_node,
    chat_node,
)

# ── 라우팅 함수 ──────────────────────────────────────────────────────────────

def _route_start(state: SajuState) -> str:
    """saju_data 유무로 분석/채팅 경로 결정"""
    return "chat" if state.get("saju_data") else "calculate"


def _route_after_monthly(state: SajuState) -> str:
    """질문 유무로 question 노드 여부 결정"""
    return "question" if (state.get("question") or "").strip() else "__end__"


# ── 그래프 빌더 ───────────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    g = StateGraph(SajuState)

    g.add_node("calculate", calculate_node)
    g.add_node("ohaeng",    ohaeng_node)
    g.add_node("yearly",    yearly_node)
    g.add_node("monthly",   monthly_node)
    g.add_node("question",  question_node)
    g.add_node("chat",      chat_node)

    # 시작: 분석 vs 채팅
    g.add_conditional_edges(START, _route_start, {
        "calculate": "calculate",
        "chat":      "chat",
    })

    # 분석 파이프라인
    g.add_edge("calculate", "ohaeng")
    g.add_edge("ohaeng",    "yearly")
    g.add_edge("yearly",    "monthly")
    g.add_conditional_edges("monthly", _route_after_monthly, {
        "question":  "question",
        "__end__":   END,
    })
    g.add_edge("question", END)

    # 채팅
    g.add_edge("chat", END)

    return g


# ── 싱글턴 관리 ───────────────────────────────────────────────────────────────

_pool: AsyncConnectionPool | None = None
_saju_graph = None


def get_graph():
    if _saju_graph is None:
        raise RuntimeError("Graph not initialized. Call init_graph() first.")
    return _saju_graph


async def init_graph(psycopg_url: str) -> None:
    """서버 시작 시 1회 호출 — 체크포인터 + 컴파일된 그래프 생성"""
    global _pool, _saju_graph

    _pool = AsyncConnectionPool(
        conninfo=psycopg_url,
        max_size=10,
        open=False,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    )
    await _pool.open()

    checkpointer = AsyncPostgresSaver(_pool)
    await checkpointer.setup()  # checkpoint 테이블 자동 생성

    _saju_graph = _build_graph().compile(checkpointer=checkpointer)
    print("[Graph] LangGraph + PostgreSQL Checkpoint 초기화 완료")


async def close_graph() -> None:
    """서버 종료 시 호출"""
    global _pool
    if _pool:
        await _pool.close()
        print("[Graph] 체크포인트 커넥션 풀 종료")
