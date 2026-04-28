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

export interface SajuAnalysisRequest {
  birth_date:    string
  birth_time:    string
  gender:        'M' | 'F'
  calendar_type: 'solar' | 'lunar'
  question_type: '팔자' | '세운' | '월운' | '특정운' | '자유질문'
  question?:     string
  fortune_type?: '연애' | '직업' | '재물' | '건강'
}

export type QuestionType = SajuAnalysisRequest['question_type']
export type FortuneType  = NonNullable<SajuAnalysisRequest['fortune_type']>
