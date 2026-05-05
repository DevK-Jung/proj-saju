"""채팅 프롬프트 (MessagesPlaceholder 사용)"""

from datetime import date
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .base import ORACLE_CHAT_PERSONA, format_saju

CHAT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "{system_content}"),
    MessagesPlaceholder(variable_name="history"),
])


def _format_monthly(monthly_fortune) -> str:
    """monthly_fortune이 dict(5개 카테고리)면 포맷, str이면 그대로 반환"""
    if not monthly_fortune:
        return ""
    if isinstance(monthly_fortune, dict):
        parts = []
        for key in ["총운", "연애운", "재물운", "직업운", "사업운"]:
            val = monthly_fortune.get(key, "")
            if val:
                parts.append(f"[{key}] {val}")
        return "\n".join(parts)
    return str(monthly_fortune)


def build_chat_input(
    saju: dict,
    name: str,
    personality_analysis: str,
    yearly_fortune: str,
    monthly_fortune,
    question_answer: str,
    rag_text: str,
    chat_history: list,
) -> dict:
    """채팅 노드 LCEL 체인 입력값 딕셔너리 생성"""
    today = date.today()
    answer_section = f"\n[질문 답변]\n{question_answer}" if question_answer else ""

    # 기질·운세는 핵심 요약만 (전문을 반복하면 LLM이 매번 비슷한 말을 시작함)
    personality_summary = (personality_analysis or "")[:200].rstrip() + ("..." if len(personality_analysis or "") > 200 else "")
    yearly_summary = (yearly_fortune or "")[:150].rstrip() + ("..." if len(yearly_fortune or "") > 150 else "")

    system_content = (
        f"{ORACLE_CHAT_PERSONA}\n\n"
        f"[{name}님 사주 — {today.year}년]\n"
        f"{format_saju(saju)}\n\n"
        f"기질 요약: {personality_summary}\n"
        f"올해 운세 요약: {yearly_summary}\n"
        f"이번 달 운세: {_format_monthly(monthly_fortune)}"
        f"{answer_section}\n\n"
        f"[참고 사주 지식]\n{rag_text or '(없음)'}"
    )

    return {
        "system_content": system_content,
        "history": chat_history,
    }
