# PaperLoom TODO

## Priority 0 — Functional / security fixes

- [x] Fix logout redirect
  - [x] Logout must clear auth state/token.
  - [x] Immediately redirect to `/login` without requiring a manual refresh.
  - [x] Prevent access to `/workspace` after logout, including browser back navigation.
  - [x] Verify `/workspace` redirects unauthenticated users consistently.

- [x] Security leak audit
  - [x] Search the frontend and backend for hard-coded secrets, API keys, tokens, passwords, and private URLs.
  - [x] Confirm `.env` and secret values are ignored by Git and are not tracked.
  - [x] Verify JWT secret is never exposed to the frontend.
  - [x] Verify API responses do not expose stack traces, internal filesystem paths, database details, or raw exception objects.
  - [x] Verify authentication is required on every user-specific document/search/ask endpoint.
  - [x] Verify `user_id` is always derived from the authenticated user, never trusted from the client.
  - [x] Verify document IDs from the client are server-side authorized against the current user's documents.
  - [x] Verify cross-user access cannot be achieved by modifying document IDs, conversation IDs, or request payloads.
  - [x] Review CORS configuration and restrict allowed origins for production.
  - [x] Verify password hashing uses bcrypt correctly and plaintext passwords are never stored/logged.
  - [x] Verify JWT expiry and invalid/expired token handling.

- [x] Multi-user isolation testing
  - [x] Create User A and User B.
  - [x] Upload documents as User A; confirm only User A can list/view/search/ask over them.
  - [x] Upload documents as User B; confirm User A cannot access them.
  - [x] Attempt forged `document_ids` from the other user; expect server-side filtering/rejection.
  - [x] Confirm same PDF can coexist for different users.
  - [x] Confirm re-uploading the same PDF by the same user replaces the old document correctly.
  - [x] Confirm logout/login switches the visible document set correctly.
  - [x] Confirm stale Zustand/localStorage auth state cannot expose another user's documents.
  - [x] Confirm browser back/refresh after logout does not reveal protected data.

## Priority 1 — Chat UX / rendering

- [x] Fix chat rendering
  - [x] Render assistant Markdown instead of displaying raw Markdown syntax.
  - [x] Support headings, bold/italic, bullet lists, numbered lists, inline code, and fenced code blocks.
  - [x] Improve assistant-message typography and spacing.
  - [x] Improve message bubble width and wrapping on desktop/tablet/mobile.
  - [x] Improve source/citation rendering into readable citation items/cards.
  - [x] Preserve source metadata and page references.
  - [x] Verify long AI answers do not overflow the conversation area.
  - [x] Verify very long user questions wrap correctly.

## Priority 2 — Authentication UI

- [x] Enhance login page UI
  - [x] Improve visual hierarchy, spacing, typography, and form styling.
  - [x] Improve loading state while logging in.
  - [x] Improve validation and error-state presentation.
  - [x] Add show/hide password control if appropriate.
  - [x] Make the page responsive and consistent with PaperLoom's dark theme.

- [x] Enhance register page UI
  - [x] Match login page visual system.
  - [x] Improve username/password validation feedback.
  - [x] Improve loading and error states.
  - [x] Add polished success/redirect behavior.

## Priority 3 — Animations / polish

- [x] Add subtle, purposeful animations
  - [x] Login/register page entrance animation.
  - [x] Form/error/success transitions.
  - [x] Mobile document drawer slide-in/out.
  - [x] Mobile context drawer slide-in/out.
  - [x] Backdrop fade transitions.
  - [x] Document selection transition.
  - [x] Upload progress/loading transition.
  - [x] Chat message appearance animation.
  - [x] Avoid excessive animation or delays; respect reduced-motion preferences.

## Priority 4 — Upload / document UX

- [x] Keep upload errors user-friendly; never show raw JSON.
- [x] Verify duplicate upload behavior:
  - [x] Same user + same file hash → replace existing document.
  - [x] Different user + same file hash → allow coexistence.
- [x] Improve upload loading state and disable conflicting actions while uploading.
- [x] Confirm document list updates immediately after upload/replace.

## Priority 5 — Context / viewer UX

- [x] Continue polishing Context Panel after its rendering fix.
- [x] Mount/verify DocumentViewerPanel when it is integrated into the workspace.
- [x] Verify PDF/page navigation and responsive behavior once mounted.

## Priority 6 — Final QA / regression

- [x] Run backend test suite after every auth/data-model change.
- [x] Run frontend `npm run build`.
- [x] Run frontend lint.
- [x] Test at viewport widths: 1440, 1200, 1024, 900, 765, 375.
- [x] Test empty, loading, success, duplicate, unauthorized, and server-error states.
- [x] Test fresh browser session and existing localStorage session.
- [x] Test logout → immediate redirect → protected-route guard.
- [x] Test User A/User B isolation end-to-end.
- [x] Review network requests for accidental secret/token leakage.
- [x] Final Git checkpoint before deployment.

