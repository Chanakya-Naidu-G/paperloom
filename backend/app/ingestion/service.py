import json
from dataclasses import asdict
from pathlib import Path

from app.core.storage import CHUNK_DIR
from app.core.storage import PARSED_DIR
from app.ingestion.chunking.chunker import create_chunks
from app.ingestion.chunking.preprocess import preprocess_document
from app.ingestion.chunking.section_detector import detect_sections
from app.ingestion.loader import load_document
from app.models.chunk import Chunk, IngestionResult
from app.models.parsed import ParsedDocument
from app.models.storage import StoredFile


class IngestionService:

    def ingest(
        self,
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        return self._parse_and_chunk(
            stored_file,
            document_id,
        )

    def _parse_and_chunk(
        self,
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        parsed = load_document(
            str(stored_file.path),
            stored_file.path.suffix,
        )

        PARSED_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        parsed_path = (
            PARSED_DIR
            / f"{document_id}.txt"
        )

        with open(
            parsed_path,
            "w",
            encoding="utf-8",
        ) as output:

            output.write(
                parsed["text"]
            )

        parsed_document = ParsedDocument(
            pages=parsed["pages"],
            path=parsed_path,
            characters=len(parsed["text"]),
        )

        processed_document = preprocess_document(
            parsed_document
        )

        sections = detect_sections(
            processed_document
        )

        chunks = create_chunks(
            sections,
            document_id,
        )

        chunk_path = self.save_chunks(
            chunks,
            document_id,
        )

        return IngestionResult(
            parsed_document=processed_document,
            sections=sections,
            chunks=chunks,
            chunk_path=chunk_path,
        )

    def save_chunks(
        self,
        chunks: list[Chunk],
        document_id: str,
    ) -> Path:

        CHUNK_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        chunk_path = (
            CHUNK_DIR
            / f"{document_id}.json"
        )

        with open(
            chunk_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                [asdict(chunk) for chunk in chunks],
                file,
                indent=4,
                ensure_ascii=False,
            )

        return chunk_path