import { useSajuStore } from '../store/useSajuStore'

export function BirthForm() {
  const { birthForm, setBirthForm, analyze, loading } = useSajuStore()

  const handleSubmit = async () => {
    await analyze({ question_type: '팔자' })
  }

  return (
    <div className="p-6 bg-white rounded-2xl shadow-lg border border-purple-100 overflow-hidden">
      <h2 className="text-xl font-bold text-purple-800 mb-5">🔮 사주 정보 입력</h2>

      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2 sm:col-span-1">
          <label className="block text-sm font-medium text-gray-600 mb-1">생년월일</label>
          <input
            type="date"
            value={birthForm.birth_date}
            onChange={(e) => setBirthForm({ birth_date: e.target.value })}
            className="w-full border border-gray-200 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
        </div>

        <div className="col-span-2 sm:col-span-1">
          <label className="block text-sm font-medium text-gray-600 mb-1">태어난 시간</label>
          <input
            type="time"
            value={birthForm.birth_time}
            onChange={(e) => setBirthForm({ birth_time: e.target.value })}
            className="w-full border border-gray-200 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">성별</label>
          <select
            value={birthForm.gender}
            onChange={(e) => setBirthForm({ gender: e.target.value as 'M' | 'F' })}
            className="w-full border border-gray-200 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-purple-400"
          >
            <option value="M">남성</option>
            <option value="F">여성</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">양력 / 음력</label>
          <select
            value={birthForm.calendar_type}
            onChange={(e) => setBirthForm({ calendar_type: e.target.value as 'solar' | 'lunar' })}
            className="w-full border border-gray-200 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-purple-400"
          >
            <option value="solar">양력</option>
            <option value="lunar">음력</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !birthForm.birth_date}
        className="w-full mt-5 bg-purple-600 text-white py-3 rounded-xl font-bold text-lg
                   hover:bg-purple-700 active:scale-95 transition-all
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? '분석 중...' : '사주 분석하기'}
      </button>
    </div>
  )
}
