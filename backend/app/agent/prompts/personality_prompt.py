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

인사말 없이 바로 시작하세요. 아래 순서대로 서술하세요.

1. 과다 오행({excess_str})이 만드는 기질
   - 이 오행이 강하기 때문에 생기는 구체적인 장점 2가지를 실생활 상황으로 예시하세요.
     예) "土(흙)가 과다한 사람은 한 번 신뢰를 쌓은 관계를 오래 유지하는 경향이 있어, 직장에서 팀워크가 필요한 장기 프로젝트에서 두각을 나타냅니다."
   - 동시에 이 오행이 과다해서 생기는 부작용·단점도 구체적인 상황으로 2가지 서술하세요.
     예) "반면 土가 지나치면 변화를 거부하고 현실에 안주하려 해, 이직 기회나 새로운 도전 앞에서 결정을 미루다 타이밍을 놓치는 일이 잦습니다."
   - 과다 오행이 없으면 이 항목은 생략하세요.

2. 부족 오행({lacking_str})이 만드는 취약점과 보완법
   - 이 오행이 부족해서 실제로 어떤 상황에서 어려움을 겪는지 구체적으로 서술하세요.
     예) "水(물)가 없는 사주는 감정을 유연하게 흘려보내지 못해, 작은 갈등도 오래 마음에 담아두다 인간관계가 경직되는 경향이 있습니다."
   - 이를 채우기 위한 실천법을 제시하고, 실천하면 어떤 방향으로 변화할 수 있는지 구체적으로 말하세요.
     예) "검정·남색 계열 소품을 가까이 두거나 물가 근처에서 산책하는 루틴을 만들면, 감정 기복이 줄고 대인관계에서 여유가 생길 수 있습니다."
   - 부족 오행이 없으면 이 항목은 생략하세요.

3. 이 사주에 잘 맞는 직업·역할
   - 과다·부족 오행을 고려해 구체적인 직군 2~3가지와 그 이유를 제시하세요.
     예) "土 과다·水 부족 사주는 장기적 신뢰가 중요한 기획직·프로젝트 매니저에 적합하지만, 빠른 판단이 필요한 트레이딩·언론 분야는 소진이 빠를 수 있습니다." """),
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
