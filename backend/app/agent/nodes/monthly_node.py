"""이번 달 운세 노드 — 5개 카테고리 병렬 실행"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from ..state.saju_state import SajuState
from ..prompts.monthly_prompt import (
    MONTHLY_GENERAL_TEMPLATE,
    MONTHLY_LOVE_TEMPLATE,
    MONTHLY_WEALTH_TEMPLATE,
    MONTHLY_CAREER_TEMPLATE,
    MONTHLY_BUSINESS_TEMPLATE,
    build_monthly_input,
)
from .base import get_llm, rag


async def monthly_node(state: SajuState) -> dict:
    saju = state["saju_data"]
    name = state.get("name", "")
    mf = saju.get("monthly_fortune", {})

    rag_text = await rag(
        query=f"{mf.get('gan', '')} {mf.get('zhi', '')} 월운",
        elements=[mf.get("gan", ""), mf.get("zhi", "")],
        contexts=["월운", "운세흐름"],
    )

    llm = get_llm()
    parser = StrOutputParser()
    monthly_input = build_monthly_input(
        saju=saju,
        name=name,
        yearly_fortune=state.get("yearly_fortune") or "",
        rag_text=rag_text,
        relationship=state.get("relationship") or "",
    )

    # 5개 카테고리 동시 실행
    parallel = RunnableParallel(
        총운=MONTHLY_GENERAL_TEMPLATE  | llm | parser,
        연애운=MONTHLY_LOVE_TEMPLATE   | llm | parser,
        재물운=MONTHLY_WEALTH_TEMPLATE  | llm | parser,
        직업운=MONTHLY_CAREER_TEMPLATE  | llm | parser,
        사업운=MONTHLY_BUSINESS_TEMPLATE | llm | parser,
    )

    result: dict = await parallel.ainvoke(monthly_input)
    return {"monthly_fortune": result}
