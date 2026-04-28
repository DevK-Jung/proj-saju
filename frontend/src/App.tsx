import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useSajuStore, UserInfo, MonthlyFortune } from './store/useSajuStore'
import { SajuData } from './types/saju'

// ─── Stars ─────────────────────────────────────────────────────────────────
function Stars() {
  const stars = useMemo(() => Array.from({ length: 60 }, (_, i) => ({
    id: i,
    size: Math.random() * 2 + 0.5,
    top: Math.random() * 100,
    left: Math.random() * 100,
    d: (Math.random() * 4 + 2).toFixed(1) + 's',
    delay: (Math.random() * 4).toFixed(1) + 's',
    op: (Math.random() * 0.5 + 0.2).toFixed(2),
  })), [])
  return (
    <div className="stars">
      {stars.map(s => (
        <div key={s.id} className="star" style={{
          width: s.size, height: s.size,
          top: s.top + '%', left: s.left + '%',
          ['--d' as string]: s.d,
          ['--delay' as string]: s.delay,
          ['--op' as string]: s.op,
        }} />
      ))}
    </div>
  )
}

// ─── Sparks ─────────────────────────────────────────────────────────────────
function Sparks() {
  const sparks = useMemo(() => Array.from({ length: 10 }, (_, i) => ({
    id: i,
    top: (10 + Math.random() * 80) + '%',
    left: Math.random() * 100 + '%',
    d: (2 + Math.random() * 3).toFixed(1) + 's',
    delay: (Math.random() * 3).toFixed(1) + 's',
  })), [])
  return (
    <div className="oracle-particles">
      {sparks.map(s => (
        <div key={s.id} className="oracle-spark" style={{
          top: s.top, left: s.left,
          ['--d' as string]: s.d,
          ['--delay' as string]: s.delay,
        }} />
      ))}
    </div>
  )
}

// ─── Oracle Full ─────────────────────────────────────────────────────────────
function OracleFull({ text, typing }: { text?: string; typing?: boolean }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 40, flexShrink: 0 }}>
      <div style={{ position: 'relative' }}>
        <div className="oracle-bust">
          <img src="/saju.png" alt="설아" />
          <Sparks />
        </div>
      </div>
      <div style={{ marginTop: 10, fontSize: 11, letterSpacing: 3, color: 'var(--gold)', fontFamily: 'Cinzel, serif' }}>
        ORACLE · 설아
      </div>
      {text !== undefined && (
        <div className="oracle-bubble" style={{ marginTop: 16 }}>
          <p>{text}{typing && <span className="cursor" />}</p>
        </div>
      )}
    </div>
  )
}

// ─── Oracle Small ────────────────────────────────────────────────────────────
function OracleSmall({ text }: { text?: string }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 14,
      padding: '16px 20px 12px', flexShrink: 0,
      borderBottom: '1px solid var(--border)',
      background: 'linear-gradient(to bottom, rgba(14,8,32,0.98) 80%, transparent)',
      position: 'sticky', top: 0, zIndex: 10,
    }}>
      <div className="oracle-ring sm">
        <div className="oracle-face"><img src="/saju.png" alt="설아" /></div>
      </div>
      <div>
        <div style={{ fontSize: 10, letterSpacing: 2, color: 'var(--gold)', fontFamily: 'Cinzel, serif', marginBottom: 3 }}>
          ORACLE · 설아
        </div>
        {text && <div className="oracle-bubble-sm">{text}</div>}
      </div>
    </div>
  )
}

// ─── Typewriter ──────────────────────────────────────────────────────────────
function useTypewriter(text: string, speed = 40) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)
  useEffect(() => {
    setDisplayed(''); setDone(false)
    if (!text) return
    let i = 0
    const id = setInterval(() => {
      i++
      setDisplayed(text.slice(0, i))
      if (i >= text.length) { clearInterval(id); setDone(true) }
    }, speed)
    return () => clearInterval(id)
  }, [text, speed])
  return { displayed, done }
}

