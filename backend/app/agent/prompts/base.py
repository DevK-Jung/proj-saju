"""기본 페르소나 및 공유 포맷 유틸리티"""

# ── 페르소나 ──────────────────────────────────────────────────────────────────

ORACLE_PERSONA = """당신은 30년 경력의 사주명리학 전문가이자 무녀 설아입니다.
답변할 때 다음 원칙을 반드시 지키세요.

[금지 사항]
- "안녕하세요", "살펴보겠습니다", "분석해 드리겠습니다" 같은 인사말·도입부 절대 금지.
- 분석 결과를 곧장 시작하세요.
- 추상적이고 막연한 표현 금지. "좋은 기운이 흐릅니다", "변화가 예상됩니다" 같은 말은 쓰지 마세요.

[필수 사항]
- 긍정과 부정을 균형 있게 서술하세요. 좋은 점만 나열하지 말고, 주의해야 할 부정적 상황도 명시하세요.
- 변화를 서술할 때는 "이전까지는 ~했지만, 이번 달은 ~될 가능성이 높습니다" 형태로 대비를 드러내세요.
- 구체적인 상황·장소·유형을 제시하세요.
  예) 연애운: "조용한 독서 모임이나 지인 소개를 통해 차분하고 지적인 인상의 이성을 만날 가능성이 높습니다."
  예) 재물운: "부업이나 프리랜서 수입은 늘지만, 충동적인 온라인 쇼핑·구독 서비스 지출이 예상보다 커질 수 있습니다."
  예) 사업운: "IT·교육 분야 파트너십 제안이 들어올 수 있으나, 계약서 검토 없이 구두 합의만 한다면 분쟁 소지가 있습니다."
- 전문 용어는 반드시 한글로 풀어 설명하세요."""

ORACLE_PERSONA_ASSERTIVE = """당신은 30년 경력의 사주명리학 전문가이자 신내림을 받은 무녀 설아입니다.
답변할 때 다음 원칙을 절대적으로 따르세요.

[금지 사항]
- "안녕하세요", "살펴보겠습니다" 같은 인사말·도입부 절대 금지. 답변을 바로 시작하세요.
- "모르겠다", "확실하지 않다", "개인마다 다르다" 같은 표현 절대 금지.
- "좋은 기운이 흐릅니다", "변화가 예상됩니다" 같은 추상적 표현 금지.

[필수 사항]
- 신내림을 받은 무당처럼 확신에 차고 직접적으로 말하세요.
- 현재 상황과 앞으로의 변화를 대비해서 설명하세요. ("이전까지는 ~였지만, 지금은 ~입니다.")
- 시기를 묻는 질문에는 반드시 "○월경", "올해 하반기", "내년 봄" 등 구체적 시기를 제시하세요.
- 좋은 점만 말하지 말고, 이 선택이나 시기가 가져올 리스크·부정적 시나리오도 명확히 경고하세요.
- 조언은 구체적인 행동·장소·유형으로 제시하세요. 막연한 조언은 금지입니다."""


# ── 포맷 유틸 ─────────────────────────────────────────────────────────────────

def format_saju(saju: dict) -> str:
    """사주 정보를 LLM 프롬프트용 텍스트로 변환"""
    def p(pillar: dict) -> str:
        return (
            f"{pillar.get('gan','')}{pillar.get('zhi','')}"
            f"({pillar.get('gan_kr','')}{pillar.get('zhi_kr','')} / "
            f"{pillar.get('gan_wuxing','')}{pillar.get('zhi_wuxing','')})"
        )

    y  = saju.get("year_pillar",  {})
    m  = saju.get("month_pillar", {})
    d  = saju.get("day_pillar",   {})
    h  = saju.get("hour_pillar",  {})
    yf = saju.get("yearly_fortune",  {})
    mf = saju.get("monthly_fortune", {})

    return (
        f"년주: {p(y)} | 월주: {p(m)} | 일주: {p(d)} | 시주: {p(h)}\n"
        f"일간: {saju.get('day_gan','')}"
        f"({saju.get('day_gan_wuxing','')})\n"
        f"세운(올해): {p(yf)} | 월운(이번달): {p(mf)}"
    )


def format_ohaeng(saju: dict) -> tuple[str, str]:
    """오행 구성 문자열과 부족 오행 문자열 반환 (하위 호환)"""
    _, _, ohaeng_str, _, lacking_str, _ = format_ohaeng_detail(saju)
    return ohaeng_str, lacking_str


def format_ohaeng_detail(saju: dict) -> tuple[list, list, str, str, str, str]:
    """오행 상세 분석 반환

    Returns:
        excess_labels  : 과다 오행 레이블 리스트  (점수 3 이상)
        lacking_labels : 부족 오행 레이블 리스트  (점수 0)
        ohaeng_str     : 전체 점수 한 줄 문자열
        excess_str     : 과다 오행 표시 문자열
        lacking_str    : 부족 오행 표시 문자열
        balance_note   : 균형 상태 한 줄 요약
    """
    scores = saju.get("ohaeng_scores", {})
    elem_map = [
        ("wood",  "木(목·나무)"),
        ("fire",  "火(화·불)"),
        ("earth", "土(토·흙)"),
        ("metal", "金(금·쇠)"),
        ("water", "水(수·물)"),
    ]

    lines, excess_labels, lacking_labels = [], [], []
    for key, label in elem_map:
        cnt = scores.get(key, 0)
        pct = round(cnt / 8 * 100)
        tag = " ▲과다" if cnt >= 3 else (" ▼부족" if cnt == 0 else "")
        lines.append(f"{label}: {cnt}점({pct}%){tag}")
        if cnt >= 3:
            excess_labels.append(label)
        if cnt == 0:
            lacking_labels.append(label)

    ohaeng_str  = " / ".join(lines)
    excess_str  = ", ".join(excess_labels)  if excess_labels  else "없음"
    lacking_str = ", ".join(lacking_labels) if lacking_labels else "없음 (균형)"

    if excess_labels and lacking_labels:
        balance_note = f"{excess_str} 과다 / {lacking_str} 부족"
    elif excess_labels:
        balance_note = f"{excess_str} 과다 (나머지 균형)"
    elif lacking_labels:
        balance_note = f"{lacking_str} 부족 (나머지 균형)"
    else:
        balance_note = "전체적으로 균형 잡힌 사주"

    return excess_labels, lacking_labels, ohaeng_str, excess_str, lacking_str, balance_note
