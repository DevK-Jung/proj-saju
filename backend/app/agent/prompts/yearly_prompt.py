"""신년운세 프롬프트

총운 풀이, 올해 좋은 점, 주의가 필요한 점, 설아의 조언 구성.
"""

from datetime import date
from langchain_core.prompts import ChatPromptTemplate
from .base import ORACLE_PERSONA, format_saju

YEARLY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", ORACLE_PERSONA),
    ("human", """{name}님 {year}년 신년운세.

[사주팔자]
{saju_info}

[타고난 기질]
{personality_analysis}

[{year}년 세운: {yearly_gan}{yearly_zhi} ({yearly_wuxing})]

[참고 사주 지식]
{rag_text}

아래 4가지를 각각 2~3문장으로 서술하세요. 인사말 없이 바로 시작하세요.

금지 표현 (절대 사용 금지):
- "OOOO년에는", "올해는" 등 연도·시기로 문장을 시작하는 것
- "OO의 기운이 넘쳐", "OO 기운이 강해" 등 오행 기운 묘사 문장
- 오행(수·목·화·토·금) 이름을 직접 나열하는 것
- 간지(갑자·을축 등)를 본문에 직접 언급하는 것

1. 총운: 올해 전체 흐름을 지난해와 대비해서 설명하고, 상반기·하반기 중 어느 시기가 더 유리한지 명시하세요.
2. 기회의 영역: 올해 운이 집중되는 구체적인 분야(예: 커리어 전환, 재테크, 새 인간관계)와 그 이유를 서술하세요.
3. 주의할 상황: 올해 발생 가능한 부정적 시나리오(예: 건강 악화 시기, 금전 손실 패턴, 인간관계 갈등)를 구체적으로 경고하세요.
4. 핵심 조언: 올해를 잘 보내기 위해 반드시 해야 할 행동 1가지와 반드시 피해야 할 행동 1가지를 제시하세요."""),
])


def build_yearly_input(
    saju: dict,
    name: str,
    personality_analysis: str,
    rag_text: str,
) -> dict:
    today = date.today()
    yf = saju.get("yearly_fortune", {})
    return {
        "name":                 name,
        "year":                 today.year,
        "saju_info":            format_saju(saju),
        "personality_analysis": personality_analysis or "",
        "yearly_gan":           yf.get("gan", ""),
        "yearly_zhi":           yf.get("zhi", ""),
        "yearly_wuxing":        f"{yf.get('gan_wuxing','')}{yf.get('zhi_wuxing','')}",
        "rag_text":             rag_text or "(관련 사주 지식 없음)",
    }
