"""사주 AI Agent 노드 구현

각 화면에 대응하는 노드:
  calculate  → 사주팔자 계산 (만세력 화면)
  ohaeng     → 오행 분석 (오행 화면)
  yearly     → 올해 운세 (세운 화면)
  monthly    → 이번 달 운세 (월운 화면)
  question   → 질문 답변 (선택 — 질문이 있을 때만)
  chat       → 채팅 (체크포인트 복원 후)
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.engine.calculator import calculate_saju
from app.engine.models import SajuRequest
from app.rag.retriever import hybrid_search, simple_search
from app.core.database import get_db_session
from app.core.config import settings
from .state import SajuState
from .prompts import (
    build_ohaeng_prompt,
    build_yearly_prompt,
    build_monthly_prompt,
    build_question_prompt,
    build_chat_messages,
)

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.7,
            streaming=True,
            api_key=settings.OPENAI_API_KEY,
        )
    return _llm


# ── RAG 헬퍼 ─────────────────────────────────────────────────────────────────

async def _rag(query: str, elements: list[str], contexts: list[str], top_k: int = 4) -> str:
    """RAG 검색 결과를 문자열로 반환 (실패 시 빈 문자열)"""
    try:
        async with get_db_session() as db:
            results = await hybrid_search(
                db=db,
                query=query,
                elements=elements,
                context_types=contexts,
                top_k=top_k,
            )
        return "\n\n".join(f"[{r['category']}] {r['content']}" for r in results[:3])
    except Exception:
        return ""


async def _rag_simple(query: str, top_k: int = 4) -> str:
    try:
        async with get_db_session() as db:
            results = await simple_search(db=db, query=query, top_k=top_k)
        return "\n\n".join(f"[{r['category']}] {r['content']}" for r in results[:3])
    except Exception:
        return ""


# ── 노드 구현 ─────────────────────────────────────────────────────────────────

async def calculate_node(state: SajuState) -> dict:
    """사주팔자 계산 (만세력 화면 데이터 생산)"""
    req = SajuRequest(
        birth_date=state["birth_date"],
        birth_time=state.get("birth_time", "미상"),
        gender=state["gender"],
        calendar_type=state.get("calendar_type", "solar"),
    )
    saju_data = calculate_saju(req)
    return {"saju_data": saju_data.model_dump()}


async def ohaeng_node(state: SajuState) -> dict:
    """오행 분석 노드"""
    saju = state["saju_data"]
    name = state.get("name", "")

    gans = [saju[f"{p}_pillar"]["gan"] for p in ("year", "month", "day", "hour")]
    zhis = [saju[f"{p}_pillar"]["zhi"] for p in ("year", "month", "day", "hour")]
    rag_text = await _rag(
        query=f"{''.join(gans)} {''.join(zhis)} 오행 성격 기질",
        elements=gans + zhis,
        contexts=["오행", "음양오행", "성격"],
    )

    prompt = build_ohaeng_prompt(saju, name, rag_text)
    response = await get_llm().ainvoke(prompt)
    return {"ohaeng_analysis": response.content}


async def yearly_node(state: SajuState) -> dict:
    """올해 운세 노드"""
    saju = state["saju_data"]
    name = state.get("name", "")
    yf = saju.get("yearly_fortune", {})

    rag_text = await _rag(
        query=f"{yf.get('gan', '')} {yf.get('zhi', '')} 세운 운세 흐름",
        elements=[yf.get("gan", ""), yf.get("zhi", "")],
        contexts=["세운", "운세흐름", "재물", "직업"],
    )

    prompt = build_yearly_prompt(saju, name, rag_text)
    response = await get_llm().ainvoke(prompt)
    return {"yearly_fortune": response.content}


async def monthly_node(state: SajuState) -> dict:
    """이번 달 운세 노드"""
    saju = state["saju_data"]
    name = state.get("name", "")
    mf = saju.get("monthly_fortune", {})

    rag_text = await _rag(
        query=f"{mf.get('gan', '')} {mf.get('zhi', '')} 월운",
        elements=[mf.get("gan", ""), mf.get("zhi", "")],
        contexts=["월운", "운세흐름"],
    )

    prompt = build_monthly_prompt(saju, name, rag_text)
    response = await get_llm().ainvoke(prompt)
    return {"monthly_fortune": response.content}


async def question_node(state: SajuState) -> dict:
    """질문 답변 노드 (question이 있을 때만 실행)"""
    question = state.get("question", "").strip()
    if not question:
        return {"question_answer": ""}

    saju = state["saju_data"]
    name = state.get("name", "")

    rag_text = await _rag_simple(query=question)

    prompt = build_question_prompt(
        saju=saju,
        name=name,
        question=question,
        ohaeng_analysis=state.get("ohaeng_analysis") or "",
        yearly_fortune=state.get("yearly_fortune") or "",
        rag_text=rag_text,
    )
    response = await get_llm().ainvoke(prompt)
    return {"question_answer": response.content}


async def chat_node(state: SajuState) -> dict:
    """채팅 노드 — 체크포인트에서 복원된 전체 컨텍스트 활용"""
    saju = state.get("saju_data", {})
    name = state.get("name", "")
    messages = state.get("messages", [])

    # 마지막 사용자 메시지를 기반으로 RAG 검색
    last_user_msg = ""
    for msg in reversed(messages):
        role = getattr(msg, "type", "")
        if role == "human":
            last_user_msg = msg.content
            break

    rag_text = await _rag_simple(query=last_user_msg or "사주 운세") if last_user_msg else ""

    # 채팅 이력에서 마지막 AI 메시지 직전까지를 history로 사용
    # (마지막 HumanMessage는 이미 messages에 포함)
    prompt_messages = build_chat_messages(
        saju=saju,
        name=name,
        ohaeng_analysis=state.get("ohaeng_analysis") or "",
        yearly_fortune=state.get("yearly_fortune") or "",
        monthly_fortune=state.get("monthly_fortune") or "",
        question_answer=state.get("question_answer") or "",
        rag_text=rag_text,
        chat_history=messages,
    )

    response = await get_llm().ainvoke(prompt_messages)
    return {"messages": [AIMessage(content=response.content)]}
