"""절기(節) 계산 모듈 — pyswisseph 기반

태양 황경 계산에 Swiss Ephemeris(Moshier 내장 에페메리스)를 사용한다.
외부 데이터 파일 없이 동작하며, 600 BC ~ 2400 AD 범위에서 일(日) 수준 정확도를 보장한다.
"""

from datetime import date

import swisseph as swe

from app.engine.constants import JIEQI_LONGITUDES, MONTH_ZHI_ORDER

KST_OFFSET = 9.0 / 24.0  # UTC → KST Julian Day 보정값


# ─── Julian Day 변환 유틸리티 ───────────────────────────────────────────────────

def _date_to_jd(d: date) -> float:
    """그레고리력 날짜 → Julian Day Number (정수)"""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jd_to_date(jd: float) -> date:
    """Julian Day Number → 그레고리력 날짜"""
    jd = int(jd + 0.5)
    a = jd + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day   = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year  = 100 * b + d - 4800 + m // 10
    return date(year, month, day)


# ─── 태양 황경 계산 (pyswisseph) ────────────────────────────────────────────────

def _sun_longitude(jd_ut: float) -> float:
    """Swiss Ephemeris로 태양 황경 반환 (tropical ecliptic, 도 단위)

    FLG_MOSEPH: 내장 Moshier 에페메리스 사용 (외부 파일 불필요).
    반환값은 이미 황도상 현재 시점(ecliptic of date) 기준 — epoch 변환 불필요.
    """
    result, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_MOSEPH | swe.FLG_SPEED)
    return result[0] % 360


# ─── 절기 탐색 (이분법) ─────────────────────────────────────────────────────────

def find_solar_term_jd(target_lon: float, year: int) -> float:
    """특정 태양 황경에 도달하는 Julian Day를 이분법으로 탐색.

    Args:
        target_lon: 목표 태양 황경 (도, 0~360)
        year: 탐색 기준 연도
    Returns:
        해당 황경 도달 시점의 JD (UT)
    """
    approx_month = int((target_lon - 285) / 30) % 12 + 1
    jd_start = _date_to_jd(date(year, approx_month, 1)) - 20.0
    jd_end   = jd_start + 40.0

    for _ in range(50):
        jd_mid = (jd_start + jd_end) / 2
        lon = _sun_longitude(jd_mid)
        diff = ((lon - target_lon + 180) % 360) - 180
        if abs(diff) < 1e-6:
            break
        if diff > 0:
            jd_end = jd_mid
        else:
            jd_start = jd_mid

    return (jd_start + jd_end) / 2


# ─── 월 절기 결정 ────────────────────────────────────────────────────────────────

def get_current_jieqi(d: date) -> tuple[int, float]:
    """날짜 d(KST) 기준 직전 절(節)의 index와 JD를 반환.

    JIEQI_LONGITUDES의 12개 절기를 전년~다음해 범위에서 탐색하여,
    KST 기준 날짜가 d 이하인 것 중 가장 최근 절기를 선택한다.

    Returns:
        (jieqi_index 0~11, jieqi_jd)
        - index 0 = 立春(315°) = 寅月
        - index 11 = 小寒(285°) = 丑月
    """
    year = d.year
    best_idx = 0
    best_jd  = -1e18

    for y_offset in (-1, 0, 1):
        for i, lon in enumerate(JIEQI_LONGITUDES):
            try:
                jieqi_jd = find_solar_term_jd(float(lon), year + y_offset)
            except Exception:
                continue
            # KST 기준 날짜로 변환 후 비교
            if _jd_to_date(jieqi_jd + KST_OFFSET) <= d and jieqi_jd > best_jd:
                best_jd  = jieqi_jd
                best_idx = i

    return best_idx, best_jd
