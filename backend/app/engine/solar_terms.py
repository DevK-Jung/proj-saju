import swisseph as swe
from datetime import datetime, timedelta
from app.engine.constants import JIEQI_LONGITUDES

KST_OFFSET = 9 / 24.0


def datetime_to_jd_ut(dt: datetime) -> float:
    """KST → UT JD"""
    ut = dt - timedelta(hours=9)
    return swe.julday(
        ut.year, ut.month, ut.day,
        ut.hour + ut.minute / 60 + ut.second / 3600
    )


def _jd_ut_to_kst(jd: float) -> datetime:
    """UT JD → KST datetime"""
    y, m, d, h = swe.revjul(jd)
    base = datetime(y, m, int(d))
    sec = int((h % 1) * 3600)
    return base + timedelta(hours=int(h), seconds=sec) + timedelta(hours=9)


def find_solar_term_jd(target_lon: float, year: int) -> float:
    """
    절기 JD (UT 기준)
    """
    # 초기값 (입춘 기준)
    jd = swe.julday(year, 2, 4, 0.0)

    # target_lon 위치로 이동
    jd += ((target_lon - 315) % 360) / 0.985647

    for _ in range(15):
        lon, speed = swe.calc_ut(jd, swe.SUN)[0][0], swe.calc_ut(jd, swe.SUN)[0][3]

        if speed == 0:
            speed = 0.985647

        diff = (lon - target_lon + 180) % 360 - 180

        if abs(diff) < 1e-6:
            return jd

        jd -= diff / speed

    return jd


def get_current_jieqi(dt: datetime) -> tuple[int, float]:
    user_jd = datetime_to_jd_ut(dt)

    candidates = []

    # 🔥 반드시 3년 범위 탐색
    for y in [dt.year - 1, dt.year, dt.year + 1]:
        for i, lon in enumerate(JIEQI_LONGITUDES):
            try:
                jd = find_solar_term_jd(float(lon), y)
                candidates.append((i, jd))
            except:
                continue

    # 🔥 과거 절기만 필터
    past = [c for c in candidates if c[1] <= user_jd]

    if not past:
        raise ValueError("절기 계산 실패")

    # 🔥 가장 최근 절기 선택
    past.sort(key=lambda x: x[1], reverse=True)
    return past[0]