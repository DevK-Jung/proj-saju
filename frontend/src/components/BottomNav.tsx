export function BottomNav({
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