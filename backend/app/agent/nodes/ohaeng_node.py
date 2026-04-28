"""오행 분석 노드 (현재 메인 그래프에서 미사용)"""

from langchain_core.output_parsers import StrOutputParser
from ..state.saju_state import SajuState
from ..prompts.ohaeng_prompt import OHAENG_TEMPLATE, build_ohaeng_input
from .base import get_llm, rag


async def ohaeng_node(state: SajuState) -> dict:
    saju = state["saju_data"]
    name = state.get("name", "")

    gans = [saju[f"{p}_pillar"]["gan"] for p in ("year", "month", "day", "hour")]
    zhis = [saju[f"{p}_pillar"]["zhi"] for p in ("year", "month", "day", "hour")]

    rag_text = await rag(
        query=f"{''.join(gans)} {''.join(zhis)} 오행 성격 기질",
        elements=gans + zhis,
        contexts=["오행", "음양오행", "성격"],
    )

    chain = OHAENG_TEMPLATE | get_llm() | StrOutputParser()
    result = await chain.ainvoke(build_ohaeng_input(saju, name, rag_text))
    return {"ohaeng_analysis": result}
