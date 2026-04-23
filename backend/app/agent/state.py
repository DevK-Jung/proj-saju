"""사주 AI Agent 상태 정의

saju_data 유무로 분석/채팅 단계를 구분:
  - saju_data is None  → 최초 분석 단계 (calculate → ohaeng → yearly → monthly → [question])
  - saju_data exists   → 채팅 단계 (chat node, 체크포인트에서 컨텍스트 복원)
"""

from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class SajuState(TypedDict, total=False):
    # ── 입력 (최초 세션 생성 시 설정) ─────────────────────────
    birth_date:    str
    birth_time:    str          # "HH:MM" 또는 "미상"
    gender:        str          # "M" | "F"
    calendar_type: str          # "solar" | "lunar"

    name:         str
    relationship: str           # "솔로" | "연애중" | "기혼" | ""
    question:     str           # 사용자 질문 (선택)

    # ── 계산/분석 결과 (체크포인트에 영속) ───────────────────
    saju_data:        Optional[dict]   # SajuData.model_dump()
    ohaeng_analysis:  Optional[str]
    yearly_fortune:   Optional[str]
    monthly_fortune:  Optional[str]
    question_answer:  Optional[str]    # question이 없으면 빈 문자열

    # ── 채팅 이력 (add_messages로 누적) ──────────────────────
    messages: Annotated[list, add_messages]
