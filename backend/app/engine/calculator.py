"""사주팔자 계산 엔진

절기 계산: solar_terms.py (pyswisseph 기반)
일주 기준: 1984-02-02 = 甲子日 (JDN = 2,445,733)
자시 처리: 야자시(夜子時) 기준 — 23:xx는 다음날 子時로 계산
"""

from datetime import date, timedelta

from korean_lunar_calendar import KoreanLunarCalendar

from app.engine.constants import (
    DAY_PILLAR_ANCHOR_JDN,
    DAY_STEM_TO_HOUR_STEM_BASE,
    DIZHI,
    DIZHI_KR,
    HOUR_TO_ZHI,
    JIEQI_LONGITUDES,
    MONTH_ZHI_ORDER,
    SIPSUNG_MAP,
    TIANGAN,
    TIANGAN_KR,
    WUXING_DIZHI,
    WUXING_TIANGAN,
    YEAR_STEM_TO_MONTH_STEM_BASE,
    YIN_YANG,
)
from app.engine.models import OhaengScores, Pillar, SajuData, SajuRequest
from app.engine.solar_terms import (
    KST_OFFSET,
    _date_to_jd,
    _jd_to_date,
    find_solar_term_jd,
    get_current_jieqi,
)


# ─── 십성 / 기둥 생성 ──────────────────────────────────────────────────────────

def _calc_sipsung(day_gan: str, target_gan: str) -> str:
    day_wx    = WUXING_TIANGAN[day_gan]
    target_wx = WUXING_TIANGAN[target_gan]
    same_yy   = YIN_YANG[day_gan] == YIN_YANG[target_gan]
    return SIPSUNG_MAP.get((day_wx, target_wx, same_yy), "비견")


def _make_pillar(gan_idx: int, zhi_idx: int, day_gan: str = "") -> Pillar:
    gi  = gan_idx % 10
    zi  = zhi_idx % 12
    gan = TIANGAN[gi]
    zhi = DIZHI[zi]
    return Pillar(
        gan=gan,
        zhi=zhi,
        gan_kr=TIANGAN_KR[gi],
        zhi_kr=DIZHI_KR[zi],
        gan_wuxing=WUXING_TIANGAN[gan],
        zhi_wuxing=WUXING_DIZHI[zhi],
        sipsung=_calc_sipsung(day_gan, gan) if day_gan else "",
    )


# ─── 사주 핵심 계산 ────────────────────────────────────────────────────────────

def _calc_year_ganzhi(d: date) -> tuple[int, int]:
    """년주: 立春(태양 황경 315°) KST 기준 이전이면 전년도 간지 사용"""
    lichun_jd   = find_solar_term_jd(315.0, d.year)
    lichun_date = _jd_to_date(lichun_jd + KST_OFFSET)
    effective   = d.year if d >= lichun_date else d.year - 1
    idx = (effective - 4) % 60
    return idx % 10, idx % 12


def _calc_month_ganzhi(d: date, year_stem_idx: int) -> tuple[int, int]:
    """월주: 직전 절(節) 기준, 五虎遁年法으로 월간 결정"""
    best_idx, _ = get_current_jieqi(d)
    month_zhi   = MONTH_ZHI_ORDER[best_idx]
    base_stem   = YEAR_STEM_TO_MONTH_STEM_BASE[year_stem_idx]
    month_stem  = (base_stem + best_idx) % 10
    return month_stem, month_zhi


def _calc_day_ganzhi(d: date) -> tuple[int, int]:
    """일주: JDN 기반 60-cycle
    기준일: 1984-02-02 = 甲子日 (JDN = 2,445,733)
    """
    jdn = int(_date_to_jd(d))
    idx = (jdn - DAY_PILLAR_ANCHOR_JDN) % 60
    return idx % 10, idx % 12


def _calc_hour_ganzhi(hour: int, day_stem_idx: int) -> tuple[int, int]:
    """시주: 五鼠遁日法"""
    zhi_idx  = HOUR_TO_ZHI.get(hour, 0)
    base     = DAY_STEM_TO_HOUR_STEM_BASE[day_stem_idx]
    gan_idx  = (base + zhi_idx) % 10
    return gan_idx, zhi_idx


