import { useMemo } from 'react'

function Sparks() {
  const sparks = useMemo(() => Array.from({ length: 10 }, (_, i) => ({
    id: i,
    top: (10 + Math.random() * 80) + '%',
    left: Math.random() * 100 + '%',
    d: (2 + Math.random() * 3).toFixed(1) + 's',
    delay: (Math.random() * 3).toFixed(1) + 's',
  })), [])
  return (
    <div className="oracle-particles">
      {sparks.map(s => (
        <div key={s.id} className="oracle-spark" style={{
          top: s.top, left: s.left,
          ['--d' as string]: s.d,
          ['--delay' as string]: s.delay,
        }} />
      ))}
    </div>
  )
}

export function OracleFull({ text, typing }: { text?: string; typing?: boolean }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 40, flexShrink: 0 }}>
      <div style={{ position: 'relative' }}>
        <div className="oracle-bust">
          <img src="/saju.png" alt="설아" />
          <Sparks />
        </div>
      </div>
      <div style={{ marginTop: 10, fontSize: 11, letterSpacing: 3, color: 'var(--gold)', fontFamily: 'Cinzel, serif' }}>
        ORACLE · 설아
      </div>
      {text !== undefined && (
        <div className="oracle-bubble" style={{ marginTop: 16 }}>
          <p>{text}{typing && <span className="cursor" />}</p>
        </div>
      )}
    </div>
  )
}

export function OracleSmall({ text }: { text?: string }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 14,
      padding: '16px 20px 12px', flexShrink: 0,
      borderBottom: '1px solid var(--border)',
      background: 'linear-gradient(to bottom, rgba(14,8,32,0.98) 80%, transparent)',
      position: 'sticky', top: 0, zIndex: 10,
    }}>
      <div className="oracle-ring sm">
        <div className="oracle-face"><img src="/saju.png" alt="설아" /></div>
      </div>
      <div>
        <div style={{ fontSize: 10, letterSpacing: 2, color: 'var(--gold)', fontFamily: 'Cinzel, serif', marginBottom: 3 }}>
          ORACLE · 설아
        </div>
        {text && <div className="oracle-bubble-sm">{text}</div>}
      </div>
    </div>
  )
}