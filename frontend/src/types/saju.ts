export interface Pillar {
  gan: string
  zhi: string
  gan_kr: string
  zhi_kr: string
  gan_wuxing: string
  zhi_wuxing: string
  sipsung: string
}

export interface OhaengScores {
  wood:  number  // 木 count (0~8)
  fire:  number  // 火 count
  earth: number  // 土 count
  metal: number  // 金 count
  water: number  // 水 count
}

export interface SajuData {
  year_pillar:     Pillar
  month_pillar:    Pillar
  day_pillar:      Pillar
  hour_pillar:     Pillar
  day_gan:         string
  day_gan_wuxing:  string
  yearly_fortune:  Pillar
  monthly_fortune: Pillar
  daeun:           Pillar[]
  daeun_start_age: number
  ohaeng_scores:   OhaengScores  // 백엔드 계산 (AI 없음)
}

// ── API 요청 타입 ─────────────────────────────────────────────────────────────

export interface CalculateRequest {
  birth_date:    string        // "YYYY-MM-DD"
  birth_time:    string        // "HH:MM" | "미상"
  gender:        'M' | 'F'
  calendar_type: 'solar' | 'lunar'
  city:          string | null // 출생지 도시명 (진태양시 보정), 모르면 null
}

export interface AnalyzeRequest extends CalculateRequest {
  saju_data:    SajuData      // /calculate 결과
  name:         string
  relationship: '솔로' | '연애중' | '기혼' | ''
  question:     string
}

export interface ChatRequest {
  thread_id: string
  message:   string
}
