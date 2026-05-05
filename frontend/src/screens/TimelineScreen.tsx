import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore } from '../store/useSajuStore'
import { TimelineItem } from '../types/saju'

const HIGHLIGHT_STYLES: Record<TimelineItem['highlight'], { color: string; bg: string; border: string }> = {
  '연애운': { color: '#e05535', bg: 'rgba(224,85,53,0.12)',   border: 'rgba(224,85,53,0.35)'   },
  '재물운': { color: '#5588e8', bg: 'rgba(85,136,232,0.12)',  border: 'rgba(85,136,232,0.35)'  },
  '직업운': { color: '#5db85d', bg: 'rgba(93,184,93,0.12)',   border: 'rgba(93,184,93,0.35)'   },
  '사업운': { color: '#b8bcd4', bg: 'rgba(184,188,212,0.12)', border: 'rgba(184,188,212,0.35)' },
}

function SkeletonCard() {
  return (
    <div className="card" style={{ margin: '0 0 16px', opacity: 0.5 }}>
      <div style={{ height: 14, width: '40%', borderRadius: 6, background: 'rgba(255,255,255,0.08)', marginBottom: 12 }} />
      <div style={{ height: 12, width: '90%', borderRadius: 6, background: 'rgba(255,255,255,0.06)', marginBottom: 8 }} />
      <div style={{ height: 12, width: '70%', borderRadius: 6, background: 'rgba(255,255,255,0.06)' }} />
    </div>
  )
}

export function TimelineScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { timeline, loadingStep } = useSajuStore()
  const isLoading = !timeline && loadingStep === 'timeline'

  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text="앞으로 4개월의 기운을 살펴볼게요." />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">월운 타임라인</div>

          {isLoading && (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          )}

          {timeline && timeline.map((item, idx) => {
            const hl = HIGHLIGHT_STYLES[item.highlight]
            const isThisMonth = idx === 0
            return (
              <div
                key={`${item.year}-${item.month}`}
                style={{
                  marginBottom: 16,
                  borderRadius: 14,
                  border: isThisMonth
                    ? '1px solid rgba(201,146,42,0.5)'
                    : '1px solid rgba(255,255,255,0.07)',
                  background: isThisMonth
                    ? 'rgba(201,146,42,0.07)'
                    : 'rgba(255,255,255,0.03)',
                  padding: '16px 18px',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {isThisMonth && (
                  <div style={{
                    position: 'absolute', top: 10, right: 12,
                    fontSize: 10, color: 'var(--gold)',
                    fontWeight: 700, letterSpacing: 1,
                    background: 'rgba(201,146,42,0.15)',
                    padding: '2px 8px', borderRadius: 20,
                    border: '1px solid rgba(201,146,42,0.3)',
                  }}>
                    이번 달
                  </div>
                )}

                {/* 월 헤더 */}
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: 18, fontWeight: 700, color: isThisMonth ? 'var(--gold)' : 'var(--text)' }}>
                    {item.month_label}
                  </span>
                  <span style={{ fontSize: 13, color: 'var(--text-dim)', fontFamily: 'serif' }}>
                    {item.month_pillar}
                  </span>
                </div>

                {/* 총운 요약 */}
                <p style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.7, marginBottom: 12 }}>
                  {item.summary}
                </p>

                {/* 하이라이트 배지 + 내용 */}
                <div style={{
                  borderRadius: 10,
                  background: hl.bg,
                  border: `1px solid ${hl.border}`,
                  padding: '10px 14px',
                }}>
                  <div style={{
                    display: 'inline-block',
                    fontSize: 11, fontWeight: 700,
                    color: hl.color,
                    background: `${hl.bg}`,
                    border: `1px solid ${hl.border}`,
                    borderRadius: 20, padding: '2px 10px',
                    marginBottom: 8,
                  }}>
                    {item.highlight}
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.75, margin: 0 }}>
                    {item.highlight_content}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
      <BottomNav screen={6} total={9} onNext={onNext} onBack={onBack} />
    </div>
  )
}