// ─── Bottom Nav ──────────────────────────────────────────────────────────────
function BottomNav({
  screen, total, onNext, onBack,
  nextLabel = '다음', disabled = false,
}: {
  screen: number; total: number; onNext: () => void; onBack: () => void;
  nextLabel?: string; disabled?: boolean;
}) {
  return (
    <div className="bottom-nav">
      <button className="btn-ghost" onClick={onBack} style={{ visibility: screen > 0 ? 'visible' : 'hidden' }}>이전</button>
      <div className="progress-dots">
        {Array.from({ length: total }).map((_, i) => (
          <div key={i} className={`progress-dot${i === screen ? ' active' : ''}`} />
        ))}
      </div>
      <button className="btn-gold" onClick={onNext} disabled={disabled} style={{ padding: '12px 28px', fontSize: 14 }}>
        {nextLabel}
      </button>
    </div>
  )
}

// ─── SCREEN 0: Welcome ───────────────────────────────────────────────────────
function WelcomeScreen({ onNext }: { onNext: () => void }) {
  const greeting = '안녕하세요. 저는 운명의 문을 여는 무녀 설아입니다.\n\n당신의 사주를 풀어, 지나온 길과 앞으로의 운명을 이야기해 드리겠습니다.'
  const { displayed, done } = useTypewriter(greeting, 38)
  return (
    <div className="screen active" style={{ justifyContent: 'space-between' }}>
      <Stars />
      <div style={{ zIndex: 1, flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '48px 24px 100px', gap: 0 }}>
        <OracleFull text={displayed} typing={!done} />
        <div className="divider" />
        <p style={{ fontSize: 12, letterSpacing: 2, color: 'var(--text-dim)', textAlign: 'center', marginBottom: 32 }}>
          생년월일의 기운으로 당신의 운명을 읽습니다
        </p>
        {done && (
          <button className="btn-gold" onClick={onNext}>
            사주 보러 가기
          </button>
        )}
      </div>
    </div>
  )
}

