# PaperLoom backend

FastAPI RAG API (Python 3.12, managed with `uv`). Pipeline:
PDF upload → parse → chunk → embed (sentence-transformers) → Chroma (cosine)
→ retrieve → rerank → grounded answer (Gemini).

## Setup

```bash
uv sync --frozen              # or: pip install -r requirements.txt
cp .env.example .env          # fill in SECRET_KEY + GEMINI_API_KEY
PYTHONPATH=. uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Environment (`.env`, see `.env.example`)

| Var | Default | Notes |
|---|---|---|
| `ENV` | `development` | `production` enforces `SECRET_KEY` |
| `SECRET_KEY` | — | 64-char hex; JWT HS256 signing |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | — | generation providers |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT lifetime |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | comma-separated prod origins |
| `DATABASE_URL` | `sqlite:///./data/rag.db` | SQLAlchemy URL (Postgres-ready) |
| `VECTOR_DB_PATH` | `vector_db` | Chroma persistent dir |
| `STORAGE_ROOT` | `data` | `uploads/`, `parsed/`, `chunks/` underneath |

## API (prefix `/api/v1`)

`POST /auth/register` (201/409) · `POST /auth/login` (JWT) ·
`GET /documents` (scoped) · `GET /documents/{id}/pdf` (ownership-checked) ·
`POST /upload` (same-user dup replaces in place, cross-user coexists) ·
`POST /search` · `POST /ask` (answer + sources; `document_ids` server-side filtered).

## Data model & rules

- `User(id, username unique, hashed_password)`; `Document.user_id` nullable indexed
  (legacy rows stay hidden, never auto-claimed); `file_hash` indexed, not unique.
- Idempotent startup migrations (`app/database/migrations.py`) run before `create_all`.
- `user_id` always comes from the JWT — never from the client.

## Tests

```bash
PYTHONPATH=. uv run pytest -q   # 12 files, 103 tests
```

## Local data (git-ignored, ephemeral on free hosts)

`data/rag.db`, `vector_db/`, `data/uploads|parsed|chunks/`. Reindex helper:
`reindex_doc.py`; debug scripts: `debug_*.py`.
