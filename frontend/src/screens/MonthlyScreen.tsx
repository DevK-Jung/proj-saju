import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore, MonthlyFortune } from '../store/useSajuStore'

const MONTHLY_CATS: { key: keyof MonthlyFortune; icon: string; color: string; bg: string }[] = [
  { key: '총운',  icon: '✦', color: '#c9922a', bg: 'rgba(201,146,42,0.1)' },
  { key: '연애운', icon: '♥', color: '#e05535', bg: 'rgba(224,85,53,0.1)'  },
  { key: '재물운', icon: '◉', color: '#5588e8', bg: 'rgba(85,136,232,0.1)' },
  { key: '직업운', icon: '◈', color: '#5db85d', bg: 'rgba(93,184,93,0.1)'  },
  { key: '사업운', icon: '◆', color: '#b8bcd4', bg: 'rgba(184,188,212,0.1)'},
]

export function MonthlyScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { content } = useSajuStore()
  const month = new Date().getMonth() + 1
  const monthly = content?.monthly

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
                <p style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                  {monthly?.[cat.key] || '—'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
      <BottomNav screen={5} total={8} onNext={onNext} onBack={onBack} />
    </div>
  )
}