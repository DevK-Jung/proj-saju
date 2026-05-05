"""이번 달 운세 프롬프트 — 5개 카테고리 병렬 실행용

총운 / 연애운 / 재물운 / 직업운 / 사업운 각각 개별 ChatPromptTemplate.
monthly_node 에서 RunnableParallel 로 동시 실행.
"""

from datetime import date
from langchain_core.prompts import ChatPromptTemplate
from .base import ORACLE_PERSONA, format_saju


def _monthly_template(fortune_type: str, instruction: str) -> ChatPromptTemplate:
    """카테고리별 월운 템플릿 팩토리"""
    return ChatPromptTemplate.from_messages([
        ("system", ORACLE_PERSONA),
        ("human", f"""{{name}}님 {{year}}년 {{month}}월 {fortune_type}.

[사주팔자]
{{saju_info}}

[연애 상태]
{{relationship}}

[올해 신년운세 흐름]
{{yearly_fortune}}

[{{month}}월 월운 간지: {{monthly_gan}}{{monthly_zhi}} ({{monthly_wuxing}})]

[참고 사주 지식]
{{rag_text}}

금지 표현 (절대 사용 금지):
- "OO월에는", "이번 달에는" 등 월·시기로 문장을 시작하는 것
- "OO의 기운이 넘쳐", "OO 기운이 강해" 등 오행 기운 묘사 문장
- 오행(수·목·화·토·금) 이름을 직접 나열하는 것
- 간지(갑자·을축 등)를 본문에 직접 언급하는 것

{instruction}"""),
    ])


MONTHLY_GENERAL_TEMPLATE = _monthly_template(
    "총운",
    """이번 달 전체 기운을 3~4문장으로 서술하세요.
- 이달의 지배적인 기운이 지난달과 어떻게 달라지는지 대비해서 설명하세요.
- 이달 중 특히 조심해야 할 시기(상순·중순·하순)와 그 이유를 구체적으로 말하세요.
- 이달을 잘 보내기 위한 행동 지침 1가지를 명확하게 제시하세요.""",
)

MONTHLY_LOVE_TEMPLATE = _monthly_template(
    "연애운",
    """[연애 상태]에 명시된 현재 상황에 맞게 3~4문장으로 서술하세요.
- 솔로인 경우: 이달 인연이 생길 가능성이 높은 장소·상황(예: 지인 소개, 직장 내, 취미 모임)과 만날 가능성이 높은 이성의 구체적인 성격·분위기를 서술하세요. 인연이 생기기 어려운 시기나 주의해야 할 감정 패턴도 함께 언급하세요.
- 연애 중인 경우: 이달 관계에서 갈등이 생길 수 있는 구체적인 상황(예: 미래 계획 충돌, 연락 빈도 문제)과 관계가 깊어질 수 있는 계기를 함께 말하세요. 이달 넘기기 어려운 감정적 고비도 짚어주세요.
- 기혼인 경우: 배우자와의 관계 흐름(예: 대화 단절, 공동 지출 갈등, 친밀감 회복 기회)을 구체적 상황으로 서술하고, 이달 부부 관계에서 특히 조심해야 할 행동을 명시하세요.""",
)

MONTHLY_WEALTH_TEMPLATE = _monthly_template(
    "재물운",
    """3~4문장으로 서술하세요.
- 수입이 늘거나 줄어드는 구체적인 경로(예: 급여 외 부수입, 투자 수익, 예상치 못한 지출)를 명시하세요.
- 이달 돈이 새는 패턴(예: 충동구매, 경조사 지출, 보증 위험)을 구체적으로 경고하세요.
- 투자·저축과 관련해 이달에 해도 되는 것과 피해야 할 것을 각각 1가지씩 제시하세요.""",
)

MONTHLY_CAREER_TEMPLATE = _monthly_template(
    "직업운",
    """3~4문장으로 서술하세요.
- 직장 내 분위기 변화(예: 상사와의 관계, 팀 갈등, 새 프로젝트 기회)를 구체적 상황으로 그려주세요.
- 이달 업무에서 빛을 발하는 영역(예: 발표·기획·대외 협력)과 오히려 실수가 잦아질 영역을 함께 말하세요.
- 취업·이직·시험을 앞뒀다면 이달의 타이밍이 유리한지 불리한지 명확히 말하세요.""",
)

MONTHLY_BUSINESS_TEMPLATE = _monthly_template(
    "사업운",
    """3~4문장으로 서술하세요.
- 이달 기회가 오는 업종·거래 유형(예: 온라인 판매, B2B 계약, 해외 파트너십)을 구체적으로 제시하세요.
- 계약·투자·동업에서 반드시 주의해야 할 리스크(예: 구두 계약, 선급금 요구, 새 파트너 신뢰 문제)를 경고하세요.
- 이달 사업 확장보다 내실을 다져야 하는지, 공격적으로 나가도 좋은지 방향을 명확히 말하세요.""",
)


def build_monthly_input(
    saju: dict,
    name: str,
    yearly_fortune: str,
    rag_text: str,
    relationship: str = "",
) -> dict:
    today = date.today()
    mf = saju.get("monthly_fortune", {})

    # 연애 상태 레이블 정규화
    rel_label = {
        "솔로":   "솔로 (현재 연애 중이 아님)",
        "연애중":  "연애 중",
        "기혼":   "기혼",
    }.get(relationship, "미입력")

    return {
        "name":           name,
        "year":           today.year,
        "month":          today.month,
        "saju_info":      format_saju(saju),
        "relationship":   rel_label,
        "yearly_fortune": yearly_fortune or "",
        "monthly_gan":    mf.get("gan", ""),
        "monthly_zhi":    mf.get("zhi", ""),
        "monthly_wuxing": f"{mf.get('gan_wuxing','')}{mf.get('zhi_wuxing','')}",
        "rag_text":       rag_text or "(관련 사주 지식 없음)",
    }
