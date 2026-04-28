"""오행 분석 프롬프트"""

from datetime import date
from langchain_core.prompts import ChatPromptTemplate
from .base import ORACLE_PERSONA, format_saju

OHAENG_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", ORACLE_PERSONA),
    ("human", """{name}님({year}년 기준)의 사주를 오행(五行) 관점에서 분석해주세요.

[사주팔자]
{saju_info}

[오행 구성]
{ohaeng_str}

[참고 사주 지식]
{rag_text}

오행 균형과 {name}님의 기질·성향·강점·주의점을 3~4문장으로 설명해주세요."""),
])


def build_ohaeng_input(saju: dict, name: str, rag_text: str) -> dict:
    today = date.today()
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pk in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        p = saju.get(pk, {})
        for wx_key in ("gan_wuxing", "zhi_wuxing"):
            wx = p.get(wx_key, "")
            if wx in counts:
                counts[wx] += 1
    total = sum(counts.values()) or 8
    ohaeng_str = " / ".join(
        f"{k}({round(v / total * 100)}%)"
        for k, v in counts.items()
    )

    return {
        "name": name,
        "year": today.year,
        "saju_info": format_saju(saju),
        "ohaeng_str": ohaeng_str,
        "rag_text": rag_text or "(관련 사주 지식 없음)",
    }
