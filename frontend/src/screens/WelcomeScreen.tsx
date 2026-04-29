import { Stars } from '../components/Stars'
import { OracleFull } from '../components/Oracle'
import { useTypewriter } from '../hooks/useTypewriter'

export function WelcomeScreen({ onNext }: { onNext: () => void }) {
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