// ─── SCREEN 1: Info Input ────────────────────────────────────────────────────
function InfoScreen({
  userInfo, setUserInfo, onNext, onBack,
}: {
  userInfo: UserInfo
  setUserInfo: (u: Partial<UserInfo>) => void
  onNext: () => void
  onBack: () => void
}) {
  const up = <K extends keyof UserInfo>(k: K, v: UserInfo[K]) => setUserInfo({ [k]: v } as Partial<UserInfo>)

  // ── 생년월일 단일 입력 ────────────────────────────────────────────────────────
  // raw: 숫자만 최대 8자리 (YYYYMMDD)
  const [birthRaw, setBirthRaw] = useState(() => {
    const { birthYear, birthMonth, birthDay } = userInfo
    if (!birthYear) return ''
    return birthYear
      + (birthMonth ? birthMonth.padStart(2, '0') : '')
      + (birthDay   ? birthDay.padStart(2, '0')   : '')
  })

  // 숫자 → "YYYY.MM.DD" 포맷 (입력 중에도 실시간 표시)
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
  const [timeUnknown, setTimeUnknown] = useState(false)
  const [ampm,       setAmpm]        = useState<'오전' | '오후'>('오전')
  const [timeHour,   setTimeHour]    = useState('')
  const [timeMinute, setTimeMinute]  = useState('')
  const minuteRef = useRef<HTMLInputElement>(null)

  const syncTime = useCallback(
    (unknown: boolean, ap: string, h: string, m: string) => {
      if (unknown || !h) { setUserInfo({ birthTime: '' }); return }
      let hour = parseInt(h, 10) || 0
      if (ap === '오후' && hour !== 12) hour += 12
      if (ap === '오전' && hour === 12) hour = 0
      const hStr = String(hour).padStart(2, '0')
      const mStr = (m || '00').padStart(2, '0')
      setUserInfo({ birthTime: `${hStr}:${mStr}` })
    },
    [setUserInfo]
  )

  // ── 유효성: 이름·성별·생년월일 필수 / 질문 선택 ────────────────────────────
  const valid = !!(userInfo.name && userInfo.gender && userInfo.birthYear && userInfo.birthMonth && userInfo.birthDay)

  return (
    <div className="screen active" style={{ flexDirection: 'column' }}>
      <Stars />
      <OracleSmall text="몇 가지 여쭤볼게요. 정확히 알수록 더 깊이 읽힙니다." />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div style={{ padding: '20px 20px 0' }}>

          {/* ── 성함 (최대 5자) ─────────────────────────────────────────────── */}
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

          {/* ── 생년월일 (단일 입력, YYYY.MM.DD 자동 포맷) ──────────────────── */}
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

          {/* ── 양력 / 음력 (생년월일 바로 아래) ───────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', gap: 10 }}>
              {(['양력', '음력'] as const).map(c => (
                <div key={c} className={`radio-btn${userInfo.calendar === c ? ' sel' : ''}`} onClick={() => up('calendar', c)}>{c}</div>
              ))}
            </div>
          </div>

          {/* ── 태어난 시간 ──────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <label className="form-label" style={{ margin: 0 }}>태어난 시간</label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--text-dim)', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={timeUnknown}
                  style={{ width: 15, height: 15, accentColor: 'var(--gold)', cursor: 'pointer' }}
                  onChange={e => {
                    setTimeUnknown(e.target.checked)
                    syncTime(e.target.checked, ampm, timeHour, timeMinute)
                  }}
                />
                모름
              </label>
            </div>

            {!timeUnknown && (
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                {/* 오전 / 오후 토글 */}
                <div style={{
                  display: 'flex', flexShrink: 0, overflow: 'hidden',
                  border: '1px solid var(--border)', borderRadius: 8,
                }}>
                  {(['오전', '오후'] as const).map(ap => (
                    <button
                      key={ap}
                      type="button"
                      onClick={() => { setAmpm(ap); syncTime(false, ap, timeHour, timeMinute) }}
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

                {/* 시 입력 */}
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
                    syncTime(false, ampm, v, timeMinute)
                    if (v.length === 2) minuteRef.current?.focus()
                  }}
                />
                <span style={{ color: 'var(--text-dim)', fontSize: 13, flexShrink: 0 }}>시</span>

                {/* 분 입력 */}
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
                    syncTime(false, ampm, timeHour, v)
                  }}
                />
                <span style={{ color: 'var(--text-dim)', fontSize: 13, flexShrink: 0 }}>분</span>
              </div>
            )}
          </div>

          {/* ── 현재 연애 여부 ────────────────────────────────────────────────── */}
          <div style={{ marginBottom: 20 }}>
            <label className="form-label">현재 연애 여부</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {(['솔로', '연애중', '기혼'] as const).map(r => (
                <div key={r} className={`radio-btn${userInfo.relationship === r ? ' sel' : ''}`} onClick={() => up('relationship', r)}>{r}</div>
              ))}
            </div>
          </div>

          {/* ── 가장 궁금한 것 (선택, 최대 100자) ──────────────────────────── */}
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
      <BottomNav screen={1} total={8} onNext={onNext} onBack={onBack} disabled={!valid} />
    </div>
  )
}

// ─── SCREEN 2: Loading ───────────────────────────────────────────────────────
function LoadingScreen() {
  const msgs = ['생년월일의 기운을 읽는 중...', '천간과 지지를 배열하는 중...', '오행의 균형을 분석하는 중...', '운명의 실마리를 풀어내는 중...']
  const [idx, setIdx] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setIdx(i => (i + 1) % msgs.length), 1800)
    return () => clearInterval(id)
  }, [])
  return (
    <div className="screen active">
      <Stars />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 32, padding: 40, zIndex: 1 }}>
        <div className="oracle-ring lg">
          <div className="oracle-face"><img src="/saju.png" alt="설아" /></div>
        </div>
        <div className="loading-orb" />
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: 18, color: 'var(--gold)', marginBottom: 8 }}>사주를 읽고 있습니다</h3>
          <p style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.7 }}>{msgs[idx]}</p>
        </div>
      </div>
    </div>
  )
}

