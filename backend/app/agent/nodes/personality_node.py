"""기질·성격 분석 노드 — 사주 계산 후 첫 번째 AI 단계"""

from langchain_core.output_parsers import StrOutputParser
from ..state.saju_state import SajuState
from ..prompts.personality_prompt import PERSONALITY_TEMPLATE, build_personality_input
from .base import get_llm, rag


async def personality_node(state: SajuState) -> dict:
    saju = state["saju_data"]
    name = state.get("name", "")

    # 일간과 오행 기반 RAG 검색
    day_gan = saju.get("day_gan", "")
    rag_text = await rag(
        query=f"{day_gan} 일간 타고난 기질 성격 장단점",
        elements=[day_gan],
        contexts=["기질", "성격", "오행", "일간"],
    )

    chain = PERSONALITY_TEMPLATE | get_llm() | StrOutputParser()
    result = await chain.ainvoke(build_personality_input(saju, name, rag_text))
    return {"personality_analysis": result}