## Priority 7 — Theme & Client-Side Security (2026-08-25)

- [x] Login Page Theme Toggle
  - [x] Add Light/Dark switch to login/register page matching workspace `ThemeToggle.tsx:16` behavior (localStorage `theme`, `document.documentElement.classList`, `dark` class, default dark).
  - [x] Persist theme when navigating between `/login` and `/workspace` (shared `localStorage` key `theme`).
  - [x] Persist after page refresh (inline script in `layout.tsx:32` applies saved theme before hydration, `suppressHydrationWarning`).
  - [x] Verify via `npm run build` (no FOUC, no hydration mismatch).

- [x] Audit client-side secret exposure using DevTools — verify API keys and private environment variables are never present in bundles, source maps, browser storage, cookies, request headers, query parameters, or responses; confirm all third-party API calls requiring secrets are routed through the backend.
  - [x] Verified `NEXT_PUBLIC_*` in `frontend/src`: only `NEXT_PUBLIC_API_URL` (`lib/api.ts:2`) — no `NEXT_PUBLIC_GEMINI_API_KEY`/`HF_TOKEN`/`SECRET_KEY`/`API_KEY` (grep `NEXT_PUBLIC.*GEMINI|HF|SECRET|API_KEY` → 0).
  - [x] Verified `GEMINI`/`AIza`/`SECRET_KEY`/`HF_TOKEN` not in `frontend/src` (grep → 0; only `backend/.env` and `backend/app`).
  - [x] Verified frontend never calls Gemini/HF directly — all `fetch` in `frontend/src` target `${API_BASE_URL}/auth|/documents|/upload|/ask` (`services/*.ts`) → Browser `JWT` → FastAPI → Gemini/HF.
  - [x] Verified frontend storage: `localStorage` only `paperloom-auth` (`{token,username}`, JWT is expected) and `theme` (`ThemeToggle.tsx:16,20`, `lib/api.ts:12`, `useAuthStore.ts:45`, `layout.tsx:32`); `sessionStorage` 0, `cookies` 0 in `frontend/src` (grep `localStorage|sessionStorage|cookie` → only those).
  - [x] Verified Network: `Authorization: Bearer <JWT>` only (`lib/api.ts:51`); no `x-api-key`, `?key=AIza`, or Gemini token in headers/query.
  - [x] Verified `.gitignore` ignores secrets: `frontend/.gitignore` `.env*`, `backend/.gitignore` `.env`, `/.gitignore` `.env`/`.env.*` (`!.env.example`); `git ls-files` shows only `backend/.env.example`, `backend/.env` ignored (`git check-ignore -v` confirms).
  - [x] Verified `.next` bundles contain no secrets: `grep -R GEMINI|AIza frontend/.next` → 0; `strings frontend/.next/static/chunks/*.js | grep -i AIza` → 0.
  - [x] Verified backend does not leak secrets: `SECRET_KEY`/`GEMINI_API_KEY` only in `backend/app/auth/security.py:11`/`generation/client.py:13` server-side, never returned in `auth.py`/`documents.py`/`search.py`/`ask.py` responses (only `access_token` JWT); error detail sanitized (`upload_service` generic 500, no path leak).
  - [x] Manual DevTools checklist documented: Network → no Gemini/HF key, Storage → Local `paperloom-auth`+`theme` only, Session `empty`, Cookies `none`, Debugger global search `AIza|GEMINI|SECRET_KEY|HF_TOKEN` → 0 in `frontend/src`, Source Maps → only frontend source (no secrets).

## Priority 8 — Motion animations (2026-09-08)

- [x] Install `motion` (motion/react) + global `MotionProvider` (`reducedMotion="user"`)
- [x] Template 1 ConditionalField → `AnimatedReveal` (height-auto reveal): login field/server errors, explorer/history upload errors, workspace amber banner
- [x] Template 2 UserButton → `MorphIcon` (layoutId morph + blur) + `UserMenu` (avatar↔menu morph): ThemeToggle, Eye/EyeOff, composer send, login heading swap, doc selection indicator, viewer page fade, drawers/modal with AnimatePresence exits
- [x] Template 3 Jumping dots → `JumpingDots`: login submit, explorer uploads, history empty upload, summarize, viewer load, workspace hydration
- [x] Press micro-interactions (`whileTap`) + focus-visible rings on all buttons; landing CTA hover/arrow
- [x] `npm run build` + `npm run lint` clean

## Constraints / invariants

- Preserve `rag.db`, `vector_db`, and existing embeddings.
- Do not change the existing retrieval → reranking → context pipeline unless a separate task explicitly requires it.
- Preserve per-user document isolation.
- Keep same-user duplicate upload behavior as replace-in-place.
- Do not commit secrets or production credentials.
