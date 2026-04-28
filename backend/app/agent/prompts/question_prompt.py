"""질문 답변 프롬프트 — 무당 스타일 (확신, 시기 구체적)"""

from langchain_core.prompts import ChatPromptTemplate
from .base import ORACLE_PERSONA_ASSERTIVE, format_saju

QUESTION_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", ORACLE_PERSONA_ASSERTIVE),
    ("human", """{name}님 질문: "{question}"

[사주팔자]
{saju_info}

[타고난 기질]
{personality_analysis}

[올해 운세]
{yearly_fortune}

[참고 사주 지식]
{rag_text}

인사말 없이 바로 답하세요. 아래 3가지로 구성하세요.

1. 사주 기운으로 본 핵심 답변
   - 이전 상황과 지금 기운의 변화를 대비해서 설명하세요. ("이전까지는 ~였지만, 지금은 ~입니다.")
   - 시기를 묻는 질문이라면 반드시 "○월경", "올해 하반기", "내년 봄" 등 구체적 시기를 제시하세요.
   - 긍정적 가능성뿐 아니라 이 선택이 가져올 리스크도 명확히 말하세요.

2. 원하는 결과를 위해 반드시 해야 할 행동
   - 막연한 조언이 아닌 구체적인 행동(예: "○월 전에 포트폴리오를 준비하세요", "지인 중 ○○분야 사람에게 먼저 연락하세요")을 제시하세요.

3. 반드시 피해야 할 것
   - 이 시기에 특히 위험한 선택이나 행동 패턴(예: "성급한 계약 서명", "특정 유형의 사람과 동업")을 구체적으로 경고하세요."""),
])


def build_question_input(
    saju: dict,
    name: str,
    question: str,
    personality_analysis: str,
    yearly_fortune: str,
    rag_text: str,
) -> dict:
    return {
        "name":                 name,
        "saju_info":            format_saju(saju),
        "personality_analysis": personality_analysis or "",
        "yearly_fortune":       yearly_fortune or "",
        "rag_text":             rag_text or "(관련 사주 지식 없음)",
        "question":             question,
    }
