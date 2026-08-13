from fastapi import FastAPI
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