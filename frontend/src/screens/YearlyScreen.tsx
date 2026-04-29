import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore } from '../store/useSajuStore'

export function YearlyScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { content, userInfo } = useSajuStore()
  const year = new Date().getFullYear()
  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text={`${year}년 ${userInfo.name}님의 운세입니다.`} />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">{year}년 신년운세</div>
          <div className="card">
            <p style={{ whiteSpace: 'pre-line', lineHeight: 1.9 }}>{content?.yearly || '—'}</p>
          </div>
        </div>
      </div>
      <BottomNav screen={4} total={8} onNext={onNext} onBack={onBack} />
    </div>
  )
}