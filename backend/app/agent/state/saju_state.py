"""사주 AI Agent 상태 정의

그래프 흐름:
  [로직] calculate  → personality → yearly → monthly → [question] → END
  [채팅] saju_data + messages → chat → END
"""

from typing import Annotated, Optional, TypedDict
from langgraph.graph.message import add_messages


class SajuState(TypedDict, total=False):
    # ── 입력 ────────────────────────────────────────────────────────────────────
    birth_date:    str
    birth_time:    str           # "HH:MM" | "미상"
    gender:        str           # "M" | "F"
    calendar_type: str           # "solar" | "lunar"
    name:          str
    relationship:  str           # "솔로" | "연애중" | "기혼" | ""
    question:      str           # 선택

    # ── 계산·분석 결과 (체크포인트 영속) ────────────────────────────────────────
    saju_data:            Optional[dict]   # SajuData.model_dump()
    personality_analysis: Optional[str]   # 기질·성격·장단점·직업·부족오행 채우기
    yearly_fortune:       Optional[str]   # 신년운세 (총운/좋은점/주의점/조언)
    monthly_fortune:      Optional[dict]  # {"총운","연애운","재물운","직업운","사업운"}
    question_answer:      Optional[str]   # 질문 답변 (없으면 "")

    # ── 채팅 이력 ────────────────────────────────────────────────────────────────
    messages: Annotated[list, add_messages]
