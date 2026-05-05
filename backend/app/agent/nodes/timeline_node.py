"""월운 타임라인 노드 — 이번 달 + 향후 3개월"""

import asyncio
from datetime import date
from pydantic import BaseModel
from sajupy import calculate_saju as sajupy_calc

from app.engine.constants import WUXING_TIANGAN, WUXING_DIZHI
from ..state.saju_state import SajuState
from ..prompts.timeline_prompt import TIMELINE_TEMPLATE, build_timeline_input
from .base import get_structured_llm


class MonthFortune(BaseModel):
    summary: str           # 이달 총운 한 문장
    highlight: str         # 연애운 | 재물운 | 직업운 | 사업운
    highlight_content: str # 해당 운 구체적 설명 2문장


def _get_upcoming_months(n: int = 4) -> list[tuple[int, int]]:
    """이번 달 포함 n개월 (year, month) 리스트"""
    today = date.today()
    y, m = today.year, today.month
    months = []
    for _ in range(n):
        months.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return months


async def _calc_month_fortune(
    saju: dict,
    name: str,
    yearly_fortune: str,
    year: int,
    month: int,
) -> dict:
    # 해당 월 월운 간지 계산 (15일 기준)
    raw = sajupy_calc(year, month, 15, 12, 0)
    gan = raw["month_stem"]
    zhi = raw["month_branch"]
    month_pillar = gan + zhi
    month_wuxing = WUXING_TIANGAN[gan] + WUXING_DIZHI[zhi]

    structured_llm = TIMELINE_TEMPLATE | get_structured_llm().with_structured_output(MonthFortune)
    result: MonthFortune = await structured_llm.ainvoke(
        build_timeline_input(
            saju=saju,
            name=name,
            yearly_fortune=yearly_fortune,
            year=year,
            month=month,
            month_pillar=month_pillar,
            month_wuxing=month_wuxing,
        )
    )

    return {
        "year":              year,
        "month":             month,
        "month_label":       f"{month}월",
        "month_pillar":      month_pillar,
        "summary":           result.summary,
        "highlight":         result.highlight,
        "highlight_content": result.highlight_content,
    }


async def timeline_node(state: SajuState) -> dict:
    saju          = state["saju_data"]
    name          = state.get("name", "")
    yearly        = state.get("yearly_fortune") or ""

    months = _get_upcoming_months(4)
    results = await asyncio.gather(*[
        _calc_month_fortune(saju, name, yearly, y, m)
        for y, m in months
    ])

    return {"timeline_fortune": list(results)}