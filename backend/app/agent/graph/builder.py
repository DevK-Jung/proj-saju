"""사주 AI LangGraph — PostgreSQL 체크포인트 기반

그래프 흐름:
  [로직] calculate → [AI] personality → [AI] yearly → [AI] monthly → [AI] timeline → [AI?] question → END
  [채팅]           → chat → END
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from ..state.saju_state import SajuState
from ..nodes.calculate_node import calculate_node
from ..nodes.personality_node import personality_node
from ..nodes.yearly_node import yearly_node
from ..nodes.monthly_node import monthly_node
from ..nodes.timeline_node import timeline_node
from ..nodes.question_node import question_node
from ..nodes.chat_node import chat_node
from ..router.routes import route_start, route_after_timeline

_pool: AsyncConnectionPool | None = None
_saju_graph = None


def _build_graph() -> StateGraph:
    g = StateGraph(SajuState)

    g.add_node("calculate",   calculate_node)
    g.add_node("personality", personality_node)
    g.add_node("yearly",      yearly_node)
    g.add_node("monthly",     monthly_node)
    g.add_node("timeline",    timeline_node)
    g.add_node("question",    question_node)
    g.add_node("chat",        chat_node)

    # 시작: 계산 / 기질분석 / 채팅
    g.add_conditional_edges(START, route_start, {
        "calculate":   "calculate",
        "personality": "personality",
        "chat":        "chat",
    })

    # 분석 파이프라인
    g.add_edge("calculate",   "personality")
    g.add_edge("personality", "yearly")
    g.add_edge("yearly",      "monthly")
    g.add_edge("monthly",     "timeline")
    g.add_conditional_edges("timeline", route_after_timeline, {
        "question":  "question",
        "__end__":   END,
    })
    g.add_edge("question", END)

    # 채팅
    g.add_edge("chat", END)

    return g


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
