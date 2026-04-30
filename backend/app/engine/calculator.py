from datetime import datetime
from sajupy import calculate_saju as _sajupy_calc, lunar_to_solar as _sajupy_lunar_to_solar

from app.engine.constants import (
    TIANGAN, TIANGAN_KR, DIZHI, DIZHI_KR,
    WUXING_TIANGAN, WUXING_DIZHI,
    YIN_YANG, SIPSUNG_MAP,
    JIEQI_LONGITUDES,
    CITY_LONGITUDE, DEFAULT_LONGITUDE,
)
from app.engine.models import Pillar, OhaengScores, SajuData, SajuRequest


# ─────────────────────────────────────────
# 십성
# ─────────────────────────────────────────
def _calc_sipsung(day_gan: str, target_gan: str) -> str:
    day_wx = WUXING_TIANGAN[day_gan]
    target_wx = WUXING_TIANGAN[target_gan]
    same = YIN_YANG[day_gan] == YIN_YANG[target_gan]
    return SIPSUNG_MAP.get((day_wx, target_wx, same), "비견")


# ─────────────────────────────────────────
# Pillar 생성
# ─────────────────────────────────────────
def _pillar_from_chars(gan: str, zhi: str, day_gan: str = "") -> Pillar:
    """天干·地支 문자를 받아 Pillar 모델로 변환."""
    g_idx = TIANGAN.index(gan)
    z_idx = DIZHI.index(zhi)
    return Pillar(
        gan=gan,
        zhi=zhi,
        gan_kr=TIANGAN_KR[g_idx],
        zhi_kr=DIZHI_KR[z_idx],
        gan_wuxing=WUXING_TIANGAN[gan],
        zhi_wuxing=WUXING_DIZHI[zhi],
        sipsung=_calc_sipsung(day_gan, gan) if day_gan else "",
    )


# ─────────────────────────────────────────
# 음력 → 양력 변환
# ─────────────────────────────────────────
def _lunar_to_solar(birth_date: str) -> tuple[int, int, int]:
    y, m, d = map(int, birth_date.split("-"))
    result = _sajupy_lunar_to_solar(y, m, d, is_leap_month=False)
    return result["solar_year"], result["solar_month"], result["solar_day"]


# ─────────────────────────────────────────
# 대운 시작 나이 (pyswisseph 기반)
# ─────────────────────────────────────────
def _calc_daeun_start_age(dt: datetime, gender: str, year_gan: str) -> int:
    from app.engine.solar_terms import datetime_to_jd_ut, find_solar_term_jd

    yy = YIN_YANG[year_gan]
    forward = (gender == "M" and yy == "양") or (gender == "F" and yy == "음")

    jd = datetime_to_jd_ut(dt)
    diffs = []

    for y in [dt.year - 1, dt.year, dt.year + 1]:
        for lon in JIEQI_LONGITUDES:
            jq = find_solar_term_jd(float(lon), y)
            diff = jq - jd
            if forward and diff > 0:
                diffs.append(diff)
            elif not forward and diff < 0:
                diffs.append(abs(diff))

    return max(1, round(min(diffs) / 3)) if diffs else 1


# ─────────────────────────────────────────
# 대운 8주
# ─────────────────────────────────────────
def _calc_daeun_pillars(
    month_gan: str, month_zhi: str,
    year_gan: str,
    gender: str,
    day_gan: str,
) -> list[Pillar]:
    yy = YIN_YANG[year_gan]
    forward = (gender == "M" and yy == "양") or (gender == "F" and yy == "음")

    mg_idx = TIANGAN.index(month_gan)
    mz_idx = DIZHI.index(month_zhi)

    daeun = []
    for i in range(1, 9):
        offset = i if forward else -i
        g = (mg_idx + offset) % 10
        z = (mz_idx + offset) % 12
        daeun.append(_pillar_from_chars(TIANGAN[g], DIZHI[z], day_gan))
    return daeun


# ─────────────────────────────────────────
# 오행
# ─────────────────────────────────────────
def _calc_ohaeng(pillars: list[Pillar]) -> OhaengScores:
    scores = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for p in pillars:
        scores[p.gan_wuxing] += 1
        scores[p.zhi_wuxing] += 1
    return OhaengScores(
        wood=scores["木"],
        fire=scores["火"],
        earth=scores["土"],
        metal=scores["金"],
        water=scores["水"],
    )


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def calculate_saju(req: SajuRequest) -> SajuData:
    # 1. 날짜 변환
    if req.calendar_type == "lunar":
        y, m, d = _lunar_to_solar(req.birth_date)
    else:
        y, m, d = map(int, req.birth_date.split("-"))

    if req.birth_time and req.birth_time != "미상":
        parts = req.birth_time.split(":")
        h = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
    else:
        h, minute = 12, 0

    # 2. 도시명 → 경도 (Nominatim 없이 직접 조회)
    longitude = CITY_LONGITUDE.get(req.city, DEFAULT_LONGITUDE)

    # 3. sajupy로 사주 4주 계산
    #    야자시(23시): 다음날 子時로 처리 (early_zi_time=False)
    #    조자시(0시): 당일 子時 유지 (early_zi_time=True, 기본값)
    early_zi = not (h == 23)
    raw = _sajupy_calc(y, m, d, h, minute, longitude=longitude, use_solar_time=True, early_zi_time=early_zi)

    year_gan  = raw["year_stem"]
    year_zhi  = raw["year_branch"]
    month_gan = raw["month_stem"]
    month_zhi = raw["month_branch"]
    day_gan   = raw["day_stem"]
    day_zhi   = raw["day_branch"]
    hour_gan  = raw["hour_stem"]
    hour_zhi  = raw["hour_branch"]

    # 3. Pillar 객체 생성 (일주는 sipsung 없음)
    yp = _pillar_from_chars(year_gan,  year_zhi,  day_gan)
    mp = _pillar_from_chars(month_gan, month_zhi, day_gan)
    dp = _pillar_from_chars(day_gan,   day_zhi)
    hp = _pillar_from_chars(hour_gan,  hour_zhi,  day_gan)

    # 4. 올해 세운·이번 달 월운
    now = datetime.now()
    now_raw = _sajupy_calc(now.year, now.month, now.day, now.hour, now.minute)
    yearly  = _pillar_from_chars(now_raw["year_stem"],  now_raw["year_branch"],  day_gan)
    monthly = _pillar_from_chars(now_raw["month_stem"], now_raw["month_branch"], day_gan)

    # 5. 대운 시작 나이
    birth_dt = datetime(y, m, d, h, minute)
    daeun_start = _calc_daeun_start_age(birth_dt, req.gender, year_gan)

    # 6. 대운 8주
    daeun = _calc_daeun_pillars(month_gan, month_zhi, year_gan, req.gender, day_gan)

    # 7. 오행 점수
    ohaeng = _calc_ohaeng([yp, mp, dp, hp])

    return SajuData(
        year_pillar=yp,
        month_pillar=mp,
        day_pillar=dp,
        hour_pillar=hp,
        day_gan=day_gan,
        day_gan_wuxing=WUXING_TIANGAN[day_gan],
        yearly_fortune=yearly,
        monthly_fortune=monthly,
        daeun=daeun,
        daeun_start_age=daeun_start,
        ohaeng_scores=ohaeng,
    )