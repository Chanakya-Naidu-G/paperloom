from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.database.entities import Document, DocumentStatus
from app.indexing.service import IndexingService
from app.models.chunk import Chunk
from app.models.embeddedChunk import EmbeddedChunk
from app.models.indexing import IndexingResult
from app.models.retrieval import RetrievalResult
from app.vectorstore.base import VectorStore


class FakeEmbedder:

    def __init__(
        self,
        dimension: int = 4,
        model_name: str = "fake-model",
    ) -> None:

        self.config = SimpleNamespace(
            model_name=model_name,
            dimension=dimension,
        )

    def embed_chunks(
        self,
        chunks: list[Chunk],
        batch_size: int = 32,
    ) -> list[EmbeddedChunk]:

        return [
            EmbeddedChunk.from_chunk(
                chunk,
                [float(chunk.chunk_index) * 0.1] * self.config.dimension,
            )
            for chunk in chunks
        ]


class FakeVectorStore(VectorStore):

    def __init__(self) -> None:
        self._vectors: dict[str, EmbeddedChunk] = {}

    @property
    def count(self) -> int:
        return len(self._vectors)

    def add_documents(
        self,
        documents: list[EmbeddedChunk],
        batch_size: int = 100,
    ) -> None:

        for embedded_chunk in documents:
            self._vectors[embedded_chunk.chunk.chunk_id] = embedded_chunk

    def document_exists(self, document_id: str) -> bool:
        return any(
            chunk.chunk.document_id == document_id
            for chunk in self._vectors.values()
        )

    def delete_document(self, document_id: str) -> None:
        stale = [
            chunk_id
            for chunk_id, chunk in self._vectors.items()
            if chunk.chunk.document_id == document_id
        ]
        for chunk_id in stale:
            del self._vectors[chunk_id]
    def query(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:

        return []


    def get_embedding(
        self,
        chunk_id: str,
    ) -> list[float] | None:

        embedded_chunk = self._vectors.get(
            chunk_id
        )

        if embedded_chunk is None:
            return None

        return embedded_chunk.embedding

class FakeDocumentService:

    def __init__(self) -> None:
        self.transitions: list[str] = []
        self.failed_message: str | None = None

    def mark_indexing(self, document: Document) -> None:
        document.status = DocumentStatus.INDEXING
        self.transitions.append("INDEXING")

    def mark_indexed(self, document: Document) -> None:
        document.status = DocumentStatus.INDEXED
        document.indexed_at = datetime.now(timezone.utc)
        self.transitions.append("INDEXED")

    def record_embedding_metadata(
        self,
        document: Document,
        *,
        embedding_model: str,
        embedding_dimension: int,
        chunk_count: int,
    ) -> None:

        document.embedding_model = embedding_model
        document.embedding_dimension = embedding_dimension
        document.chunk_count = chunk_count

    def mark_failed(
        self,
        document: Document,
        error_message: str,
    ) -> None:

        document.status = DocumentStatus.FAILED
        document.error_message = error_message
        self.transitions.append("FAILED")
        self.failed_message = error_message


def make_document(document_id: str = "doc-1") -> Document:
    return Document(
        document_id=document_id,
        original_filename="paper.pdf",
        stored_filename="abc-paper.pdf",
        parsed_filename="abc-paper.txt",
        mime_type="application/pdf",
        file_size=100,
        file_hash="hash-1",
        page_count=1,
        character_count=100,
        chunk_count=0,
        embedding_model="",
        embedding_dimension=0,
    )


def make_chunks(
    document_id: str,
    count: int = 3,
) -> list[Chunk]:

    return [
        Chunk(
            chunk_id=f"chunk-{i}",
            document_id=document_id,
            chunk_index=i,
            section="Introduction",
            page_start=1,
            page_end=1,
            text=f"Chunk {i} text.",
            character_count=12,
            word_count=3,
        )
        for i in range(count)
    ]


def make_service(
    embedder: FakeEmbedder | None = None,
    vector_store: FakeVectorStore | None = None,
) -> tuple[IndexingService, FakeDocumentService, FakeVectorStore]:

    document_service = FakeDocumentService()
    store = vector_store or FakeVectorStore()

    service = IndexingService(
        document_service=document_service,
        embedder=embedder or FakeEmbedder(),
        vector_store=store,
    )

    return service, document_service, store


def test_indexes_document_and_updates_metadata():

    service, document_service, store = make_service()

    document = make_document()
    chunks = make_chunks(document.document_id)

    result = service.index_document(document, chunks)

    assert isinstance(result, IndexingResult)
    assert result.document_id == document.document_id
    assert result.chunk_count == len(chunks)
    assert result.embedding_model == "fake-model"
    assert result.embedding_dimension == 4

    assert store.count == len(chunks)
    assert document.status is DocumentStatus.INDEXED
    assert document.embedding_model == "fake-model"
    assert document.embedding_dimension == 4
    assert document.chunk_count == len(chunks)
    assert document_service.transitions == ["INDEXING", "INDEXED"]


def test_reindex_is_idempotent():

    service, _, store = make_service()

    document = make_document()
    chunks = make_chunks(document.document_id)

    service.index_document(document, chunks)
    first_count = store.count

    service.index_document(document, chunks)

    assert store.count == first_count


def test_rejects_empty_chunks():

    service, document_service, store = make_service()

    document = make_document()

    with pytest.raises(ValueError, match="without chunks"):
        service.index_document(document, [])

    assert store.count == 0
    assert document_service.transitions == []


def test_rejects_chunks_from_other_document():

    service, _, store = make_service()

    document = make_document("doc-1")
    chunks = make_chunks("doc-2")

    with pytest.raises(ValueError, match="different document"):
        service.index_document(document, chunks)

    assert store.count == 0


def test_rolls_back_and_marks_failed_when_store_fails():

    class FailingVectorStore(FakeVectorStore):

        def add_documents(
            self,
            documents: list[EmbeddedChunk],
            batch_size: int = 100,
        ) -> None:
            raise RuntimeError("Chroma down")

    service, document_service, store = make_service(
        vector_store=FailingVectorStore()
    )

    document = make_document()
    chunks = make_chunks(document.document_id)

    with pytest.raises(RuntimeError, match="Chroma down"):
        service.index_document(document, chunks)

    assert document.status is DocumentStatus.FAILED
    assert store.count == 0
    assert document_service.transitions == ["INDEXING", "FAILED"]
    assert "Chroma down" in document_service.failed_message


def test_rolls_back_and_marks_failed_when_existence_check_fails():

    class BrokeVectorStore(FakeVectorStore):

        def document_exists(self, document_id: str) -> bool:
            raise RuntimeError("store unavailable")

    service, document_service, store = make_service(
        vector_store=BrokeVectorStore()
    )

    document = make_document()
    chunks = make_chunks(document.document_id)

    with pytest.raises(RuntimeError, match="store unavailable"):
        service.index_document(document, chunks)

    assert document.status is DocumentStatus.FAILED
    assert document_service.transitions == ["INDEXING", "FAILED"]
    assert "store unavailable" in document_service.failed_message


def test_rejects_wrong_embedding_dimension():

    class WrongDimensionEmbedder(FakeEmbedder):

        def embed_chunks(
            self,
            chunks: list[Chunk],
            batch_size: int = 32,
        ) -> list[EmbeddedChunk]:
            return [
                EmbeddedChunk.from_chunk(chunk, [0.1, 0.2])
                for chunk in chunks
            ]

    service, document_service, store = make_service(
        embedder=WrongDimensionEmbedder(dimension=4)
    )

    document = make_document()
    chunks = make_chunks(document.document_id)

    with pytest.raises(ValueError, match="dimension"):
        service.index_document(document, chunks)

    assert document.status is DocumentStatus.FAILED
    assert store.count == 0
    assert document_service.transitions == ["INDEXING", "FAILED"]
    assert "dimension" in document_service.failed_message
