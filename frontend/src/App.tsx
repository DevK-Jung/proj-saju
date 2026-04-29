import { useState, useCallback } from 'react'
import { useSajuStore } from './store/useSajuStore'

import { WelcomeScreen }    from './screens/WelcomeScreen'
import { InfoScreen }       from './screens/InfoScreen'
import { LoadingScreen }    from './screens/LoadingScreen'
import { ManseryeokScreen } from './screens/ManseryeokScreen'
import { OhaengScreen }     from './screens/OhaengScreen'
import { YearlyScreen }     from './screens/YearlyScreen'
import { MonthlyScreen }    from './screens/MonthlyScreen'
import { QuestionScreen }   from './screens/QuestionScreen'
import { ChatScreen }       from './screens/ChatScreen'

// 화면 흐름:
//   0 Welcome → 1 Info → 2 Loading(세션 SSE) → 3 만세력
//   → 4 오행 → 5 신년운세 → 6 월운 → 7 질문답변(선택) → 8 채팅
const TOTAL = 8

export default function App() {
  const [screen, setScreen] = useState(0)
  const { userInfo, setUserInfo, startSession, error } = useSajuStore()

  const goTo = useCallback((n: number) => setScreen(n), [])
  const back = useCallback(() => setScreen(s => Math.max(0, s - 1)), [])

  const handleInfoSubmit = useCallback(async () => {
    goTo(2)
    await startSession()
    if (!useSajuStore.getState().error) goTo(3)
  }, [startSession, goTo])

  const next = useCallback(() => {
    if (screen === 1) {
      handleInfoSubmit()
    } else if (screen === 6 && !useSajuStore.getState().userInfo.question.trim()) {
      goTo(8)   // 질문 없으면 QuestionScreen 건너뜀
    } else {
      setScreen(s => Math.min(TOTAL, s + 1))
    }
  }, [screen, handleInfoSubmit, goTo])

  const screens = [
    <WelcomeScreen onNext={next} />,
    <InfoScreen userInfo={userInfo} setUserInfo={setUserInfo} onNext={next} onBack={back} />,
    <LoadingScreen />,
    <ManseryeokScreen onNext={next} onBack={back} />,
    <OhaengScreen onNext={next} onBack={back} />,
    <YearlyScreen onNext={next} onBack={back} />,
    <MonthlyScreen onNext={next} onBack={back} />,
    <QuestionScreen onNext={next} onBack={back} />,
    <ChatScreen onBack={() => goTo(0)} />,
  ]

  return (
    <div className="saju-app">
      {error && screen === 2 && (
        <div style={{
          position: 'absolute', bottom: 40, left: 20, right: 20,
          background: 'rgba(139,21,53,0.3)', border: '1px solid rgba(139,21,53,0.5)',
          borderRadius: 12, padding: '12px 16px', zIndex: 200,
          fontSize: 13, color: 'var(--text-dim)', textAlign: 'center',
        }}>
          <div>{error}</div>
          <button className="btn-ghost" style={{ marginTop: 10, fontSize: 12 }} onClick={() => goTo(1)}>← 다시 입력하기</button>
        </div>
      )}
      <div style={{ width: '100%', height: '100%', position: 'relative' }}>
        {screens[screen]}
      </div>
    </div>
  )
}