// ─── 오행 점수: 백엔드 계산값을 % 로 변환 (총 8점 기준) ─────────────────────
function calcOhaengScores(saju: SajuData) {
  const s = saju.ohaeng_scores
  const toPercent = (n: number) => Math.round((n / 8) * 100)
  return {
    wood:  toPercent(s.wood),
    fire:  toPercent(s.fire),
    earth: toPercent(s.earth),
    metal: toPercent(s.metal),
    water: toPercent(s.water),
  }
}

// ─── SCREEN 3: 오행 ──────────────────────────────────────────────────────────
function OhaengScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { sajuData, userInfo, content, analyzing } = useSajuStore()
  const scores = sajuData ? calcOhaengScores(sajuData) : { wood: 25, fire: 25, earth: 25, metal: 25, water: 25 }

  const elements = [
    { key: 'wood',  label: '목(木)', cls: 'oh-wood',  char: '木', color: '#5db85d', pct: scores.wood },
    { key: 'fire',  label: '화(火)', cls: 'oh-fire',  char: '火', color: '#e05535', pct: scores.fire },
    { key: 'earth', label: '토(土)', cls: 'oh-earth', char: '土', color: '#c8a830', pct: scores.earth },
    { key: 'metal', label: '금(金)', cls: 'oh-metal', char: '金', color: '#b8bcd4', pct: scores.metal },
    { key: 'water', label: '수(水)', cls: 'oh-water', char: '水', color: '#5588e8', pct: scores.water },
  ]

  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text={`${userInfo.name}님의 오행 에너지를 풀어봤어요.`} />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">오행 분석 · Five Elements</div>

          <div style={{ display: 'flex', justifyContent: 'center', gap: 10, marginBottom: 24 }}>
            {elements.map(e => (
              <div key={e.key} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                <div className={`ohaeng-circle ${e.cls}`}>{e.char}</div>
                <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>{e.label.split('(')[0]}</div>
              </div>
            ))}
          </div>

          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title">오행 균형</div>
            {elements.map(e => (
              <div key={e.key} style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-dim)', marginBottom: 4 }}>
                  <span>{e.label}</span><span>{e.pct}%</span>
                </div>
                <div className="ohaeng-bar-track">
                  <div className="ohaeng-bar-fill" style={{ width: e.pct + '%', background: e.color }} />
                </div>
              </div>
            ))}
          </div>

          {/* 타고난 기질 — AI 분석 (백그라운드 로드) */}
          <div className="card">
            <div className="card-title">타고난 기질 · 성격</div>
            {analyzing && !content?.personality
              ? <p style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>설아가 기운을 읽고 있습니다…</p>
              : content?.personality
                ? <p style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>{content.personality}</p>
                : <p style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>분석 준비 중…</p>
            }
          </div>

        </div>
      </div>
      <BottomNav screen={3} total={8} onNext={onNext} onBack={onBack} />
    </div>
  )
}

