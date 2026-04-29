import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore } from '../store/useSajuStore'
import { useTypewriter } from '../hooks/useTypewriter'

export function QuestionScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
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