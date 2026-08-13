from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.service import DocumentService
from app.embeddings.embedder import Embedder
from app.indexing.service import IndexingService
from app.ingestion.service import IngestionService
from app.retrieval.service import RetrievalService
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.services.upload_service import UploadService
from app.vectorstore.base import VectorStore
from app.vectorstore.chroma import ChromaDB

from app.context.builder import ContextBuilder
from app.generation.client import GeminiClient
from app.generation.generator import AnswerGenerator

def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:

    return DocumentService(db)


def get_ingestion_service() -> IngestionService:

    return IngestionService()


def get_embedder() -> Embedder:

    return Embedder()


def get_vector_store() -> VectorStore:

    return ChromaDB()


def get_indexing_service(
    document_service: DocumentService = Depends(
        get_document_service
    ),
    embedder: Embedder = Depends(
        get_embedder
    ),
    vector_store: VectorStore = Depends(
        get_vector_store
    ),
) -> IndexingService:

    return IndexingService(
        document_service=document_service,
        embedder=embedder,
        vector_store=vector_store,
    )


def get_document_processing_service(
    document_service: DocumentService = Depends(
        get_document_service
    ),
    ingestion_service: IngestionService = Depends(
        get_ingestion_service
    ),
    indexing_service: IndexingService = Depends(
        get_indexing_service
    ),
) -> DocumentProcessingService:

    return DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )


def get_upload_service(
    document_processing_service: DocumentProcessingService = Depends(
        get_document_processing_service
    ),
) -> UploadService:

    return UploadService(
        document_processing_service
    )


def get_retrieval_service(
    embedder: Embedder = Depends(
        get_embedder
    ),
    vector_store: VectorStore = Depends(
        get_vector_store
    ),
) -> RetrievalService:

    return RetrievalService(
        embedder=embedder,
        vector_store=vector_store,
    )
def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


def get_generation_client() -> GeminiClient:
    return GeminiClient()


def get_answer_generator(
    client: GeminiClient = Depends(
        get_generation_client
    ),
    context_builder: ContextBuilder = Depends(
        get_context_builder
    ),
) -> AnswerGenerator:

    return AnswerGenerator(
        client=client,
        context_builder=context_builder,
    )