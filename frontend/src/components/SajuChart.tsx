import { Pillar } from '../types/saju'
import { useSajuStore } from '../store/useSajuStore'

const WUXING_COLOR: Record<string, string> = {
  木: 'bg-green-100 text-green-800 border-green-200',
  火: 'bg-red-100 text-red-800 border-red-200',
  土: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  金: 'bg-gray-100 text-gray-700 border-gray-200',
  水: 'bg-blue-100 text-blue-800 border-blue-200',
}

function PillarCard({ label, pillar }: { label: string; pillar: Pillar }) {
  const ganColor = WUXING_COLOR[pillar.gan_wuxing] ?? 'bg-purple-50 text-purple-800 border-purple-200'
  const zhiColor = WUXING_COLOR[pillar.zhi_wuxing] ?? 'bg-purple-50 text-purple-800 border-purple-200'
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-xs text-gray-500 font-medium">{label}</span>
      <div className={`w-14 h-14 rounded-xl border flex flex-col items-center justify-center font-bold ${ganColor}`}>
        <span className="text-2xl leading-none">{pillar.gan}</span>
        <span className="text-[10px] mt-0.5">{pillar.gan_kr}</span>
      </div>
      <div className={`w-14 h-14 rounded-xl border flex flex-col items-center justify-center font-bold ${zhiColor}`}>
        <span className="text-2xl leading-none">{pillar.zhi}</span>
        <span className="text-[10px] mt-0.5">{pillar.zhi_kr}</span>
      </div>
      {pillar.sipsung && (
        <span className="text-xs text-purple-600 font-semibold">{pillar.sipsung}</span>
      )}
    </div>
  )
}

export function SajuChart() {
  const { sajuData } = useSajuStore()
  if (!sajuData) return null

  return (
    <div className="p-5 bg-white rounded-2xl shadow-lg border border-purple-100">
      <h3 className="font-bold text-purple-800 mb-4 text-sm uppercase tracking-wide">사주팔자</h3>
      <div className="flex justify-around mb-4">
        <PillarCard label="년주" pillar={sajuData.year_pillar} />
        <PillarCard label="월주" pillar={sajuData.month_pillar} />
        <PillarCard label="일주" pillar={sajuData.day_pillar} />
        <PillarCard label="시주" pillar={sajuData.hour_pillar} />
      </div>
      <div className="border-t border-gray-100 pt-4 flex justify-around">
        <PillarCard label="세운" pillar={sajuData.yearly_fortune} />
        <PillarCard label="월운" pillar={sajuData.monthly_fortune} />
        <div className="flex flex-col items-center justify-center">
          <span className="text-xs text-gray-500 font-medium mb-1">일간</span>
          <div className={`w-14 h-14 rounded-xl border flex flex-col items-center justify-center font-bold
            ${WUXING_COLOR[sajuData.day_gan_wuxing] ?? 'bg-purple-50'}`}>
            <span className="text-2xl">{sajuData.day_gan}</span>
            <span className="text-[10px]">{sajuData.day_gan_wuxing}</span>
          </div>
        </div>
      </div>

      {/* 대운 */}
      <div className="mt-4 border-t border-gray-100 pt-4">
        <p className="text-xs text-gray-500 font-medium mb-2">대운 흐름 (대운시작 {sajuData.daeun_start_age}세)</p>
        <div className="flex gap-1.5 flex-wrap">
          {sajuData.daeun.slice(0, 8).map((d, i) => (
            <span
              key={i}
              className={`text-xs px-2 py-1 rounded-lg border ${WUXING_COLOR[d.gan_wuxing] ?? 'bg-gray-50'}`}
            >
              {d.gan}{d.zhi}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
