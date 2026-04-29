import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { BottomNav } from '../components/BottomNav'
import { useSajuStore } from '../store/useSajuStore'

export function ManseryeokScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
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