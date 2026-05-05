"""LangGraph 라우팅 함수"""

from ..state.saju_state import SajuState


def route_start(state: SajuState) -> str:
    """라우팅:
    - saju_data 없음              → calculate (처음부터 계산)
    - saju_data 있음 + 메시지 있음 → chat
    - saju_data 있음 + 메시지 없음 → personality (AI 기질 분석부터 시작)
    """
    if not state.get("saju_data"):
        return "calculate"
    if state.get("messages"):
        return "chat"
    return "personality"


def route_after_timeline(state: SajuState) -> str:
    """질문 유무로 question 노드 여부 결정"""
    return "question" if (state.get("question") or "").strip() else "__end__"
