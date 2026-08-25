from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.ask import router as ask_router
from app.api.routes.search import router as search_router
from app.api.routes.upload import router as upload_router
from app.database.connection import Base, engine

from app.database import entities

from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="ChatPDF RAG Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://172.16.101.78:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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