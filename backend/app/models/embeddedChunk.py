from dataclasses import dataclass
from app.models.chunk import Chunk
@dataclass(slots=True, frozen=True)
class EmbeddedChunk:
    chunk: Chunk
    embedding: list[float]
    def to_chroma(self):
        return (
            self.chunk.chunk_id,
            self.embedding,
            self.chunk.text,
            {
                "document_id": self.chunk.document_id,
                "chunk_index": self.chunk.chunk_index,
                "section": self.chunk.section,
                "page_start": self.chunk.page_start,
                "page_end": self.chunk.page_end,
                "character_count": self.chunk.character_count,
                "word_count": self.chunk.word_count,
            },
        )
    @classmethod
    def from_chunk(cls, chunk: Chunk, embedding: list[float]) -> "EmbeddedChunk":
        return cls(chunk=chunk, embedding=embedding)