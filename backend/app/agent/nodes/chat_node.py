"""채팅 노드 — 체크포인트에서 복원된 전체 컨텍스트 활용"""

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from ..state.saju_state import SajuState
from ..prompts.chat_prompt import CHAT_TEMPLATE, build_chat_input
from .base import get_llm, rag_simple


async def chat_node(state: SajuState) -> dict:
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

    rag_text = await rag_simple(query=last_user_msg or "사주 운세") if last_user_msg else ""

    chain = CHAT_TEMPLATE | get_llm() | StrOutputParser()
    result = await chain.ainvoke(
        build_chat_input(
            saju=saju,
            name=name,
            personality_analysis=state.get("personality_analysis") or "",
            yearly_fortune=state.get("yearly_fortune") or "",
            monthly_fortune=state.get("monthly_fortune") or {},
            question_answer=state.get("question_answer") or "",
            rag_text=rag_text,
            chat_history=messages,
        )
    )
    return {"messages": [AIMessage(content=result)]}
