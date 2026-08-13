from app.database.entities import Document, DocumentStatus
from app.database.service import DocumentService
from app.indexing.service import IndexingService
from app.ingestion.service import IngestionService
from app.models.chunk import IngestionResult
from app.models.storage import StoredFile


class DocumentProcessingService:

    def __init__(
        self,
        document_service: DocumentService,
        ingestion_service: IngestionService,
        indexing_service: IndexingService,
    ) -> None:

        self._document_service = document_service
        self._ingestion_service = ingestion_service
        self._indexing_service = indexing_service

    def process_stored_file(
        self,
        stored_file: StoredFile,
        *,
        original_filename: str,
        mime_type: str,
        file_size: int,
        file_hash: str,
    ) -> tuple[Document, IngestionResult]:

        document = Document(
            original_filename=original_filename,
            stored_filename=stored_file.filename,
            parsed_filename="",
            mime_type=mime_type,
            file_size=file_size,
            file_hash=file_hash,
            page_count=0,
            character_count=0,
            chunk_count=0,
            embedding_model="",
            embedding_dimension=0,
            status=DocumentStatus.UPLOADED,
        )

        document = self._document_service.create_document(
            document
        )

        try:

            result = self._ingestion_service.ingest(
                stored_file,
                document.document_id,
            )

            document.page_count = (
                result.parsed_document.page_count
            )

            document.character_count = (
                result.parsed_document.characters
            )

            document.chunk_count = (
                len(result.chunks)
            )

            document.parsed_filename = (
                result.parsed_document.path.name
            )

            self._document_service.mark_parsed(
                document
            )

            self._document_service.mark_chunked(
                document
            )

        except Exception as exc:

            self._document_service.mark_failed(
                document,
                str(exc)[:512],
            )

            raise

        self._indexing_service.index_document(
            document,
            result.chunks,
        )

        return document, result