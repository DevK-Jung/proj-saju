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


class SajuRequest(BaseModel):
    birth_date:    str = Field(..., example="1995-03-15")
    birth_time:    str = Field(..., example="14:30")
    gender:        str = Field(..., example="M", description="M (남성) / F (여성)")
    calendar_type: str = Field(..., example="solar", description="solar (양력) / lunar (음력)")


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
    name:         str = Field(..., example="홍길동")
    relationship: str = Field("", example="솔로", description="솔로 / 연애중 / 기혼 / 빈칸")
    question:     str = Field("", example="올해 이직해도 될까요?", description="선택 사항")


class ChatRequest(BaseModel):
    """채팅 요청 (기존 세션 thread_id 필요)"""
    thread_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    message:   str = Field(..., example="올해 연애운이 어떤가요?")
