import logging

from app.database.entities import Document
from app.database.service import DocumentService
from app.embeddings.embedder import Embedder
from app.models.chunk import Chunk
from app.models.embeddedChunk import EmbeddedChunk
from app.models.indexing import IndexingResult
from app.vectorstore.base import VectorStore

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 32
VECTOR_BATCH_SIZE = 100


class IndexingService:

    def __init__(
        self,
        document_service: DocumentService,
        embedder: Embedder,
        vector_store: VectorStore,
    ) -> None:

        self._document_service = document_service
        self._embedder = embedder
        self._vector_store = vector_store

    def index_document(
        self,
        document: Document,
        chunks: list[Chunk],
    ) -> IndexingResult:

        self._validate_chunks(document, chunks)

        self._document_service.mark_indexing(document)

        try:
            if self._vector_store.document_exists(document.document_id):
                self._vector_store.delete_document(document.document_id)

            embedded_chunks = self._embedder.embed_chunks(
                chunks,
                batch_size=EMBED_BATCH_SIZE,
            )

            self._validate_embeddings(embedded_chunks)

            self._vector_store.add_documents(
                embedded_chunks,
                batch_size=VECTOR_BATCH_SIZE,
            )

        except Exception as exc:
            self._handle_failure(document, exc)
            raise

        self._document_service.record_embedding_metadata(
            document,
            embedding_model=self._embedder.config.model_name,
            embedding_dimension=self._embedder.config.dimension,
            chunk_count=len(embedded_chunks),
        )

        self._document_service.mark_indexed(document)

        return IndexingResult(
            document_id=document.document_id,
            chunk_count=len(embedded_chunks),
            embedding_model=self._embedder.config.model_name,
            embedding_dimension=self._embedder.config.dimension,
        )

    def _validate_chunks(
        self,
        document: Document,
        chunks: list[Chunk],
    ) -> None:

        if not chunks:
            raise ValueError(
                "Cannot index a document without chunks."
            )

        for chunk in chunks:
            if chunk.document_id != document.document_id:
                raise ValueError(
                    "Chunk belongs to a different document."
                )

    def _validate_embeddings(
        self,
        embedded_chunks: list[EmbeddedChunk],
    ) -> None:

        expected_dimension = self._embedder.config.dimension

        for embedded_chunk in embedded_chunks:
            if len(embedded_chunk.embedding) != expected_dimension:
                raise ValueError(
                    f"Embedding dimension {len(embedded_chunk.embedding)} "
                    f"does not match expected dimension {expected_dimension}."
                )

    def _handle_failure(
        self,
        document: Document,
        exc: Exception,
    ) -> None:

        logger.exception(
            "Indexing failed for document %s; rolling back vectors.",
            document.document_id,
        )

        try:
            self._vector_store.delete_document(document.document_id)
        except Exception:
            logger.exception(
                "Failed to remove partial vectors for document %s.",
                document.document_id,
            )

        self._document_service.mark_failed(
            document,
            error_message=str(exc)[:512],
        )
