"""월운 타임라인 프롬프트 — 이번 달 + 향후 3개월"""

from langchain_core.prompts import ChatPromptTemplate
from .base import ORACLE_PERSONA_ASSERTIVE, format_saju


TIMELINE_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", ORACLE_PERSONA_ASSERTIVE),
    ("human", """{name}님의 {year}년 {month}월 운세.

[사주팔자]
{saju_info}

[{month}월 월운 간지: {month_pillar} ({month_wuxing})]

[올해 운세 흐름]
{yearly_fortune}

이달 운세를 분석해주세요.
- summary: 이달 전체 흐름을 한 문장으로 (구체적으로, 30자 이내)
- highlight: 이달 가장 중요한 운 하나 (연애운, 재물운, 직업운, 사업운 중 택1)
- highlight_content: 해당 운에 대한 구체적인 설명 (2문장)

금지 표현: "OO월에는", "OO의 기운이 넘쳐/강해", 오행 이름 직접 나열, 간지 본문 언급"""),
])


def build_timeline_input(
    saju: dict,
    name: str,
    yearly_fortune: str,
    year: int,
    month: int,
    month_pillar: str,
    month_wuxing: str,
) -> dict:
    return {
        "name":           name,
        "year":           year,
        "month":          month,
        "saju_info":      format_saju(saju),
        "yearly_fortune": yearly_fortune or "",
        "month_pillar":   month_pillar,
        "month_wuxing":   month_wuxing,
    }