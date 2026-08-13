from dataclasses import dataclass
from pathlib import Path

from app.models.parsed import ParsedDocument
from app.models.section import DocumentSection


@dataclass(slots=True, frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    section: str
    page_start: int
    page_end: int
    text: str
    character_count: int
    word_count: int


@dataclass(slots=True, frozen=True)
class IngestionResult:
    parsed_document: ParsedDocument
    sections: list[DocumentSection]
    chunks: list[Chunk]
    chunk_path: Path