def _calc_daeun_start_age(birth_date: date, gender: str, year_stem_idx: int) -> int:
    """대운 시작 나이: 다음/이전 절기까지 일수 ÷ 3
    양남음녀=순행(다음 절기), 음남양녀=역행(이전 절기)
    """
    year_yy = YIN_YANG[TIANGAN[year_stem_idx]]
    forward = (gender == "M" and year_yy == "양") or (gender == "F" and year_yy == "음")

    jd_birth = _date_to_jd(birth_date)
    min_days = 90.0

    for lon in [float(x) for x in JIEQI_LONGITUDES]:
        for y_off in (-1, 0, 1):
            try:
                jieqi_jd = find_solar_term_jd(lon, birth_date.year + y_off)
            except Exception:
                continue
            diff = jieqi_jd - jd_birth
            if forward and 0 < diff < min_days:
                min_days = diff
            elif not forward and -90 < diff < 0:
                min_days = abs(diff)

    return max(1, round(min_days / 3))


# ─── 오행 점수 계산 ─────────────────────────────────────────────────────────────

_WUXING_KR = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}

def _calc_ohaeng_scores(pillars: list[Pillar]) -> OhaengScores:
    """4기둥(천간 4 + 지지 4 = 총 8점) 오행 점수 집계"""
    cnt: dict[str, int] = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for p in pillars:
        cnt[p.gan_wuxing] += 1
        cnt[p.zhi_wuxing] += 1
    return OhaengScores(
        wood=cnt["木"],
        fire=cnt["火"],
        earth=cnt["土"],
        metal=cnt["金"],
        water=cnt["水"],
    )


# ─── 공개 API ──────────────────────────────────────────────────────────────────

def calculate_saju(request: SajuRequest) -> SajuData:
    """생년월일시 → 사주팔자 계산"""
    birth_date = request.birth_date
    if request.calendar_type == "lunar":
        cal = KoreanLunarCalendar()
        y, m, d = map(int, birth_date.split("-"))
        cal.setLunarDate(y, m, d, False)
        birth_date = cal.getSolarIsoFormat()

    y, mo, d = map(int, birth_date.split("-"))
    birth_dt = date(y, mo, d)

    if request.birth_time and request.birth_time != "미상":
        h = int(request.birth_time.split(":")[0])
    else:
        h = 12

    # 야자시(夜子時) 기준: 23:xx는 다음날 子時로 계산
    # 정자시(正子時) 기준을 원하면 이 줄을 제거하면 됨
    calc_date = birth_dt + timedelta(days=1) if h == 23 else birth_dt

    # 사주 계산
    year_gan_idx,  year_zhi_idx  = _calc_year_ganzhi(calc_date)
    month_gan_idx, month_zhi_idx = _calc_month_ganzhi(calc_date, year_gan_idx)
    day_gan_idx,   day_zhi_idx   = _calc_day_ganzhi(calc_date)
    hour_gan_idx,  hour_zhi_idx  = _calc_hour_ganzhi(h, day_gan_idx)

    day_gan = TIANGAN[day_gan_idx]

    year_pillar  = _make_pillar(year_gan_idx,  year_zhi_idx,  day_gan)
    month_pillar = _make_pillar(month_gan_idx, month_zhi_idx, day_gan)
    day_pillar   = _make_pillar(day_gan_idx,   day_zhi_idx,   day_gan)
    hour_pillar  = _make_pillar(hour_gan_idx,  hour_zhi_idx,  day_gan)

    # 세운 / 월운 (오늘 기준)
    today = date.today()
    ty_gan, ty_zhi = _calc_year_ganzhi(today)
    tm_gan, tm_zhi = _calc_month_ganzhi(today, ty_gan)
    yearly_fortune  = _make_pillar(ty_gan, ty_zhi, day_gan)
    monthly_fortune = _make_pillar(tm_gan, tm_zhi, day_gan)

    # 대운: 60-cycle 순환 (연간 경계에서도 정확)
    year_yy = YIN_YANG[TIANGAN[year_gan_idx]]
    forward = (request.gender == "M" and year_yy == "양") or \
              (request.gender == "F" and year_yy == "음")

    birth_month_n = (6 * month_gan_idx - 5 * month_zhi_idx) % 60
    daeun_list = [
        _make_pillar(
            ((birth_month_n + (i if forward else -i)) % 60) % 10,
            ((birth_month_n + (i if forward else -i)) % 60) % 12,
            day_gan,
        )
        for i in range(1, 9)
    ]

    daeun_start = _calc_daeun_start_age(calc_date, request.gender, year_gan_idx)

    four_pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]

    return SajuData(
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_gan=day_gan,
        day_gan_wuxing=WUXING_TIANGAN[day_gan],
        yearly_fortune=yearly_fortune,
        monthly_fortune=monthly_fortune,
        daeun=daeun_list,
        daeun_start_age=daeun_start,
        ohaeng_scores=_calc_ohaeng_scores(four_pillars),
    )
