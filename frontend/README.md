# PaperLoom frontend

Next.js 16 + React 19 workspace UI (Tailwind CSS 4, Zustand, `motion`).
Routes: `/` landing → `/login` (login/register + light/dark toggle) → `/workspace`
(documents · chat with Markdown+GFM + citation cards · context panel · PDF viewer).

## Setup

```bash
npm install
npm run dev        # http://localhost:3000
npm run lint       # eslint, must be exit 0
npm run build      # production build (/, /_not-found, /login, /workspace)
npm start          # serve production build
```

## Environment

| Var | Default | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` | backend base; set in `.env.local` / Vercel project settings |

Only `NEXT_PUBLIC_API_URL` is public. No AI keys, JWT secrets, or private URLs in
the bundle — all AI calls go through the backend with `Authorization: Bearer <JWT>`.
Browser storage is just `localStorage: paperloom-auth` (+ `theme`).

## Structure (`src/`)

- `app/` — `page.tsx` (landing), `login/page.tsx`, `workspace/page.tsx` (auth guard + hydration)
- `components/chat/` — `ConversationHistory`, `ConversationMessage`, `QuestionComposer`, `ConversationHeader`
- `components/workspace/` — `AppHeader`, `UserMenu` (avatar↔menu `layoutId` morph),
  `DocumentExplorer`, `ContextPanel`, `DocumentViewerPanel`, `ResearchWorkspace`, `ThemeToggle`
- `components/ui/` — Motion primitives `AnimatedReveal` (height-auto reveal),
  `MorphIcon` (icon morph), `JumpingDots` (loading dots), `MotionProvider`
  (`reducedMotion="user"`) + shadcn (`button`, `card`, `input`, `textarea`, `scroll-area`, `sheet`)
- `lib/api.ts` — base URL, `getAuthHeaders()`, friendly `extractErrorMessage()`
- `services/` — `authService`, `documentService`, `chatServices`
- `store/` — `useAuthStore` (persisted), `useDocumentStore` (upsert), `useChatStore`, `usePdfStore`

## Deploy (Vercel)

Import the repo, set **Root Directory = `frontend`**, add `NEXT_PUBLIC_API_URL`
pointing at the backend (`https://<api>.onrender.com/api/v1`). No other config needed.
