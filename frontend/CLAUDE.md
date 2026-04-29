# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # TypeScript check + Vite production build
npm run preview  # Preview production build locally
```

No test or lint scripts are configured.

## Architecture

### Single-file UI with Zustand state

All screens are defined in `src/App.tsx` (~880 lines). Navigation is state-driven — a single `screen` integer (0–8) controls which screen renders. There is no router.

**Screen flow:**
```
0: Welcome → 1: User Info Input → 2: Loading (SSE) → 3: 만세력 (Pillars) →
4: 오행 분석 (Five Elements) → 5: 신년운세 (Yearly) → 6: 이번달 (Monthly) →
7: Q&A → 8: Chat
```

### State management (`src/store/useSajuStore.ts`)

Zustand store holds all user input, session results, and async logic. Two key async methods:

- `startSession()` — POSTs to `/api/v1/saju/session`, reads SSE stream. Events arrive in order: `saju_data` → `personality` → `yearly` → `monthly` → `answer` → `done`. Updates `loadingStep` at each stage for the loading screen progress bar.
- `streamChat(message, onToken)` — POSTs to `/api/v1/saju/chat` with `thread_id`, streams response tokens via callback.

### Backend proxy

Vite proxies `/api/*` to `http://localhost:8000` in dev. The backend must be running for any API calls to work.

### Types (`src/types/saju.ts`)

All backend contract types live here. Key types:
- `SajuData` — four pillars (year/month/day/hour) + ohaeng scores + fortune pillars
- `Pillar` — a single pillar with Chinese char, Korean reading, and five-element classification
- `AnalysisContent` — AI-generated text for personality, yearly, monthly (structured), and Q&A answer
- `CalculateRequest` / `AnalyzeRequest` / `ChatRequest` — API payloads

### Styling

Dark mystical theme with CSS variables in `src/index.css`. Key vars: `--gold`, `--crimson`, `--purple`, `--bg`, `--text`. Mobile-optimized at 430px max-width. Tailwind used for layout; custom CSS handles animations (`twinkle`, `spark`, `halo`, `float`, `shimmer`).