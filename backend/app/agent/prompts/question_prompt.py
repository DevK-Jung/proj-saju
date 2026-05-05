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

인사말·번호·소제목 없이 3~4문장으로 짧게 답하세요.

1. 질문의 핵심 결론을 첫 문장에 바로 말하세요. (예: "된다" / "지금은 아니다" / "○월이 적기다")
2. 그 근거를 사주에서 1~2가지만 뽑아 간결하게 설명하세요.
3. 필요하면 딱 한 가지 행동 지침만 덧붙이세요.

군더더기·반복·장황한 설명 금지. 짧고 명확하게."""),
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
