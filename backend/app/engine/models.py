from pydantic import BaseModel, Field
from typing import Optional


class Pillar(BaseModel):
    gan: str
    zhi: str
    gan_kr: str
    zhi_kr: str
    gan_wuxing: str
    zhi_wuxing: str
    sipsung: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "gan": "丙",
                "zhi": "申",
                "gan_kr": "병",
                "zhi_kr": "신",
                "gan_wuxing": "火",
                "zhi_wuxing": "金",
                "sipsung": "비견",
            }
        }
    }


class OhaengScores(BaseModel):
    """오행 점수 — 천간 1점·지지(지장간 가중) 합산.
    지장간 반영으로 소수점이 생길 수 있음 (예: 木=2.5).
    """
    wood:  float  # 木
    fire:  float  # 火
    earth: float  # 土
    metal: float  # 金
    water: float  # 水


class SajuData(BaseModel):
    year_pillar:     Pillar
    month_pillar:    Pillar
    day_pillar:      Pillar
    hour_pillar:     Pillar
    day_gan:         str
    day_gan_wuxing:  str
    yearly_fortune:  Pillar
    monthly_fortune: Pillar
    daeun:           list[Pillar]
    daeun_start_age: int
    ohaeng_scores:   OhaengScores   # 오행 점수 (AI 없는 순수 계산)


class SajuRequest(BaseModel):
    birth_date:    str = Field(..., example="1995-03-15")
    birth_time:    str = Field(..., example="14:30")
    gender:        str = Field(..., example="M", description="M (남성) / F (여성)")
    calendar_type: str = Field(..., example="solar", description="solar (양력) / lunar (음력)")
    city:          str = Field("Seoul", example="Incheon", description="출생지 도시명 (진태양시 보정에 사용)")


class SajuAnalysisRequest(SajuRequest):
    question_type: str = Field(
        ...,
        example="팔자",
        description="팔자 / 세운 / 월운 / 특정운 / 자유질문",
    )
    question: Optional[str] = Field(None, example="재물운이 어떻게 될까요?")


# ── 새 프론트엔드 화면 대응 모델 ───────────────────────────────────────────────

class FullAnalysisRequest(BaseModel):
    """9화면 사주 앱용 전체 분석 요청"""
    birth_date:    str = Field(..., example="1995-03-15")
    birth_time:    str = Field("미상", example="14:30", description="HH:MM 또는 '미상'")
    gender:        str = Field(..., example="M", description="M / F")
    calendar_type: str = Field("solar", example="solar", description="solar / lunar")
    city:          str = Field("Seoul", example="Seoul", description="출생지 도시명 (진태양시 보정에 사용)")
    name:         str = Field(..., example="홍길동")
    relationship: str = Field("", example="솔로", description="솔로 / 연애중 / 기혼 / 빈칸")
    question:     str = Field("", example="올해 이직해도 될까요?", description="선택 사항")


class AnalyzeRequest(BaseModel):
    """사전 계산된 사주 데이터 기반 AI 분석 요청 (2단계 — 만세력·오행 확인 후 호출)"""
    saju_data:     dict = Field(..., description="/calculate 결과 SajuData dict")
    name:          str  = Field(..., example="홍길동")
    gender:        str  = Field("M", example="M", description="M / F")
    birth_date:    str  = Field("", example="1995-03-15")
    birth_time:    str  = Field("미상", example="14:30")
    calendar_type: str  = Field("solar", example="solar")
    relationship:  str  = Field("", example="솔로")
    question:      str  = Field("", example="올해 이직해도 될까요?")


class ChatRequest(BaseModel):
    """채팅 요청 (기존 세션 thread_id 필요)"""
    thread_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    message:   str = Field(..., example="올해 연애운이 어떤가요?")