// ─── SCREEN 4: 만세력 ────────────────────────────────────────────────────────
function ManseryeokScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { sajuData } = useSajuStore()

  const pillars = sajuData ? [
    { name: '년주', stem: sajuData.year_pillar.gan,   branch: sajuData.year_pillar.zhi,   stemKo: sajuData.year_pillar.gan_kr,   branchKo: sajuData.year_pillar.zhi_kr },
    { name: '월주', stem: sajuData.month_pillar.gan,  branch: sajuData.month_pillar.zhi,  stemKo: sajuData.month_pillar.gan_kr,  branchKo: sajuData.month_pillar.zhi_kr },
    { name: '일주', stem: sajuData.day_pillar.gan,    branch: sajuData.day_pillar.zhi,    stemKo: sajuData.day_pillar.gan_kr,    branchKo: sajuData.day_pillar.zhi_kr },
    { name: '시주', stem: sajuData.hour_pillar.gan,   branch: sajuData.hour_pillar.zhi,   stemKo: sajuData.hour_pillar.gan_kr,   branchKo: sajuData.hour_pillar.zhi_kr },
  ] : [
    { name: '년주', stem: '甲', branch: '子', stemKo: '갑', branchKo: '자' },
    { name: '월주', stem: '丙', branch: '午', stemKo: '병', branchKo: '오' },
    { name: '일주', stem: '壬', branch: '辰', stemKo: '임', branchKo: '진' },
    { name: '시주', stem: '戊', branch: '寅', stemKo: '무', branchKo: '인' },
  ]

  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text="사주 팔자를 펼쳐보겠습니다." />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">사주 팔자 만세력</div>
          <div className="pillars">
            {pillars.map(p => (
              <div key={p.name} className="pillar">
                <div className="pillar-name">{p.name}</div>
                <div className="pillar-stem" style={{ color: 'var(--gold-l)' }}>{p.stem}</div>
                <div className="pillar-label">{p.stemKo} (천간)</div>
                <div className="pillar-branch" style={{ marginTop: 8 }}>{p.branch}</div>
                <div className="pillar-label">{p.branchKo} (지지)</div>
              </div>
            ))}
          </div>

          {sajuData && (
            <>
              <div className="card">
                <div className="card-title">세운 (올해 운)</div>
                <div style={{ display: 'flex', gap: 16, marginTop: 4 }}>
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 4 }}>년간</div>
                    <div style={{ fontSize: 22, color: 'var(--gold-l)' }}>{sajuData.yearly_fortune.gan}</div>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.6 }}>{sajuData.yearly_fortune.gan_kr}</div>
                    <div style={{ fontSize: 18, color: 'var(--text-dim)', marginTop: 6 }}>{sajuData.yearly_fortune.zhi}</div>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.6 }}>{sajuData.yearly_fortune.zhi_kr}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 4 }}>월간</div>
                    <div style={{ fontSize: 22, color: 'var(--gold-l)' }}>{sajuData.monthly_fortune.gan}</div>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.6 }}>{sajuData.monthly_fortune.gan_kr}</div>
                    <div style={{ fontSize: 18, color: 'var(--text-dim)', marginTop: 6 }}>{sajuData.monthly_fortune.zhi}</div>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.6 }}>{sajuData.monthly_fortune.zhi_kr}</div>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-title">대운</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {sajuData.daeun.map((d, i) => (
                    <div key={i} style={{ textAlign: 'center', padding: '8px 10px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', borderRadius: 8 }}>
                      <div style={{ fontSize: 14, color: 'var(--gold-l)' }}>{d.gan}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 2 }}>{d.zhi}</div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.5, marginTop: 3 }}>
                        {sajuData.daeun_start_age + (i * 10)}세
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      <BottomNav screen={2} total={8} onNext={onNext} onBack={onBack} />
    </div>
  )
}

// ─── SCREEN 5: 올해 운세 ─────────────────────────────────────────────────────
function YearlyScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { content, userInfo, analyzing } = useSajuStore()
  const year = new Date().getFullYear()
  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text={`${year}년 ${userInfo.name}님의 운세입니다.`} />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">{year}년 신년운세</div>
          <div className="card">
            {analyzing && !content?.yearly
              ? <p style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>설아가 올해 기운을 읽고 있습니다…</p>
              : <p style={{ whiteSpace: 'pre-line', lineHeight: 1.9 }}>{content?.yearly || '—'}</p>
            }
          </div>
        </div>
      </div>
      <BottomNav screen={4} total={8} onNext={onNext} onBack={onBack} />
    </div>
  )
}

// ─── SCREEN 6: 이번 달 운세 ──────────────────────────────────────────────────
const MONTHLY_CATS: { key: keyof MonthlyFortune; icon: string; color: string; bg: string }[] = [
  { key: '총운',  icon: '✦', color: '#c9922a', bg: 'rgba(201,146,42,0.1)' },
  { key: '연애운', icon: '♥', color: '#e05535', bg: 'rgba(224,85,53,0.1)'  },
  { key: '재물운', icon: '◉', color: '#5588e8', bg: 'rgba(85,136,232,0.1)' },
  { key: '직업운', icon: '◈', color: '#5db85d', bg: 'rgba(93,184,93,0.1)'  },
  { key: '사업운', icon: '◆', color: '#b8bcd4', bg: 'rgba(184,188,212,0.1)'},
]

function MonthlyScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { content, analyzing } = useSajuStore()
  const month = new Date().getMonth() + 1
  const monthly = content?.monthly   // MonthlyFortune | null

  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text={`${month}월에 일어날 일들을 살펴볼게요.`} />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">{month}월 이번 달 운세</div>

          {MONTHLY_CATS.map(cat => (
            <div key={cat.key} style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <div style={{
                  width: 30, height: 30, borderRadius: 8, flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 15, background: cat.bg, color: cat.color,
                }}>
                  {cat.icon}
                </div>
                <div style={{ fontSize: 14, color: 'var(--text)', fontWeight: 700 }}>{cat.key}</div>
              </div>
              <div className="card" style={{ margin: 0 }}>
                {analyzing && !monthly
                  ? <p style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>설아가 읽고 있습니다…</p>
                  : <p style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                      {monthly?.[cat.key] || '—'}
                    </p>
                }
              </div>
            </div>
          ))}
        </div>
      </div>
      <BottomNav screen={5} total={8} onNext={onNext} onBack={onBack} />
    </div>
  )
}

// ─── SCREEN 7: Question Answer ───────────────────────────────────────────────
function QuestionScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { content, userInfo } = useSajuStore()
  const { displayed, done: typeDone } = useTypewriter(content?.answer ?? '', 25)
  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text="궁금하셨던 질문에 답해드릴게요." />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">질문 · 답변</div>
          <div className="card" style={{ background: 'rgba(139,21,53,0.1)', borderColor: 'rgba(139,21,53,0.3)' }}>
            <div className="card-title" style={{ color: 'var(--text-dim)' }}>질문</div>
            <p style={{ color: 'var(--text)', fontStyle: 'italic' }}>"{userInfo.question}"</p>
          </div>
          <div className="card">
            <div className="card-title">설아의 답변</div>
            <p>{displayed}{!typeDone && <span className="cursor" />}</p>
          </div>
        </div>
      </div>
      <BottomNav screen={6} total={8} onNext={onNext} onBack={onBack} nextLabel="채팅으로 더 묻기" />
    </div>
  )
}

