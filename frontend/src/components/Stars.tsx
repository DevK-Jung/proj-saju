import { useMemo } from 'react'

export function Stars() {
  const stars = useMemo(() => Array.from({ length: 60 }, (_, i) => ({
    id: i,
    size: Math.random() * 2 + 0.5,
    top: Math.random() * 100,
    left: Math.random() * 100,
    d: (Math.random() * 4 + 2).toFixed(1) + 's',
    delay: (Math.random() * 4).toFixed(1) + 's',
    op: (Math.random() * 0.5 + 0.2).toFixed(2),
  })), [])
  return (
    <div className="stars">
      {stars.map(s => (
        <div key={s.id} className="star" style={{
          width: s.size, height: s.size,
          top: s.top + '%', left: s.left + '%',
          ['--d' as string]: s.d,
          ['--delay' as string]: s.delay,
          ['--op' as string]: s.op,
        }} />
      ))}
    </div>
  )
}