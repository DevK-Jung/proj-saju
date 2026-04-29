import { create } from 'zustand'
import { SajuData } from '../types/saju'

const API_BASE = '/api/v1'

export interface UserInfo {
  name:         string
  gender:       '남성' | '여성' | ''
  birthYear:    string
  birthMonth:   string
  birthDay:     string
  birthTime:    string    // "HH:MM" (오전·오후 변환 후) | "" (모름)
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
  yearly:      string           // 신년운세
  monthly:     MonthlyFortune | null
  answer:      string           // 질문 답변 (없으면 "")
}

// 로딩 진행 단계
export type LoadingStep =
  | 'idle'
  | 'calculating'   // 만세력·오행 계산 중
  | 'personality'   // 기질 분석 중
  | 'yearly'        // 신년운세 분석 중
  | 'monthly'       // 이번달 운세 분석 중
  | 'question'      // 질문 답변 중
  | 'done'

// ── 시간 변환 ─────────────────────────────────────────────────────────────────

function toBirthTime(timeStr: string): string {
  if (!timeStr) return '미상'
  if (/^\d{2}:\d{2}$/.test(timeStr)) return timeStr
  return '미상'
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

async function parseSessionSSE(response: Response, callbacks: SSECallbacks) {
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE는 빈 줄(\n\n)로 이벤트 단위를 구분함
        const events = buffer.split('\n\n');
        // 마지막 미완성 조각은 버퍼에 남겨둠
        buffer = events.pop() ?? '';

        for (const event of events) {
            if (!event.trim()) continue;

            const lines = event.split('\n');
            let eventType = '';
            let dataBuffer = '';

            for (const line of lines) {
                if (line.startsWith('event:')) {
                    eventType = line.replace('event:', '').trim();
                } else if (line.startsWith('data:')) {
                    // data: 가 여러 줄 올 경우를 대비해 합쳐줌
                    dataBuffer += line.replace('data:', '').trim();
                }
            }

            if (!dataBuffer) continue;

            try {
                // 1. JSON 파싱 시도
                let parsedData;
                try {
                    parsedData = JSON.parse(dataBuffer);
                } catch {
                    // 2. 만약 순수 문자열이면 그대로 사용
                    parsedData = dataBuffer;
                }

                // 이벤트 타입별 콜백 실행
                switch (eventType) {
                    case 'saju_data':
                        callbacks.onSajuData?.(parsedData);
                        break;
                    case 'personality':
                        callbacks.onPersonality?.(parsedData);
                        break;
                    case 'yearly':
                        callbacks.onYearly?.(parsedData);
                        break;
                    case 'monthly':
                        callbacks.onMonthly?.(parsedData);
                        break;
                    case 'answer':
                        callbacks.onAnswer?.(parsedData);
                        break;
                    case 'done':
                        // thread_id가 객체로 오는지 확인 필요
                        const tid = typeof parsedData === 'object' ? parsedData.thread_id : parsedData;
                        callbacks.onDone?.(tid);
                        break;
                    case 'error':
                        callbacks.onError?.(parsedData);
                        break;
                }
            } catch (err) {
                console.error('SSE Parsing Error:', err, dataBuffer);
            }
        }
    }
}

// ── Store ────────────────────────────────────────────────────────────────────

interface SajuStore {
  userInfo:    UserInfo
  threadId:    string | null
  sajuData:    SajuData | null
  content:     AnalysisContent | null
  loading:     boolean        // 세션 전체 로딩 중
  loadingStep: LoadingStep    // 로딩 단계 (LoadingScreen 진행 표시용)
  error:       string | null

  setUserInfo:   (u: Partial<UserInfo>) => void
  startSession:  () => Promise<void>    // /session 호출 — 그래프 전체 실행
  streamChat:    (message: string, onToken: (t: string) => void) => Promise<void>
  reset:         () => void
}

const defaultUserInfo: UserInfo = {
  name: '', gender: '', birthYear: '', birthMonth: '', birthDay: '',
  birthTime: '', calendar: '양력', relationship: '', question: '',
}

export const useSajuStore = create<SajuStore>((set, get) => ({
  userInfo:    defaultUserInfo,
  threadId:    null,
  sajuData:    null,
  content:     null,
  loading:     false,
  loadingStep: 'idle',
  error:       null,

  setUserInfo: (u) => set((s) => ({ userInfo: { ...s.userInfo, ...u } })),

  // ── /session: 그래프 전체 실행 (calculate → personality → yearly → monthly) ──
  startSession: async () => {
    const ui = get().userInfo
    set({ loading: true, loadingStep: 'calculating', error: null,
          sajuData: null, content: null, threadId: null })

    const body = {
      birth_date:    toBirthDate(ui),
      birth_time:    toBirthTime(ui.birthTime),
      gender:        ui.gender === '남성' ? 'M' : 'F',
      calendar_type: ui.calendar === '음력' ? 'lunar' : 'solar',
      name:          ui.name,
      relationship:  ui.relationship,
      question:      ui.question,
    }

    try {
      const response = await fetch(`${API_BASE}/saju/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!response.ok) throw new Error(`서버 오류: ${response.status}`)

      const partial: AnalysisContent = { personality: '', yearly: '', monthly: null, answer: '' }

      await parseSessionSSE(response, {
        onSajuData:    (data) => {
          set({ sajuData: data, loadingStep: 'personality' })
        },
        onPersonality: (text) => {
          partial.personality = text
          set({ content: { ...partial }, loadingStep: 'yearly' })
        },
        onYearly:      (text) => {
          partial.yearly = text
          set({ content: { ...partial }, loadingStep: 'monthly' })
        },
        onMonthly:     (data) => {
          partial.monthly = data
          set({ content: { ...partial }, loadingStep: 'question' })
        },
        onAnswer:      (text) => {
          partial.answer = text
          set({ content: { ...partial } })
        },
        onDone:        (tid)  => set({ threadId: tid, loadingStep: 'done' }),
        onError:       (msg)  => set({ error: msg }),
      })
    } catch (e: unknown) {
      set({ error: e instanceof Error ? e.message : '분석 중 오류가 발생했습니다' })
    } finally {
      set({ loading: false })
    }
  },

  // ── 채팅 ─────────────────────────────────────────────────────────────────────
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
    } catch {
      onToken('잠시 기운이 흐려졌어요. 다시 한번 물어봐 주세요.')
    }
  },

  reset: () => set({
    sajuData: null, content: null, error: null,
    threadId: null, loading: false, loadingStep: 'idle',
    userInfo: defaultUserInfo,
  }),
}))
