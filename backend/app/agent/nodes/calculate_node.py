"""사주팔자 계산 노드 (만세력 화면 데이터 생산, LLM 불필요)"""

from app.engine.calculator import calculate_saju
from app.engine.models import SajuRequest
from ..state.saju_state import SajuState


async def calculate_node(state: SajuState) -> dict:
    req = SajuRequest(
        birth_date=state["birth_date"],
        birth_time=state.get("birth_time", "미상"),
        gender=state["gender"],
        calendar_type=state.get("calendar_type", "solar"),
        city=state.get("city", "Seoul"),
    )
    saju_data = calculate_saju(req)
    return {"saju_data": saju_data.model_dump()}
