import { Stars } from '../components/Stars'
import { useSajuStore, LoadingStep } from '../store/useSajuStore'

const LOADING_STEPS: { step: LoadingStep; label: string }[] = [
  { step: 'calculating', label: '사주팔자·오행 계산 중' },
  { step: 'personality', label: '타고난 기질 분석 중'  },
  { step: 'yearly',      label: '신년운세 분석 중'     },
  { step: 'monthly',     label: '이번달 운세 분석 중'  },
  { step: 'question',    label: '질문 답변 생성 중'    },
  { step: 'done',        label: '완료'                },
]

const STEP_ORDER: LoadingStep[] = ['calculating', 'personality', 'yearly', 'monthly', 'question', 'done']

export function LoadingScreen() {
  const { loadingStep } = useSajuStore()
  const currentIdx = Math.max(0, STEP_ORDER.indexOf(loadingStep))
  const total = STEP_ORDER.length - 1
  const progress = Math.round((currentIdx / total) * 100)

  return (
    <div className="screen active">
      <Stars />
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', height: '100%', gap: 28, padding: '40px 32px', zIndex: 1,
      }}>
        <div className="oracle-ring lg">
          <div className="oracle-face"><img src="/saju.png" alt="설아" /></div>
        </div>

        <div className="loading-orb" />

        <div style={{ width: '100%', maxWidth: 280 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: 13, color: 'var(--gold)' }}>사주를 읽고 있습니다</span>
            <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>{progress}%</span>
          </div>

          <div style={{
            height: 4, borderRadius: 4,
            background: 'rgba(255,255,255,0.08)',
            overflow: 'hidden', marginBottom: 16,
          }}>
            <div style={{
              height: '100%', borderRadius: 4,
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #8b1535, #c9922a)',
              transition: 'width 0.6s ease',
            }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {LOADING_STEPS.filter(s => s.step !== 'done').map(({ step, label }, i) => {
              const done   = i < currentIdx
              const active = i === currentIdx
              return (
                <div key={step} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  opacity: done ? 0.5 : active ? 1 : 0.3,
                  transition: 'opacity 0.4s',
                }}>
                  <div style={{
                    width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10,
                    background: done   ? 'rgba(93,184,93,0.3)'   :
                                active ? 'rgba(201,146,42,0.3)'  :
                                         'rgba(255,255,255,0.06)',
                    border: `1px solid ${
                      done   ? '#5db85d' :
                      active ? 'var(--gold)' :
                               'rgba(255,255,255,0.1)'}`,
                    color: done ? '#5db85d' : active ? 'var(--gold)' : 'var(--text-dim)',
                  }}>
                    {done ? '✓' : i + 1}
                  </div>
                  <span style={{
                    fontSize: 13,
                    color: active ? 'var(--gold)' : 'var(--text-dim)',
                    fontWeight: active ? 600 : 400,
                  }}>
                    {label}
                    {active && <span className="cursor" style={{ marginLeft: 2 }} />}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}