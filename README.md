# PaperLoom — Research, organized

PaperLoom is a private, per-user RAG workspace: upload PDFs, ask questions, and get
grounded answers with page-level citations. Each user's documents are fully isolated —
same PDF re-uploaded by the same user **replaces** in place; across users it coexists.

## Monorepo layout

```
PaperLoom
├── backend/            FastAPI RAG API (Python 3.12, uv-managed)
│   ├── app/
│   │   ├── api/routes/ ask, auth, documents, search, upload (all under /api/v1)
│   │   ├── auth/       bcrypt hashing, JWT (HS256) issue/verify, HTTPBearer guard
│   │   ├── database/   SQLAlchemy models (User, Document), repository, service,
│   │   │               idempotent startup migrations
│   │   ├── ingestion/  PDF load → parse → chunk (sections, pages)
│   │   ├── indexing/ + embeddings/ + vectorstore/  embed → Chroma (cosine)
│   │   ├── retrieval/ + generation/ + context/     retrieve → rerank → grounded answer
│   │   ├── services/   upload_service, document_processing_service
│   │   ├── core/storage.py  uploads/parsed/chunks dirs (STORAGE_ROOT, default data/)
│   │   └── main.py     CORS (env-driven), router wiring
│   └── tests/          12 pytest files, 103 tests
├── frontend/           Next.js 16 + React 19 + Tailwind + Zustand + motion
│   └── src/
│       ├── app/        / (landing), /login, /workspace
│       ├── components/
│       │   ├── chat/       ConversationHistory, ConversationMessage (Markdown+GFM),
│       │   │               QuestionComposer, ConversationHeader
│       │   ├── workspace/  AppHeader, UserMenu (layoutId morph), DocumentExplorer,
│       │   │               ContextPanel, DocumentViewerPanel, ResearchWorkspace, ThemeToggle
│       │   └── ui/         AnimatedReveal, MorphIcon, JumpingDots, MotionProvider (+ shadcn)
│       ├── lib/api.ts  API_BASE_URL (NEXT_PUBLIC_API_URL), auth headers, error mapping
│       ├── services/   authService, documentService, chatServices
│       ├── store/      useAuthStore (persisted paperloom-auth), useDocumentStore (upsert),
│       │               useChatStore, usePdfStore
│       └── types/      chat, citation, document
├── PROGRESS.txt        build log: what was implemented + verified
├── PAPERLOOM_TODO.md   feature checklist (priorities 0–8, all checked)
└── backend/.env.example   all backend env vars (copy to backend/.env, never commit secrets)
```

## Quickstart

### Backend

```bash
uv sync --frozen            # in backend/ (or: pip install -r requirements.txt)
cp .env.example .env        # then fill in SECRET_KEY + GEMINI_API_KEY
PYTHONPATH=. uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
npm install                 # in frontend/
npm run dev                 # http://localhost:3000
```

Point the frontend at the API via `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Tests / checks

```bash
PYTHONPATH=. uv run pytest -q   # backend/ → 103 passed
npm run lint && npm run build   # frontend/ → exit 0, 4 routes
```

## API (base `/api/v1`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/register` | no | 201 / 409 username taken |
| POST | `/auth/login` | no | JWT, 10080 min expiry |
| GET | `/documents` | yes | only current user's docs |
| GET | `/documents/{id}/pdf` | yes | ownership-checked |
| POST | `/upload` | yes | same-user dup → replace in place |
| POST | `/search` | yes | `document_ids` server-side filtered |
| POST | `/ask` | yes | grounded answer + sources |

## Environment

Backend (`backend/.env`, see `.env.example`): `ENV`, `SECRET_KEY` (required when
`ENV=production`), `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
`CORS_ORIGINS`, `DATABASE_URL` (default `sqlite:///./data/rag.db`), `VECTOR_DB_PATH`.
Frontend: `NEXT_PUBLIC_API_URL`. Secrets are git-ignored and never reach the browser
bundle (only the JWT in `localStorage:paperloom-auth`).

## Deploy notes

Frontend → Vercel Hobby (root `frontend`, set `NEXT_PUBLIC_API_URL`).
Backend → Render Free web service (root `backend`, set `ENV=production`,
`SECRET_KEY`, `GEMINI_API_KEY`, `CORS_ORIGINS=https://<app>.vercel.app`).
Heads-up: free tiers have **ephemeral disks** — `data/rag.db`, `vector_db/` and
uploads reset on restart; plan Postgres/object storage before real users.
