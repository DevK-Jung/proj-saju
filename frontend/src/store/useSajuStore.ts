import { create } from 'zustand'
import { SajuData } from '../types/saju'

const API_BASE = '/api/v1'

export interface UserInfo {
  name:         string
  gender:       '남성' | '여성' | ''
  birthYear:    string
  birthMonth:   string
  birthDay:     string
  birthTime:    string    // Korean label e.g. "자시 (子時 23:00~01:00)" or ""
  calendar:     '양력' | '음력'
  relationship: '솔로' | '연애중' | '기혼' | ''
  question:     string    // 선택 사항
}

export interface MonthlyFortune {
  총운:  string
  연애운: string
  재물운: string
  직업운: string
  사업운: string
}

export interface AnalysisContent {
  personality: string           // 기질·성격 분석
  yearly:      string
  monthly:     MonthlyFortune | null
  answer:      string           // question_answer (없으면 "")
}

// ── 시간 변환 ────────────────────────────────────────────────────────────────

const TIME_TO_HOUR: Record<string, string> = {
  '자시': '23:00', '축시': '01:00', '인시': '03:00', '묘시': '05:00',
  '진시': '07:00', '사시': '09:00', '오시': '11:00', '미시': '13:00',
  '신시': '15:00', '유시': '17:00', '술시': '19:00', '해시': '21:00',
}

function toBirthTime(timeStr: string): string {
  if (!timeStr) return '미상'
  // 이미 HH:MM 형식이면 그대로 반환
  if (/^\d{2}:\d{2}$/.test(timeStr)) return timeStr
  // 레거시 한국어 시간 레이블 처리
  const key = timeStr.slice(0, 2)
  return TIME_TO_HOUR[key] ?? '미상'
}

function toBirthDate(ui: UserInfo): string {
  const y = ui.birthYear.padStart(4, '0')
  const m = ui.birthMonth.padStart(2, '0')
  const d = ui.birthDay.padStart(2, '0')
  return `${y}-${m}-${d}`
}

// ── SSE 파서 ─────────────────────────────────────────────────────────────────

interface SSECallbacks {
  onSajuData?:    (data: SajuData) => void
  onPersonality?: (text: string) => void
  onYearly?:      (text: string) => void
  onMonthly?:     (data: MonthlyFortune) => void
  onAnswer?:      (text: string) => void
  onDone?:        (threadId: string) => void
  onError?:       (msg: string) => void
}

async function parseSessionSSE(
  response: Response,
  callbacks: SSECallbacks,
) {
  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })

    // SSE 이벤트 단위로 분리
    const events = buf.split('\n\n')
    buf = events.pop() ?? ''

    for (const raw of events) {
      const lines = raw.split('\n')
      let eventType = ''
      let dataLine = ''
      for (const line of lines) {
        if (line.startsWith('event: ')) eventType = line.slice(7).trim()
        if (line.startsWith('data: '))  dataLine  = line.slice(6).trim()
      }
      if (!dataLine) continue

      const parsed = JSON.parse(dataLine)

      if      (eventType === 'saju_data')   callbacks.onSajuData?.(parsed as SajuData)
      else if (eventType === 'personality') callbacks.onPersonality?.(parsed as string)
      else if (eventType === 'yearly')      callbacks.onYearly?.(parsed as string)
      else if (eventType === 'monthly')     callbacks.onMonthly?.(parsed as MonthlyFortune)
      else if (eventType === 'answer')      callbacks.onAnswer?.(parsed as string)
      else if (eventType === 'done')        callbacks.onDone?.((parsed as { thread_id: string }).thread_id)
      else if (eventType === 'error')       callbacks.onError?.(parsed as string)
    }
  }
}

// ── Store ────────────────────────────────────────────────────────────────────

interface SajuStore {
  userInfo:   UserInfo
  threadId:   string | null
  sajuData:   SajuData | null
  content:    AnalysisContent | null
  loading:    boolean      // 1단계 계산 로딩
  analyzing:  boolean      // 2단계 AI 분석 로딩
  error:      string | null

