"""질문 답변 노드 (question이 있을 때만 실행) — 무당 스타일"""

from langchain_core.output_parsers import StrOutputParser
from ..state.saju_state import SajuState
from ..prompts.question_prompt import QUESTION_TEMPLATE, build_question_input
from .base import get_llm, rag_simple


async def question_node(state: SajuState) -> dict:
    question = state.get("question", "").strip()
    if not question:
        return {"question_answer": ""}

    saju = state["saju_data"]
    name = state.get("name", "")

    rag_text = await rag_simple(query=question)

    chain = QUESTION_TEMPLATE | get_llm() | StrOutputParser()
    result = await chain.ainvoke(
        build_question_input(
            saju=saju,
            name=name,
            question=question,
            personality_analysis=state.get("personality_analysis") or "",
            yearly_fortune=state.get("yearly_fortune") or "",
            rag_text=rag_text,
        )
    )
    return {"question_answer": result}
