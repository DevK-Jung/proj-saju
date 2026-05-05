import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore } from '../store/useSajuStore'

export function ManseryeokScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { sajuData } = useSajuStore()

  const pillars = sajuData ? [
    { name: '년주', pillar: sajuData.year_pillar  },
    { name: '월주', pillar: sajuData.month_pillar },
    { name: '일주', pillar: sajuData.day_pillar   },
    { name: '시주', pillar: sajuData.hour_pillar  },
  ] : null

  return (
    <div className="screen active">
      <Stars />
      <OracleSmall text="사주 팔자를 펼쳐보겠습니다." />
      <div className="scroll-inner" style={{ zIndex: 1 }}>
        <div className="content-area" style={{ paddingTop: 24 }}>
          <div className="section-title">사주 팔자 만세력</div>
          {pillars ? (
            <div className="pillars">
              {pillars.map(({ name, pillar }) => (
                <div key={name} className="pillar">
                  <div className="pillar-name">{name}</div>
                  <div style={{ fontSize: 10, color: 'var(--crimson)', marginBottom: 4 }}>{pillar.sipsung}</div>
                  <div className="pillar-stem" style={{ color: 'var(--gold-l)' }}>{pillar.gan}</div>
                  <div className="pillar-label">{pillar.gan_kr}</div>
                  <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.7 }}>{pillar.gan_wuxing}</div>
                  <div style={{ width: 1, height: 12, background: 'var(--border)', margin: '4px auto' }} />
                  <div className="pillar-branch">{pillar.zhi}</div>
                  <div className="pillar-label">{pillar.zhi_kr}</div>
                  <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.7 }}>{pillar.zhi_wuxing}</div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '24px 0' }}>데이터를 불러오는 중...</div>
          )}

          {sajuData && (
            <>
              <div className="card">
                <div className="card-title">세운 (올해 운)</div>
                <div style={{ display: 'flex', gap: 20, marginTop: 4 }}>
                  {[
                    { label: '세운 (년)', fortune: sajuData.yearly_fortune },
                    { label: '월운 (월)', fortune: sajuData.monthly_fortune },
                  ].map(({ label, fortune }) => (
                    <div key={label}>
                      <div style={{ fontSize: 11, color: 'var(--text-dim)', marginBottom: 6 }}>{label}</div>
                      <div style={{ fontSize: 10, color: 'var(--crimson)', marginBottom: 2 }}>{fortune.sipsung}</div>
                      <div style={{ fontSize: 22, color: 'var(--gold-l)' }}>{fortune.gan}</div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>{fortune.gan_kr} · {fortune.gan_wuxing}</div>
                      <div style={{ fontSize: 18, color: 'var(--text-dim)', marginTop: 6 }}>{fortune.zhi}</div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>{fortune.zhi_kr} · {fortune.zhi_wuxing}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card">
                <div className="card-title">대운</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {sajuData.daeun.map((d, i) => (
                    <div key={i} style={{ textAlign: 'center', padding: '8px 10px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', borderRadius: 8 }}>
                      <div style={{ fontSize: 9, color: 'var(--crimson)', marginBottom: 2 }}>{d.sipsung}</div>
                      <div style={{ fontSize: 14, color: 'var(--gold-l)' }}>{d.gan}</div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.7 }}>{d.gan_wuxing}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 4 }}>{d.zhi}</div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.7 }}>{d.zhi_wuxing}</div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', opacity: 0.5, marginTop: 4 }}>
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
      <BottomNav screen={2} total={9} onNext={onNext} onBack={onBack} />
    </div>
  )
}