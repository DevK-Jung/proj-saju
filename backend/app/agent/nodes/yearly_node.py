"""올해 운세 노드"""

from langchain_core.output_parsers import StrOutputParser
from ..state.saju_state import SajuState
from ..prompts.yearly_prompt import YEARLY_TEMPLATE, build_yearly_input
from .base import get_llm, rag


async def yearly_node(state: SajuState) -> dict:
    saju = state["saju_data"]
    name = state.get("name", "")
    yf = saju.get("yearly_fortune", {})

    rag_text = await rag(
        query=f"{yf.get('gan', '')} {yf.get('zhi', '')} 세운 운세 흐름",
        elements=[yf.get("gan", ""), yf.get("zhi", "")],
        contexts=["세운", "운세흐름", "재물", "직업"],
    )

    chain = YEARLY_TEMPLATE | get_llm() | StrOutputParser()
    result = await chain.ainvoke(
        build_yearly_input(
            saju=saju,
            name=name,
            personality_analysis=state.get("personality_analysis") or "",
            rag_text=rag_text,
        )
    )
    return {"yearly_fortune": result}
