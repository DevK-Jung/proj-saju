"""사주 계산 엔진 검증 테스트

테스트 케이스 기준:
  - 일주 기준일: 1984-02-02 = 甲子日 (JDN=2,445,733)
  - 절기: pyswisseph Moshier 에페메리스 기반
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import date

from app.engine.solar_terms import _date_to_jd, _jd_to_date, find_solar_term_jd
from app.engine.calculator import (
    _calc_day_ganzhi,
    _calc_year_ganzhi,
    _calc_month_ganzhi,
)
from app.engine.constants import TIANGAN, DIZHI, DAY_PILLAR_ANCHOR_JDN


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

def gan(idx: int) -> str:
    return TIANGAN[idx % 10]

def zhi(idx: int) -> str:
    return DIZHI[idx % 12]

def pillar_str(gan_idx: int, zhi_idx: int) -> str:
    return f"{TIANGAN[gan_idx % 10]}{DIZHI[zhi_idx % 12]}"


# ─── 테스트 1: 일주 기준일 자체 검증 ─────────────────────────────────────────

def test_anchor_day_jdn():
    """1984-02-02의 JDN이 상수와 일치하는지 확인"""
    assert int(_date_to_jd(date(1984, 2, 2))) == DAY_PILLAR_ANCHOR_JDN


def test_day_pillar_anchor():
    """기준일 1984-02-02 = 甲子日 (index 0)"""
    g, z = _calc_day_ganzhi(date(1984, 2, 2))
    assert gan(g) == "甲", f"기대 甲, 실제 {gan(g)}"
    assert zhi(z) == "子", f"기대 子, 실제 {zhi(z)}"


def test_day_pillar_previous_day():
    """1984-02-01 = 甲子 전날 = 癸亥"""
    g, z = _calc_day_ganzhi(date(1984, 2, 1))
    assert gan(g) == "癸", f"기대 癸, 실제 {gan(g)}"
    assert zhi(z) == "亥", f"기대 亥, 실제 {zhi(z)}"


# ─── 테스트 2: 60일 후 동일 일주 ─────────────────────────────────────────────

def test_day_pillar_60_cycle():
    """1984-02-02로부터 정확히 2160일(=36×60) 후 = 1990-01-01도 甲子日이어야 함"""
    target = date(1990, 1, 1)
    days_diff = (target - date(1984, 2, 2)).days
    assert days_diff == 2160
    assert days_diff % 60 == 0

    g, z = _calc_day_ganzhi(target)
    assert gan(g) == "甲", f"기대 甲, 실제 {gan(g)}"
    assert zhi(z) == "子", f"기대 子, 실제 {zhi(z)}"


def test_year_pillar_1990_jan():
    """1990-01-01은 立春(1990-02-04) 이전이므로 년주 = 己巳"""
    g, z = _calc_year_ganzhi(date(1990, 1, 1))
    assert TIANGAN[g] == "己", f"기대 己, 실제 {TIANGAN[g]}"
    assert DIZHI[z]  == "巳", f"기대 巳, 실제 {DIZHI[z]}"


def test_month_pillar_1990_jan():
    """1990-01-01은 大雪(12월) ~ 小寒(1월) 사이 → 子月 (丙子)
    己年: YEAR_STEM_TO_MONTH_STEM_BASE[5]=2, 子月=index10 → (2+10)%10=2 → 丙
    """
    year_g, _ = _calc_year_ganzhi(date(1990, 1, 1))
    m_g, m_z = _calc_month_ganzhi(date(1990, 1, 1), year_g)
    assert TIANGAN[m_g] == "丙", f"기대 丙, 실제 {TIANGAN[m_g]}"
    assert DIZHI[m_z]   == "子", f"기대 子, 실제 {DIZHI[m_z]}"


# ─── 테스트 3: 입춘 경계 (년주 변경) ─────────────────────────────────────────

def test_year_pillar_before_lichun_1990():
    """1990-02-03 = 1990년 立春 직전 → 년주 己巳"""
    g, z = _calc_year_ganzhi(date(1990, 2, 3))
    assert TIANGAN[g] == "己"
    assert DIZHI[z]   == "巳"


def test_year_pillar_after_lichun_1990():
    """1990-02-05 = 1990년 立春(2월4일) 직후 → 년주 庚午"""
    g, z = _calc_year_ganzhi(date(1990, 2, 5))
    assert TIANGAN[g] == "庚", f"기대 庚, 실제 {TIANGAN[g]}"
    assert DIZHI[z]   == "午", f"기대 午, 실제 {DIZHI[z]}"


def test_lichun_1990_date():
    """1990년 立春 날짜가 2월 4일인지 확인 (KST 기준)"""
    from app.engine.solar_terms import KST_OFFSET
    jd = find_solar_term_jd(315.0, 1990)
    lichun = _jd_to_date(jd + KST_OFFSET)
    assert lichun == date(1990, 2, 4), f"기대 1990-02-04, 실제 {lichun}"
