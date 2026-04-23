"""사주 AI 프롬프트 빌더

각 화면별 전용 프롬프트 + 채팅 시스템 프롬프트
"""

from datetime import date


ORACLE_PERSONA = """당신은 30년 경력의 사주명리학 전문가이자 무녀 설아입니다.
사주를 해석할 때 다음 원칙을 따르세요:
1. 전문 용어는 반드시 한글로 풀어 설명하세요.
2. 단정적 예언보다 경향과 흐름을 중심으로 설명하세요.
3. 긍정적 측면과 주의할 점을 균형 있게 다루세요.
4. 따뜻하고 신비로운 어조로, 공감하며 설명하세요.
5. 3~5문장으로 간결하게 답변하세요."""


def _format_saju(saju: dict) -> str:
    """사주 정보를 LLM 프롬프트용 텍스트로 변환"""
    def p(pillar: dict) -> str:
        return (
            f"{pillar['gan']}{pillar['zhi']}"
            f"({pillar['gan_kr']}{pillar['zhi_kr']} / "
            f"{pillar['gan_wuxing']}{pillar['zhi_wuxing']})"
        )

    y = saju.get("year_pillar", {})
    m = saju.get("month_pillar", {})
    d = saju.get("day_pillar", {})
    h = saju.get("hour_pillar", {})
    yf = saju.get("yearly_fortune", {})
    mf = saju.get("monthly_fortune", {})

    return (
        f"년주: {p(y)} | 월주: {p(m)} | 일주: {p(d)} | 시주: {p(h)}\n"
        f"일간: {saju.get('day_gan', '')}({saju.get('day_gan_wuxing', '')})\n"
        f"세운(올해): {p(yf)} | 월운(이번달): {p(mf)}"
    )


def _format_rag(rag: list[dict]) -> str:
    if not rag:
        return "(관련 사주 지식 데이터 없음)"
    return "\n\n".join(f"[{r['category']}] {r['content']}" for r in rag[:4])


# ── 화면별 프롬프트 ──────────────────────────────────────────────────────────

def build_ohaeng_prompt(saju: dict, name: str, rag_text: str) -> list[dict]:
    today = date.today()
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pk in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        p = saju.get(pk, {})
        for wx_key in ("gan_wuxing", "zhi_wuxing"):
            wx = p.get(wx_key, "")
            if wx in counts:
                counts[wx] += 1
    total = sum(counts.values()) or 8
    ohaeng_str = " / ".join(
        f"{'木火土金水'[i]}({round(v / total * 100)}%)"
        for i, (k, v) in enumerate(zip(("木", "火", "土", "金", "水"), counts.values()))
    )

    return [
        {"role": "system", "content": ORACLE_PERSONA},
        {"role": "user", "content": (
            f"{name}님({today.year}년 기준)의 사주를 오행(五行) 관점에서 분석해주세요.\n\n"
            f"[사주팔자]\n{_format_saju(saju)}\n\n"
            f"[오행 구성]\n{ohaeng_str}\n\n"
            f"[참고 사주 지식]\n{rag_text}\n\n"
            f"오행 균형과 {name}님의 기질·성향·강점·주의점을 3~4문장으로 설명해주세요."
        )},
    ]


def build_yearly_prompt(saju: dict, name: str, rag_text: str) -> list[dict]:
    today = date.today()
    yf = saju.get("yearly_fortune", {})
    yearly_gan = yf.get("gan", "")
    yearly_zhi = yf.get("zhi", "")

    return [
        {"role": "system", "content": ORACLE_PERSONA},
        {"role": "user", "content": (
            f"{name}님의 {today.year}년 운세를 분석해주세요.\n\n"
            f"[사주팔자]\n{_format_saju(saju)}\n\n"
            f"[{today.year}년 세운: {yearly_gan}{yearly_zhi}]\n"
            f"올해의 간지({yearly_gan}{yearly_zhi})가 사주에 미치는 영향\n\n"
            f"[참고 사주 지식]\n{rag_text}\n\n"
            f"올해 총운·연애운·직업운·재물운·건강운을 종합하여 3~4문장으로 설명해주세요."
        )},
    ]


def build_monthly_prompt(saju: dict, name: str, rag_text: str) -> list[dict]:
    today = date.today()
    mf = saju.get("monthly_fortune", {})
    monthly_gan = mf.get("gan", "")
    monthly_zhi = mf.get("zhi", "")

    return [
        {"role": "system", "content": ORACLE_PERSONA},
        {"role": "user", "content": (
            f"{name}님의 {today.month}월 이번 달 운세를 분석해주세요.\n\n"
            f"[사주팔자]\n{_format_saju(saju)}\n\n"
            f"[{today.month}월 월운: {monthly_gan}{monthly_zhi}]\n\n"
            f"[참고 사주 지식]\n{rag_text}\n\n"
            f"이번 달 흐름, 주의사항, 행운 포인트를 3~4문장으로 설명해주세요."
        )},
    ]


def build_question_prompt(
    saju: dict,
    name: str,
    question: str,
    ohaeng_analysis: str,
    yearly_fortune: str,
    rag_text: str,
) -> list[dict]:
    return [
        {"role": "system", "content": ORACLE_PERSONA},
        {"role": "user", "content": (
            f"{name}님의 질문에 사주를 바탕으로 답변해주세요.\n\n"
            f"[사주팔자]\n{_format_saju(saju)}\n\n"
            f"[오행 분석]\n{ohaeng_analysis}\n\n"
            f"[올해 운세]\n{yearly_fortune}\n\n"
            f"[참고 사주 지식]\n{rag_text}\n\n"
            f"[질문]\n\"{question}\"\n\n"
            f"위 사주 분석을 근거로 질문에 4~5문장으로 따뜻하고 구체적으로 답변해주세요."
        )},
    ]


def build_chat_messages(
    saju: dict,
    name: str,
    ohaeng_analysis: str,
    yearly_fortune: str,
    monthly_fortune: str,
    question_answer: str,
    rag_text: str,
    chat_history: list,  # LangChain BaseMessage list
) -> list[dict]:
    """채팅용 메시지 리스트 (system + history + rag context 주입)"""
    today = date.today()
    answer_section = f"\n[질문 답변]\n{question_answer}" if question_answer else ""

    system_content = (
        f"{ORACLE_PERSONA}\n\n"
        f"[{name}님 사주 컨텍스트 — {today.year}년]\n"
        f"사주: {_format_saju(saju)}\n\n"
        f"오행 분석: {ohaeng_analysis}\n\n"
        f"올해 운세: {yearly_fortune}\n\n"
        f"이번 달: {monthly_fortune}"
        f"{answer_section}\n\n"
        f"[추가 참고 지식]\n{rag_text}"
    )

    messages = [{"role": "system", "content": system_content}]

    # LangChain 메시지 → OpenAI 형식 변환
    for msg in chat_history:
        role = "assistant" if hasattr(msg, "type") and msg.type == "ai" else "user"
        messages.append({"role": role, "content": msg.content})

    return messages
