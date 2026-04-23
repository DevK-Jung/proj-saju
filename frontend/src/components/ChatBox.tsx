import { useState } from 'react'
import { useSajuStore } from '../store/useSajuStore'

export function ChatBox() {
  const { sajuData, loading, streamAnalyze } = useSajuStore()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; text: string }[]>([])

  if (!sajuData) return null

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const q = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: q }])

    // 임시 AI 응답 자리 확보
    setMessages((prev) => [...prev, { role: 'ai', text: '' }])

    await streamAnalyze({ question_type: '자유질문', question: q })

    // Zustand answer를 마지막 AI 메시지에 반영
    const { answer } = useSajuStore.getState()
    setMessages((prev) => {
      const updated = [...prev]
      updated[updated.length - 1] = { role: 'ai', text: answer }
      return updated
    })
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-purple-100 flex flex-col h-96">
      <div className="px-5 py-3 border-b border-gray-100">
        <h3 className="font-bold text-purple-800 text-sm">💬 사주 채팅</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-8">
            사주에 대해 무엇이든 물어보세요
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap
              ${msg.role === 'user'
                ? 'bg-purple-600 text-white rounded-br-none'
                : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}
            >
              {msg.text || (loading && msg.role === 'ai' ? '...' : '')}
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-gray-100 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="질문을 입력하세요..."
          className="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-purple-400"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-purple-600 text-white px-4 py-2 rounded-xl text-sm font-medium
                     hover:bg-purple-700 disabled:opacity-40 transition-colors"
        >
          전송
        </button>
      </div>
    </div>
  )
}