  setUserInfo: (u: Partial<UserInfo>) => void
  calculate:   () => Promise<void>                                      // 1단계: 만세력·오행 계산
  analyze:     () => Promise<void>                                      // 2단계: AI 운세 분석
  streamChat:  (message: string, onToken: (t: string) => void) => Promise<void>
  reset:       () => void
}

const defaultUserInfo: UserInfo = {
  name: '', gender: '', birthYear: '', birthMonth: '', birthDay: '',
  birthTime: '', calendar: '양력', relationship: '', question: '',
}

export const useSajuStore = create<SajuStore>((set, get) => ({
  userInfo:  defaultUserInfo,
  threadId:  null,
  sajuData:  null,
  content:   null,
  loading:   false,
  analyzing: false,
  error:     null,

  setUserInfo: (u) => set((s) => ({ userInfo: { ...s.userInfo, ...u } })),

  // ── 1단계: 만세력·오행 순수 계산 (AI 없음) ────────────────────────────────
  calculate: async () => {
    const ui = get().userInfo
    set({ loading: true, error: null, sajuData: null, content: null, threadId: null })

    const body = {
      birth_date:    toBirthDate(ui),
      birth_time:    toBirthTime(ui.birthTime),
      gender:        ui.gender === '남성' ? 'M' : 'F',
      calendar_type: ui.calendar === '음력' ? 'lunar' : 'solar',
    }

    try {
      const response = await fetch(`${API_BASE}/saju/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!response.ok) throw new Error(`서버 오류: ${response.status}`)
      const json = await response.json()
      if (!json.success) throw new Error(json.message || '계산 오류')
      set({ sajuData: json.data })
    } catch (e: unknown) {
      set({ error: e instanceof Error ? e.message : '계산 중 오류가 발생했습니다' })
    } finally {
      set({ loading: false })
    }
  },

  // ── 2단계: AI 운세 분석 (만세력·오행 화면 통과 후 호출) ──────────────────
  analyze: async () => {
    const ui      = get().userInfo
    const sajuData = get().sajuData
    if (!sajuData) return

    set({ analyzing: true, error: null })

    const body = {
      saju_data:     sajuData,
      name:          ui.name,
      gender:        ui.gender === '남성' ? 'M' : 'F',
      birth_date:    toBirthDate(ui),
      birth_time:    toBirthTime(ui.birthTime),
      calendar_type: ui.calendar === '음력' ? 'lunar' : 'solar',
      relationship:  ui.relationship,
      question:      ui.question,
    }

    try {
      const response = await fetch(`${API_BASE}/saju/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!response.ok) throw new Error(`서버 오류: ${response.status}`)

      const partial: AnalysisContent = { personality: '', yearly: '', monthly: null, answer: '' }

      await parseSessionSSE(response, {
        onPersonality: (text) => { partial.personality = text; set({ content: { ...partial } }) },
        onYearly:      (text) => { partial.yearly      = text; set({ content: { ...partial } }) },
        onMonthly:     (data) => { partial.monthly     = data; set({ content: { ...partial } }) },
        onAnswer:      (text) => { partial.answer      = text; set({ content: { ...partial } }) },
        onDone:        (tid)  => set({ threadId: tid }),
        onError:       (msg)  => set({ error: msg }),
      })
    } catch (e: unknown) {
      set({ error: e instanceof Error ? e.message : 'AI 분석 중 오류가 발생했습니다' })
    } finally {
      set({ analyzing: false })
    }
  },

  streamChat: async (message: string, onToken: (t: string) => void) => {
    const threadId = get().threadId
    if (!threadId) {
      onToken('세션이 만료되었습니다. 처음부터 다시 시작해주세요.')
      return
    }

    try {
      const response = await fetch(`${API_BASE}/saju/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, message }),
      })

      if (!response.ok) throw new Error(`서버 오류: ${response.status}`)

      const reader = response.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const text = line.slice(6)
          if (text === '[DONE]' || text.startsWith('[ERROR]')) break
          onToken(text)
        }
      }
    } catch (e: unknown) {
      onToken('잠시 기운이 흐려졌어요. 다시 한번 물어봐 주세요.')
    }
  },

  reset: () => set({
    sajuData: null, content: null, error: null,
    threadId: null, loading: false, analyzing: false,
    userInfo: defaultUserInfo,
  }),
}))
