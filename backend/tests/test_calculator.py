"""사주 계산 엔진 검증 테스트 (sajupy 기반)"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.engine.calculator import calculate_saju
from app.engine.models import SajuRequest
from app.engine.solar_terms import find_solar_term_jd, KST_OFFSET
import swisseph as swe
from datetime import date


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

def _jd_to_date(jd: float) -> date:
    y, m, d, _ = swe.revjul(jd)
    return date(y, m, int(d))

def req(birth_date, birth_time="12:00", gender="M", calendar_type="solar"):
    return SajuRequest(birth_date=birth_date, birth_time=birth_time,
                       gender=gender, calendar_type=calendar_type)


# ─── 테스트 1: known case 검증 ───────────────────────────────────────────────

def test_known_case_1990_10_10():
    """1990-10-10 14:30 남성 → 庚午年 丙戌月 戊申日 己未時"""
    result = calculate_saju(req("1990-10-10", "14:30"))
    assert result.year_pillar.gan  == "庚"
    assert result.year_pillar.zhi  == "午"
    assert result.month_pillar.gan == "丙"
    assert result.month_pillar.zhi == "戌"
    assert result.day_pillar.gan   == "戊"
    assert result.day_pillar.zhi   == "申"
    assert result.hour_pillar.gan  == "己"
    assert result.hour_pillar.zhi  == "未"


def test_year_pillar_before_lichun():
    """1990-01-01은 立春 이전 → 년주 己巳"""
    result = calculate_saju(req("1990-01-01"))
    assert result.year_pillar.gan == "己"
    assert result.year_pillar.zhi == "巳"


def test_year_pillar_after_lichun():
    """1990-02-05는 立春(1990-02-04) 이후 → 년주 庚午"""
    result = calculate_saju(req("1990-02-05"))
    assert result.year_pillar.gan == "庚"
    assert result.year_pillar.zhi == "午"


# ─── 테스트 2: 음력 변환 ──────────────────────────────────────────────────────

def test_lunar_calendar_conversion():
    """음력 1990-09-22 14:30 → 양력 1990-10-10 → 庚午年"""
    result = calculate_saju(req("1990-09-22", "14:30", calendar_type="lunar"))
    assert result.year_pillar.gan == "庚"
    assert result.year_pillar.zhi == "午"


# ─── 테스트 3: 야자시 ─────────────────────────────────────────────────────────

def test_early_zi_shi():
    """23:30 → 야자시 처리: 다음 날 일주로 계산"""
    result_normal = calculate_saju(req("1990-10-10", "22:00"))
    result_yaja   = calculate_saju(req("1990-10-10", "23:30"))
    # 야자시는 10일이 아닌 11일 일주
    result_next   = calculate_saju(req("1990-10-11", "00:30"))
    assert result_yaja.day_pillar.gan == result_next.day_pillar.gan
    assert result_yaja.day_pillar.zhi == result_next.day_pillar.zhi


# ─── 테스트 4: 절기 경계 ─────────────────────────────────────────────────────

def test_lichun_1990_date():
    """1990년 立春(황경 315°)이 2월 4일인지 확인 (KST 기준)"""
    jd = find_solar_term_jd(315.0, 1990)
    lichun = _jd_to_date(jd + KST_OFFSET)
    assert lichun == date(1990, 2, 4), f"기대 1990-02-04, 실제 {lichun}"


# ─── 테스트 5: Pillar 필드 완결성 ────────────────────────────────────────────

def test_pillar_fields_complete():
    """모든 Pillar 필드가 비어있지 않은지 확인"""
    result = calculate_saju(req("1995-03-15", "09:00", gender="F"))
    for pillar in [result.year_pillar, result.month_pillar, result.hour_pillar]:
        assert pillar.gan and pillar.zhi
        assert pillar.gan_kr and pillar.zhi_kr
        assert pillar.gan_wuxing and pillar.zhi_wuxing
        assert pillar.sipsung  # 일주 제외한 나머지는 십성 있어야 함
    # 일주는 sipsung 없음
    assert result.day_pillar.gan and result.day_pillar.zhi


# ─── 테스트 6: 대운 ───────────────────────────────────────────────────────────

def test_daeun_count():
    """대운이 8개인지 확인"""
    result = calculate_saju(req("1990-10-10", "14:30"))
    assert len(result.daeun) == 8


def test_daeun_start_age_positive():
    """대운 시작 나이가 1 이상인지 확인"""
    result = calculate_saju(req("1990-10-10", "14:30"))
    assert result.daeun_start_age >= 1


# ─── 테스트 7: 오행 점수 ─────────────────────────────────────────────────────

def test_ohaeng_total():
    """오행 점수 합계가 8 (천간 4 + 지지 4)"""
    result = calculate_saju(req("1990-10-10", "14:30"))
    s = result.ohaeng_scores
    total = s.wood + s.fire + s.earth + s.metal + s.water
    assert total == 8