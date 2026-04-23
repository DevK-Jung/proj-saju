import { BirthForm } from '../components/BirthForm'
import { SajuChart } from '../components/SajuChart'
import { FortuneTab } from '../components/FortuneTab'
import { ChatBox } from '../components/ChatBox'
import { useSajuStore } from '../store/useSajuStore'

export function SajuPage() {
  const { error, sajuData } = useSajuStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-900 to-indigo-950 py-8 px-4">
      <div className="max-w-2xl mx-auto space-y-5">
        {/* 헤더 */}
        <div className="text-center py-4">
          <h1 className="text-3xl font-bold text-white tracking-tight">🔮 사주 AI</h1>
          <p className="text-purple-300 text-sm mt-1">천간지지 기반 AI 사주 분석 서비스</p>
        </div>

        {/* 에러 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
            오류: {error}
          </div>
        )}

        {/* 입력 폼 */}
        <BirthForm />

        {/* 사주팔자 차트 */}
        {sajuData && <SajuChart />}

        {/* 운세 탭 */}
        {sajuData && <FortuneTab />}

        {/* 채팅 */}
        {sajuData && <ChatBox />}
      </div>
    </div>
  )
}
