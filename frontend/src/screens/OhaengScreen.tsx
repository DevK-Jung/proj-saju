import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore } from '../store/useSajuStore'
import { SajuData } from '../types/saju'

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

export function OhaengScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { sajuData, userInfo, content, loading } = useSajuStore()
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

          <div className="card">
            <div className="card-title">타고난 기질 · 성격</div>
            {loading && !content?.personality
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