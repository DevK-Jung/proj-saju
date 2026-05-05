import { useState, useRef, useCallback } from 'react'
import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { UserInfo } from '../store/useSajuStore'

export function InfoScreen({
  userInfo, setUserInfo, onNext, onBack,
}: {
  userInfo: UserInfo
  setUserInfo: (u: Partial<UserInfo>) => void
  onNext: () => void
  onBack: () => void
}) {
  const up = <K extends keyof UserInfo>(k: K, v: UserInfo[K]) => setUserInfo({ [k]: v } as Partial<UserInfo>)

  // ── 생년월일 단일 입력 ────────────────────────────────────────────────────────
  const [birthRaw, setBirthRaw] = useState(() => {
    const { birthYear, birthMonth, birthDay } = userInfo
    if (!birthYear) return ''
    return birthYear
      + (birthMonth ? birthMonth.padStart(2, '0') : '')
      + (birthDay   ? birthDay.padStart(2, '0')   : '')
  })

  const formatBirth = (digits: string) => {
    if (digits.length <= 4) return digits
    if (digits.length <= 6) return `${digits.slice(0, 4)}.${digits.slice(4)}`
    return `${digits.slice(0, 4)}.${digits.slice(4, 6)}.${digits.slice(6)}`
  }

  const handleBirthInput = (raw: string) => {
    const digits = raw.replace(/\D/g, '').slice(0, 8)
    setBirthRaw(digits)
    setUserInfo({
      birthYear:  digits.slice(0, 4),
      birthMonth: digits.slice(4, 6),
      birthDay:   digits.slice(6, 8),
    })
  }

  // ── 태어난 시간 ─────────────────────────────────────────────────────────────
  const [ampm,       setAmpm]       = useState<'오전' | '오후'>('오전')
  const [timeHour,   setTimeHour]   = useState('')
  const [timeMinute, setTimeMinute] = useState('')
  const minuteRef = useRef<HTMLInputElement>(null)

  const syncTime = useCallback(
    (ap: string, h: string, m: string) => {
      if (!h) { setUserInfo({ birthTime: '' }); return }
      let hour = parseInt(h, 10) || 0
      if (ap === '오후' && hour !== 12) hour += 12
      if (ap === '오전' && hour === 12) hour = 0
      const hStr = String(hour).padStart(2, '0')
      const mStr = (m || '00').padStart(2, '0')
      setUserInfo({ birthTime: `${hStr}:${mStr}` })
    },
    [setUserInfo]
  )

  const valid = !!(userInfo.name && userInfo.gender && userInfo.birthYear && userInfo.birthMonth && userInfo.birthDay && userInfo.birthTime)

  return (
    <div className="screen active" style={{ flexDirection: 'column' }}>
      <Stars />
      <OracleSmall text="몇 가지 여쭤볼게요. 정확히 알수록 더 깊이 읽힙니다." />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div style={{ padding: '20px 20px 0' }}>

          {/* ── 성함 ─────────────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label">성함</label>
            <input
              className="form-input"
              placeholder="이름을 입력하세요"
              value={userInfo.name}
              maxLength={5}
              onChange={e => up('name', e.target.value.slice(0, 5))}
            />
          </div>

          {/* ── 성별 ─────────────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label">성별</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {(['남성', '여성'] as const).map(g => (
                <div key={g} className={`radio-btn${userInfo.gender === g ? ' sel' : ''}`} onClick={() => up('gender', g)}>{g}</div>
              ))}
            </div>
          </div>

          {/* ── 생년월일 ─────────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 8 }}>
            <label className="form-label">생년월일</label>
            <input
              className="form-input"
              type="tel"
              placeholder="예) 19970101"
              style={{ textAlign: 'center', letterSpacing: 2 }}
              value={formatBirth(birthRaw)}
              maxLength={10}
              onChange={e => handleBirthInput(e.target.value)}
            />
          </div>

          {/* ── 양력 / 음력 ──────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', gap: 10 }}>
              {(['양력', '음력'] as const).map(c => (
                <div key={c} className={`radio-btn${userInfo.calendar === c ? ' sel' : ''}`} onClick={() => up('calendar', c)}>{c}</div>
              ))}
            </div>
          </div>

          {/* ── 태어난 시간 (필수) ───────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label" style={{ marginBottom: 10 }}>태어난 시간</label>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <div style={{
                display: 'flex', flexShrink: 0, overflow: 'hidden',
                border: '1px solid var(--border)', borderRadius: 8,
              }}>
                {(['오전', '오후'] as const).map(ap => (
                  <button
                    key={ap}
                    type="button"
                    onClick={() => { setAmpm(ap); syncTime(ap, timeHour, timeMinute) }}
                    style={{
                      padding: '10px 13px', fontSize: 13, border: 'none', cursor: 'pointer',
                      background: ampm === ap ? 'rgba(201,146,42,0.2)' : 'transparent',
                      color: ampm === ap ? 'var(--gold)' : 'var(--text-dim)',
                      transition: 'background 0.2s',
                    }}
                  >
                    {ap}
                  </button>
                ))}
              </div>

              <input
                className="form-input"
                type="tel"
                placeholder="00"
                style={{ flex: 1, textAlign: 'center' }}
                value={timeHour}
                maxLength={2}
                onChange={e => {
                  const v = e.target.value.replace(/\D/g, '').slice(0, 2)
                  setTimeHour(v)
                  syncTime(ampm, v, timeMinute)
                  if (v.length === 2) minuteRef.current?.focus()
                }}
              />
              <span style={{ color: 'var(--text-dim)', fontSize: 13, flexShrink: 0 }}>시</span>

              <input
                ref={minuteRef}
                className="form-input"
                type="tel"
                placeholder="00"
                style={{ flex: 1, textAlign: 'center' }}
                value={timeMinute}
                maxLength={2}
                onChange={e => {
                  const v = e.target.value.replace(/\D/g, '').slice(0, 2)
                  setTimeMinute(v)
                  syncTime(ampm, timeHour, v)
                }}
              />
              <span style={{ color: 'var(--text-dim)', fontSize: 13, flexShrink: 0 }}>분</span>
            </div>
          </div>

          {/* ── 출생지 (진태양시 보정용) ─────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label">출생지</label>
            <select
              className="form-input"
              value={userInfo.city ?? ''}
              onChange={e => up('city', e.target.value === '' ? null : e.target.value)}
              style={{ cursor: 'pointer' }}
            >
              <option value="">모름 (선택 안 함)</option>
              <option value="Seoul">서울</option>
              <option value="Busan">부산</option>
              <option value="Incheon">인천</option>
              <option value="Daegu">대구</option>
              <option value="Daejeon">대전</option>
              <option value="Gwangju">광주</option>
              <option value="Suwon">수원</option>
              <option value="Ulsan">울산</option>
              <option value="Jeonju">전주</option>
              <option value="Changwon">창원</option>
              <option value="Jeju">제주</option>
            </select>
          </div>

          {/* ── 연애 여부 ─────────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label">현재 연애 여부</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {(['솔로', '연애중', '기혼'] as const).map(r => (
                <div key={r} className={`radio-btn${userInfo.relationship === r ? ' sel' : ''}`} onClick={() => up('relationship', r)}>{r}</div>
              ))}
            </div>
          </div>

          {/* ── 궁금한 것 ─────────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label">가장 궁금한 것 <span style={{ fontSize: 11, color: 'var(--text-dim)', fontWeight: 400 }}>(선택 · 최대 100자)</span></label>
            <textarea
              className="form-input form-textarea"
              placeholder="무엇이 가장 궁금하신가요?"
              value={userInfo.question}
              onChange={e => up('question', e.target.value.slice(0, 100))}
              maxLength={100}
            />
            <div style={{ fontSize: 11, color: 'var(--text-dim)', textAlign: 'right', marginTop: 4 }}>
              {userInfo.question.length}/100
            </div>
          </div>

        </div>
      </div>
      <BottomNav screen={1} total={9} onNext={onNext} onBack={onBack} disabled={!valid} />
    </div>
  )
}