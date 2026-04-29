import { useState, useEffect, useRef } from 'react'
import { Stars } from '../components/Stars'
import { OracleSmall } from '../components/Oracle'
import { useSajuStore } from '../store/useSajuStore'

export function ChatScreen({ onBack }: { onBack: () => void }) {
  const { userInfo, streamChat } = useSajuStore()
  const [messages, setMessages] = useState([
    { role: 'oracle', text: `${userInfo.name}님, 더 궁금하신 게 있으시면 편하게 물어보세요. 사주가 닿는 모든 것을 이야기해 드릴게요.` }
  ])
  const [input, setInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages])

  const send = async () => {
    const text = input.trim()
    if (!text || chatLoading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text }])
    setChatLoading(true)

    let reply = ''
    setMessages(m => [...m, { role: 'oracle', text: '' }])

    try {
      await streamChat(text, (token) => {
        reply += token
        setMessages(m => {
          const next = [...m]
          next[next.length - 1] = { role: 'oracle', text: reply }
          return next
        })
      })
    } catch {
      setMessages(m => {
        const next = [...m]
        next[next.length - 1] = { role: 'oracle', text: '잠시 기운이 흐려졌어요. 다시 한번 물어봐 주세요.' }
        return next
      })
    }
    setChatLoading(false)
  }

  return (
    <div className="screen active" style={{ height: '100dvh', overflow: 'hidden' }}>
      <Stars />
      <OracleSmall />
      <div ref={scrollRef} className="chat-messages" style={{ zIndex: 1 }}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-${m.role}`} style={{ maxWidth: '80%', alignSelf: m.role === 'oracle' ? 'flex-start' : 'flex-end' }}>
            <div className="chat-bubble">{m.text}</div>
          </div>
        ))}
        {chatLoading && messages[messages.length - 1]?.text === '' && (
          <div className="chat-oracle" style={{ alignSelf: 'flex-start' }}>
            <div className="chat-bubble">
              <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
            </div>
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 10, padding: '12px 16px 32px', borderTop: '1px solid var(--border)', background: 'rgba(6,3,15,0.95)', zIndex: 10 }}>
        <input
          className="chat-input"
          placeholder="무엇이든 물어보세요..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <button className="chat-send" onClick={send}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#1a0a02"><path d="M2 21L23 12 2 3v7l15 2-15 2z" /></svg>
        </button>
      </div>
      <div style={{ padding: '8px 20px 16px', textAlign: 'center', background: 'rgba(6,3,15,0.95)' }}>
        <button className="btn-ghost" onClick={onBack} style={{ fontSize: 12 }}>← 처음으로</button>
      </div>
    </div>
  )
}