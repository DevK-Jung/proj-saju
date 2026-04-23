import { useState } from 'react'
import { useSajuStore } from '../store/useSajuStore'
import { QuestionType, FortuneType } from '../types/saju'

const TABS: { key: QuestionType; label: string }[] = [
  { key: '팔자',   label: '타고난 팔자' },
  { key: '세운',   label: '올해 세운' },
  { key: '월운',   label: '이번달 월운' },
  { key: '특정운', label: '특정운' },
  { key: '자유질문', label: '자유 질문' },
]

const FORTUNE_TYPES: FortuneType[] = ['연애', '직업', '재물', '건강']

export function FortuneTab() {
  const { sajuData, activeTab, setActiveTab, answer, loading, streamAnalyze } = useSajuStore()
  const [fortuneType, setFortuneType] = useState<FortuneType>('연애')
  const [question, setQuestion] = useState('')

  if (!sajuData) return null

  const handleAnalyze = async () => {
    await streamAnalyze({
      question_type: activeTab,
      question: activeTab === '자유질문' ? question : undefined,
      fortune_type: activeTab === '특정운' ? fortuneType : undefined,
    })
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-purple-100 overflow-hidden">
      {/* 탭 헤더 */}
      <div className="flex border-b border-gray-100 overflow-x-auto">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors
              ${activeTab === key
                ? 'border-b-2 border-purple-600 text-purple-700 bg-purple-50'
                : 'text-gray-500 hover:text-gray-700'}`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="p-5">
        {/* 특정운 선택 */}
        {activeTab === '특정운' && (
          <div className="flex gap-2 mb-4 flex-wrap">
            {FORTUNE_TYPES.map((ft) => (
              <button
                key={ft}
                onClick={() => setFortuneType(ft)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors
                  ${fortuneType === ft
                    ? 'bg-purple-600 text-white border-purple-600'
                    : 'border-gray-200 text-gray-600 hover:border-purple-400'}`}
              >
                {ft}
              </button>
            ))}
          </div>
        )}

        {/* 자유질문 입력 */}
        {activeTab === '자유질문' && (
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="사주에 관해 궁금한 것을 자유롭게 질문해보세요..."
            className="w-full border border-gray-200 rounded-xl p-3 text-sm resize-none h-24
                       focus:outline-none focus:ring-2 focus:ring-purple-400 mb-4"
          />
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading || (activeTab === '자유질문' && !question.trim())}
          className="w-full bg-purple-600 text-white py-2.5 rounded-xl font-semibold
                     hover:bg-purple-700 active:scale-95 transition-all
                     disabled:opacity-40 disabled:cursor-not-allowed mb-4"
        >
          {loading ? '해석 중...' : '해석하기'}
        </button>

        {/* 결과 */}
        {answer && (
          <div className="bg-purple-50 rounded-xl p-4 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
            {answer}
          </div>
        )}
      </div>
    </div>
  )
}