// ─── SCREEN 8: Chat ──────────────────────────────────────────────────────────
function ChatScreen({ onBack }: { onBack: () => void }) {
  const { userInfo, streamChat } = useSajuStore()
  const [messages, setMessages] = useState([
    { role: 'oracle', text: `${userInfo.name}님, 더 궁금하신 게 있으시면 편하게 물어보세요. 사주가 닿는 모든 것을 이야기해 드릴게요.` }
  ])
  const [input, setInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages])

  const send = async () => {
    const text = input.trim()
    if (!text || chatLoading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text }])
    setChatLoading(true)

    let reply = ''
    setMessages(m => [...m, { role: 'oracle', text: '' }])

    try {
      await streamChat(text, (token) => {
        reply += token
        setMessages(m => {
          const next = [...m]
          next[next.length - 1] = { role: 'oracle', text: reply }
          return next
        })
      })
    } catch {
      setMessages(m => {
        const next = [...m]
        next[next.length - 1] = { role: 'oracle', text: '잠시 기운이 흐려졌어요. 다시 한번 물어봐 주세요.' }
        return next
      })
    }
    setChatLoading(false)
  }

  return (
    <div className="screen active" style={{ height: '100dvh', overflow: 'hidden' }}>
      <Stars />
      <OracleSmall />
      <div ref={scrollRef} className="chat-messages" style={{ zIndex: 1 }}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-${m.role}`} style={{ maxWidth: '80%', alignSelf: m.role === 'oracle' ? 'flex-start' : 'flex-end' }}>
            <div className="chat-bubble">{m.text}</div>
          </div>
        ))}
        {chatLoading && messages[messages.length - 1]?.text === '' && (
          <div className="chat-oracle" style={{ alignSelf: 'flex-start' }}>
            <div className="chat-bubble">
              <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
            </div>
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 10, padding: '12px 16px 32px', borderTop: '1px solid var(--border)', background: 'rgba(6,3,15,0.95)', zIndex: 10 }}>
        <input
          className="chat-input"
          placeholder="무엇이든 물어보세요..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <button className="chat-send" onClick={send}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#1a0a02"><path d="M2 21L23 12 2 3v7l15 2-15 2z" /></svg>
        </button>
      </div>
      <div style={{ padding: '8px 20px 16px', textAlign: 'center', background: 'rgba(6,3,15,0.95)' }}>
        <button className="btn-ghost" onClick={onBack} style={{ fontSize: 12 }}>← 처음으로</button>
      </div>
    </div>
  )
}

// ─── Main App ────────────────────────────────────────────────────────────────
//
// 화면 흐름:
//   0 Welcome → 1 Info → 2 Loading(계산) → 3 만세력 → 4 오행(AI 동시 시작)
//   → 5 신년운세 → 6 월운 → 7 질문답변(선택) → 8 채팅
//
// AI 순서: calculate 완료 직후 analyze() 시작
//   personality → yearly → monthly(5개 병렬) → [question]
//   각 화면은 analyzing 중 로딩 표시, 결과 도착 시 자동 갱신
//
const TOTAL = 8

export default function App() {
  const [screen, setScreen] = useState(0)
  const { userInfo, setUserInfo, calculate, analyze, loading, error } = useSajuStore()

  const goTo = useCallback((n: number) => setScreen(n), [])
  const back = useCallback(() => setScreen(s => Math.max(0, s - 1)), [])

  // 1단계: 정보 입력 후 → 계산 + AI 분석 동시 시작
  const handleInfoSubmit = useCallback(async () => {
    goTo(2)                 // 로딩 화면
    await calculate()       // 만세력·오행 계산 (빠름, AI 없음)
    analyze()               // AI 분석 백그라운드 시작 (await 없음)
    goTo(3)                 // 만세력 화면으로 즉시 이동
  }, [calculate, analyze, goTo])

  const next = useCallback(() => {
    if (screen === 1) {
      handleInfoSubmit()
    } else if (screen === 6 && !useSajuStore.getState().userInfo.question.trim()) {
      goTo(8)               // 질문 없으면 QuestionScreen 건너뜀
    } else {
      setScreen(s => Math.min(TOTAL, s + 1))
    }
  }, [screen, handleInfoSubmit, goTo])

  const screens = [
    <WelcomeScreen onNext={next} />,
    <InfoScreen userInfo={userInfo} setUserInfo={setUserInfo} onNext={next} onBack={back} />,
    <LoadingScreen />,
    <ManseryeokScreen onNext={next} onBack={back} />,
    <OhaengScreen onNext={next} onBack={back} />,
    <YearlyScreen onNext={next} onBack={back} />,
    <MonthlyScreen onNext={next} onBack={back} />,
    <QuestionScreen onNext={next} onBack={back} />,
    <ChatScreen onBack={() => goTo(0)} />,
  ]

  return (
    <div className="saju-app">
      {/* 계산 실패 시 에러 배너 */}
      {error && screen === 2 && (
        <div style={{ position: 'absolute', bottom: 40, left: 20, right: 20, background: 'rgba(139,21,53,0.3)', border: '1px solid rgba(139,21,53,0.5)', borderRadius: 12, padding: '12px 16px', zIndex: 200, fontSize: 13, color: 'var(--text-dim)', textAlign: 'center' }}>
          <div>{error}</div>
          <button className="btn-ghost" style={{ marginTop: 10, fontSize: 12 }} onClick={() => goTo(1)}>← 돌아가기</button>
        </div>
      )}
      <div style={{ width: '100%', height: '100%', position: 'relative' }}>
        {screens[screen] && screens[screen]}
      </div>
    </div>
  )
}
