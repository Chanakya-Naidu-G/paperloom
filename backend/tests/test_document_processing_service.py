from pathlib import Path
from unittest.mock import Mock

import pytest

from app.database.entities import Document, DocumentStatus
from app.database.service import DocumentService
from app.indexing.service import IndexingService
from app.ingestion.service import IngestionService
from app.models.chunk import Chunk, IngestionResult
from app.models.parsed import ParsedDocument
from app.models.storage import StoredFile
from app.services.document_processing_service import (
    DocumentProcessingService,
)


def make_document_service() -> Mock:

    service = Mock(
        spec=DocumentService
    )

    def create_document(
        document: Document,
    ) -> Document:

        if not document.document_id:
            document.document_id = "doc-1"

        return document

    def mark_parsed(
        document: Document,
    ) -> Document:

        document.status = DocumentStatus.PARSED
        return document

    def mark_chunked(
        document: Document,
    ) -> Document:

        document.status = DocumentStatus.CHUNKED
        return document

    def mark_failed(
        document: Document,
        error_message: str,
    ) -> Document:

        document.status = DocumentStatus.FAILED
        document.error_message = error_message
        return document

    service.create_document.side_effect = (
        create_document
    )

    service.mark_parsed.side_effect = (
        mark_parsed
    )

    service.mark_chunked.side_effect = (
        mark_chunked
    )

    service.mark_failed.side_effect = (
        mark_failed
    )

    return service


def make_indexing_service() -> Mock:

    service = Mock(
        spec=IndexingService
    )

    def index_document(
        document: Document,
        chunks: list[Chunk],
    ) -> None:

        document.status = DocumentStatus.INDEXED

    service.index_document.side_effect = (
        index_document
    )

    return service


def make_ingestion_service() -> Mock:

    return Mock(
        spec=IngestionService
    )


def make_stored_file(
    tmp_path: Path,
) -> StoredFile:

    path = tmp_path / "abc-paper.pdf"

    path.write_bytes(
        b"fake pdf"
    )

    return StoredFile(
        filename="abc-paper.pdf",
        path=path,
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
            character_count=14,
            word_count=3,
        )
        for i in range(count)
    ]


def make_result(
    tmp_path: Path,
    document_id: str,
    page_count: int = 5,
    character_count: int = 500,
) -> IngestionResult:

    parsed_path = (
        tmp_path / "parsed.txt"
    )

    parsed_document = ParsedDocument(
        pages=[None] * page_count,
        path=parsed_path,
        characters=character_count,
    )

    chunks = make_chunks(
        document_id
    )

    return IngestionResult(
        parsed_document=parsed_document,
        sections=[],
        chunks=chunks,
        chunk_path=tmp_path / "chunks.json",
    )


def make_service(
    tmp_path: Path,
    ingestion_service: Mock | None = None,
) -> tuple[
    DocumentProcessingService,
    Mock,
    Mock,
    Mock,
]:

    document_service = (
        make_document_service()
    )

    indexing_service = (
        make_indexing_service()
    )

    ingestion_service = (
        ingestion_service
        or make_ingestion_service()
    )

    service = DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )

    return (
        service,
        document_service,
        ingestion_service,
        indexing_service,
    )


def test_process_stored_file_success(
    tmp_path,
):

    document_service = (
        make_document_service()
    )

    ingestion_service = (
        make_ingestion_service()
    )

    indexing_service = (
        make_indexing_service()
    )

    stored_file = make_stored_file(
        tmp_path
    )

    def ingest(
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        return make_result(
            tmp_path,
            document_id,
        )

    ingestion_service.ingest.side_effect = (
        ingest
    )

    service = DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )

    document, result = (
        service.process_stored_file(
            stored_file,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=1000,
            file_hash="a" * 64,
        )
    )

    assert isinstance(
        document,
        Document,
    )

    assert isinstance(
        result,
        IngestionResult,
    )

    assert document.status is (
        DocumentStatus.INDEXED
    )

    assert document.page_count == 5
    assert document.character_count == 500
    assert document.chunk_count == 3

    ingestion_service.ingest.assert_called_once_with(
        stored_file,
        document.document_id,
    )

    document_service.mark_parsed.assert_called_once_with(
        document
    )

    document_service.mark_chunked.assert_called_once_with(
        document
    )

    indexing_service.index_document.assert_called_once_with(
        document,
        result.chunks,
    )


def test_process_stored_file_updates_metadata(
    tmp_path,
):

    document_service = (
        make_document_service()
    )

    ingestion_service = (
        make_ingestion_service()
    )

    indexing_service = (
        make_indexing_service()
    )

    stored_file = make_stored_file(
        tmp_path
    )

    def ingest(
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        return make_result(
            tmp_path,
            document_id,
            page_count=10,
            character_count=2500,
        )

    ingestion_service.ingest.side_effect = (
        ingest
    )

    service = DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )

    document, _ = (
        service.process_stored_file(
            stored_file,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=1000,
            file_hash="a" * 64,
        )
    )

    assert document.page_count == 10
    assert document.character_count == 2500
    assert document.chunk_count == 3


