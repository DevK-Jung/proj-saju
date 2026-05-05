"""기질·성격 분석 프롬프트

오행 과다·부족 중심으로 장점/부작용/보완법을 구체적으로 서술.
"""

from langchain_core.prompts import ChatPromptTemplate
from .base import ORACLE_PERSONA, format_saju, format_ohaeng_detail

PERSONALITY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", ORACLE_PERSONA),
    ("human", """{name}님 사주 기질·성격 분석.

[사주팔자]
{saju_info}

[오행 구성]
{ohaeng_str}

[오행 균형 요약]
{balance_note}
- 과다 오행: {excess_str}
- 부족 오행: {lacking_str}

[참고 사주 지식]
{rag_text}

인사말·제목·번호 없이 아래 흐름대로 자연스럽게 이어지는 글로 쓰세요. 문단 사이에는 빈 줄 하나만 넣으세요.

첫 번째 문단 — 타고난 기질:
{name}님은 [과다 오행이 만드는 기질]을 타고나서, 주변 사람들이 ~다고 느낄 경향이 있습니다. [구체적인 장점 상황 1~2가지]를 잘 해내고, [또 다른 강점]으로 주변에서 인정받는 편입니다.

두 번째 문단 — 취약점과 그 원인:
그러나 [부족 오행]이 약한 탓에 [어떤 상황]에서 의욕이 갑자기 떨어지거나 체력이 빠르게 소진되는 일이 생깁니다. 특히 [구체적인 취약 상황]에서 이런 성향이 두드러집니다.

세 번째 문단 — 보완법:
그렇기에 [구체적인 행동 1]을 하고, [구체적인 행동 2]를 꾸준히 실천하면 이 부분을 채울 수 있습니다.

네 번째 문단 — 방향 전환:
이러한 성격은 [부족 오행]을 보완하면 [더 나은 구체적 모습]으로 방향을 바꿀 수 있으며, [잘 맞는 직업·역할 2가지]에서 특히 두각을 나타낼 수 있습니다. """),
])


def build_personality_input(saju: dict, name: str, rag_text: str) -> dict:
    excess_labels, lacking_labels, ohaeng_str, excess_str, lacking_str, balance_note = \
        format_ohaeng_detail(saju)

    return {
        "name":         name,
        "saju_info":    format_saju(saju),
        "ohaeng_str":   ohaeng_str,
        "balance_note": balance_note,
        "excess_str":   excess_str  if excess_labels  else "없음",
        "lacking_str":  lacking_str if lacking_labels else "없음",
        "rag_text":     rag_text or "(관련 사주 지식 없음)",
    }
