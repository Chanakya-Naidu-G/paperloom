from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class IndexingResult:
    document_id: str
    chunk_count: int
    embedding_model: str
    embedding_dimension: int
