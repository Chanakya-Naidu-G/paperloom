from abc import ABC, abstractmethod

from app.models.embeddedChunk import EmbeddedChunk
from app.models.retrieval import RetrievalResult


class VectorStore(ABC):

    @abstractmethod
    def add_documents(
        self,
        documents: list[EmbeddedChunk],
        batch_size: int = 100,
    ) -> None:
        pass

    @abstractmethod
    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        pass

    @abstractmethod
    def delete_document(
        self,
        document_id: str,
    ) -> None:
        pass
    @abstractmethod
    def query(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:
        pass
    @abstractmethod
    def get_embedding(
        self,
        chunk_id: str,
    ) -> list[float] | None:
        pass