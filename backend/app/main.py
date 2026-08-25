from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.ask import router as ask_router
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.api.routes.upload import router as upload_router
from app.database.connection import Base, engine
from app.database.migrations import run_startup_migrations

from app.database import entities

from dotenv import load_dotenv
import os

load_dotenv()

run_startup_migrations(engine)

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="ChatPDF RAG Backend",
    version="1.0.0",
)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
_allow_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
)

app.include_router(
    upload_router,
    prefix="/api/v1",
)

app.include_router(
    search_router,
    prefix="/api/v1",
)

app.include_router(
    ask_router,
    prefix="/api/v1",
)

@app.get("/")
async def root():

    return {
        "status": "running",
        "message": "ChatPDF RAG Backend is up!",
    }