def test_process_stored_file_ingestion_failure_marks_failed(
    tmp_path,
):

    ingestion_service = (
        make_ingestion_service()
    )

    ingestion_service.ingest.side_effect = (
        RuntimeError(
            "PDF parsing failed"
        )
    )

    service, document_service, _, indexing_service = (
        make_service(
            tmp_path,
            ingestion_service,
        )
    )

    stored_file = make_stored_file(
        tmp_path
    )

    with pytest.raises(
        RuntimeError,
        match="PDF parsing failed",
    ):

        service.process_stored_file(
            stored_file,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=1000,
            file_hash="a" * 64,
        )

    document = (
        document_service
        .create_document
        .call_args
        .args[0]
    )

    document_service.mark_failed.assert_called_once_with(
        document,
        "PDF parsing failed",
    )

    document_service.mark_parsed.assert_not_called()

    document_service.mark_chunked.assert_not_called()

    indexing_service.index_document.assert_not_called()

    assert document.status is (
        DocumentStatus.FAILED
    )


def test_process_stored_file_indexing_failure_is_propagated(
    tmp_path,
):

    document_service = (
        make_document_service()
    )

    ingestion_service = (
        make_ingestion_service()
    )

    indexing_service = Mock(
        spec=IndexingService
    )

    indexing_service.index_document.side_effect = (
        RuntimeError("Indexing failed")
    )

    stored_file = make_stored_file(
        tmp_path
    )

    def ingest(
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        return make_result(
            tmp_path,
            document_id,
        )

    ingestion_service.ingest.side_effect = (
        ingest
    )

    service = DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )

    with pytest.raises(
        RuntimeError,
        match="Indexing failed",
    ):

        service.process_stored_file(
            stored_file,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=1000,
            file_hash="a" * 64,
        )

    document = (
        document_service
        .create_document
        .call_args
        .args[0]
    )

    document_service.mark_failed.assert_not_called()

    assert document.status is (
        DocumentStatus.CHUNKED
    )


def test_process_stored_file_passes_correct_chunks_to_indexing(
    tmp_path,
):

    document_service = (
        make_document_service()
    )

    ingestion_service = (
        make_ingestion_service()
    )

    indexing_service = (
        make_indexing_service()
    )

    stored_file = make_stored_file(
        tmp_path
    )

    def ingest(
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        return make_result(
            tmp_path,
            document_id,
        )

    ingestion_service.ingest.side_effect = (
        ingest
    )

    service = DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )

    document, result = (
        service.process_stored_file(
            stored_file,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=1000,
            file_hash="a" * 64,
        )
    )

    indexing_service.index_document.assert_called_once()

    indexed_document, indexed_chunks = (
        indexing_service
        .index_document
        .call_args
        .args
    )

    assert indexed_document is document
    assert indexed_chunks == result.chunks

    for chunk in indexed_chunks:

        assert (
            chunk.document_id
            == document.document_id
        )


def test_process_stored_file_marks_statuses_in_order(
    tmp_path,
):

    document_service = (
        make_document_service()
    )

    ingestion_service = (
        make_ingestion_service()
    )

    indexing_service = (
        make_indexing_service()
    )

    stored_file = make_stored_file(
        tmp_path
    )

    call_order = []

    def ingest(
        stored_file: StoredFile,
        document_id: str,
    ) -> IngestionResult:

        return make_result(
            tmp_path,
            document_id,
        )

    ingestion_service.ingest.side_effect = (
        ingest
    )

    document_service.mark_parsed.side_effect = (
        lambda document: (
            call_order.append("PARSED"),
            setattr(
                document,
                "status",
                DocumentStatus.PARSED,
            ),
            document,
        )[-1]
    )

    document_service.mark_chunked.side_effect = (
        lambda document: (
            call_order.append("CHUNKED"),
            setattr(
                document,
                "status",
                DocumentStatus.CHUNKED,
            ),
            document,
        )[-1]
    )

    indexing_service.index_document.side_effect = (
        lambda document, chunks: (
            call_order.append("INDEXED"),
            setattr(
                document,
                "status",
                DocumentStatus.INDEXED,
            ),
        )[-1]
    )

    service = DocumentProcessingService(
        document_service=document_service,
        ingestion_service=ingestion_service,
        indexing_service=indexing_service,
    )

    service.process_stored_file(
        stored_file,
        original_filename="paper.pdf",
        mime_type="application/pdf",
        file_size=1000,
        file_hash="a" * 64,
    )

    assert call_order == [
        "PARSED",
        "CHUNKED",
        "INDEXED",
    ]