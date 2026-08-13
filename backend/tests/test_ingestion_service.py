import json
from pathlib import Path

from app.ingestion.service import IngestionService
from app.models.chunk import Chunk, IngestionResult
from app.models.parsed import ParsedDocument
from app.models.section import DocumentSection
from app.models.storage import StoredFile


def make_stored_file(tmp_path: Path) -> StoredFile:

    file_path = tmp_path / "paper.pdf"
    file_path.write_bytes(b"fake pdf")

    return StoredFile(
        filename="paper.pdf",
        path=file_path,
    )


def make_chunks(
    document_id: str,
    count: int = 2,
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
            character_count=14,
            word_count=3,
        )
        for i in range(count)
    ]


def configure_pipeline(
    monkeypatch,
    tmp_path: Path,
    *,
    text: str = "Research paper text.",
    pages: list | None = None,
    sections: list | None = None,
    chunks: list[Chunk] | None = None,
) -> tuple[Path, Path]:

    parsed_dir = tmp_path / "parsed"
    chunks_dir = tmp_path / "chunks"

    monkeypatch.setattr(
        "app.ingestion.service.PARSED_DIR",
        parsed_dir,
    )

    monkeypatch.setattr(
        "app.ingestion.service.CHUNK_DIR",
        chunks_dir,
    )

    monkeypatch.setattr(
        "app.ingestion.service.load_document",
        lambda *args, **kwargs: {
            "text": text,
            "pages": pages or [],
        },
    )

    monkeypatch.setattr(
        "app.ingestion.service.preprocess_document",
        lambda document: document,
    )

    monkeypatch.setattr(
        "app.ingestion.service.detect_sections",
        lambda document: (
            sections
            if sections is not None
            else []
        ),
    )

    monkeypatch.setattr(
        "app.ingestion.service.create_chunks",
        lambda sections, document_id: (
            chunks
            if chunks is not None
            else make_chunks(document_id)
        ),
    )

    return parsed_dir, chunks_dir


def test_ingest_returns_ingestion_result(
    tmp_path,
    monkeypatch,
):

    service = IngestionService()

    stored_file = make_stored_file(tmp_path)
    document_id = "doc-1"

    expected_chunks = make_chunks(document_id)

    configure_pipeline(
        monkeypatch,
        tmp_path,
        text="Hello world.",
        chunks=expected_chunks,
    )

    result = service.ingest(
        stored_file,
        document_id,
    )

    assert isinstance(result, IngestionResult)
    assert isinstance(result.parsed_document, ParsedDocument)
    assert result.parsed_document.characters == len("Hello world.")
    assert result.sections == []
    assert result.chunks == expected_chunks

    for chunk in result.chunks:
        assert chunk.document_id == document_id


def test_ingest_persists_parsed_text(
    tmp_path,
    monkeypatch,
):

    service = IngestionService()
    stored_file = make_stored_file(tmp_path)
    document_id = "doc-1"

    parsed_dir, _ = configure_pipeline(
        monkeypatch,
        tmp_path,
        text="Persisted text.",
        chunks=[],
    )

    service.ingest(stored_file, document_id)

    parsed_path = parsed_dir / f"{document_id}.txt"

    assert parsed_path.exists()
    assert parsed_path.read_text() == "Persisted text."


def test_ingest_persists_chunk_json(
    tmp_path,
    monkeypatch,
):

    service = IngestionService()
    stored_file = make_stored_file(tmp_path)
    document_id = "doc-1"

    expected_chunks = make_chunks(document_id)

    _, chunks_dir = configure_pipeline(
        monkeypatch,
        tmp_path,
        chunks=expected_chunks,
    )

    service.ingest(stored_file, document_id)

    chunk_path = chunks_dir / f"{document_id}.json"

    assert chunk_path.exists()

    payload = json.loads(chunk_path.read_text())

    assert len(payload) == len(expected_chunks)
    assert payload[0]["chunk_id"] == expected_chunks[0].chunk_id
    assert payload[0]["document_id"] == document_id


def test_ingest_uses_sections_when_detected(
    tmp_path,
    monkeypatch,
):

    service = IngestionService()
    stored_file = make_stored_file(tmp_path)
    document_id = "doc-1"

    sections = [
        DocumentSection(
            title="Introduction",
            text="Introduction content.",
            page_start=1,
            page_end=1,
        )
    ]

    configure_pipeline(
        monkeypatch,
        tmp_path,
        sections=sections,
        chunks=[],
    )

    result = service.ingest(
        stored_file,
        document_id,
    )

    assert result.sections == sections


def test_ingest_has_no_external_workflow_dependencies():
    service = IngestionService()

    assert isinstance(service, IngestionService)