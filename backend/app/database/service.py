from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.storage import get_upload_path
from app.database.entities import Document
from app.database.entities import DocumentStatus
from app.database.repository import DocumentRepository


class DocumentService:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self._repository = DocumentRepository(db)

    def create_document(
        self,
        document: Document,
    ) -> Document:

        existing = self._repository.get_by_file_hash(
            document.file_hash,
            include_deleted=True,
            user_id=document.user_id,
        )

        if existing is None:
            return self._repository.create(document)

        if existing.is_deleted:
            self._reset_document(existing, document)
            existing.is_deleted = False

            return self._repository.update(existing)

        # Active duplicate for this user: the new upload replaces
        # the old one in place (same document_id), so ingestion
        # overwrites parsed/chunks files and indexing purges the
        # stale vectors before re-indexing.
        self._delete_stored_file(existing.stored_filename)
        self._reset_document(existing, document)

        return self._repository.update(existing)

    @staticmethod
    def _reset_document(
        existing: Document,
        document: Document,
    ) -> None:

        existing.original_filename = document.original_filename
        existing.stored_filename = document.stored_filename
        existing.parsed_filename = document.parsed_filename
        existing.mime_type = document.mime_type
        existing.file_size = document.file_size
        existing.page_count = 0
        existing.character_count = 0
        existing.chunk_count = 0
        existing.embedding_model = ""
        existing.embedding_dimension = 0
        existing.status = DocumentStatus.UPLOADED
        existing.indexed_at = None
        existing.error_message = None

    @staticmethod
    def _delete_stored_file(
        stored_filename: str,
    ) -> None:

        import logging

        logger = logging.getLogger(__name__)

        try:
            path = get_upload_path(stored_filename)

            if path.exists():
                path.unlink()
        except Exception:
            logger.exception(
                "Failed to remove replaced stored file: %s",
                stored_filename,
            )

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:

        return self._repository.get_by_document_id(
            document_id
        )

    def list_documents(
        self,
        user_id: str | None = None,
    ) -> list[Document]:

        return self._repository.list_documents(
            user_id=user_id,
        )

    def mark_parsed(
        self,
        document: Document,
    ) -> Document:

        document.status = DocumentStatus.PARSED

        return self._repository.update(
            document
        )

    def mark_chunked(
        self,
        document: Document,
    ) -> Document:

        document.status = DocumentStatus.CHUNKED

        return self._repository.update(
            document
        )

    def mark_indexing(
        self,
        document: Document,
    ) -> Document:

        document.status = DocumentStatus.INDEXING

        return self._repository.update(
            document
        )

    def mark_indexed(
        self,
        document: Document,
    ) -> Document:

        document.status = DocumentStatus.INDEXED
        document.indexed_at = datetime.now(
            timezone.utc
        )

        return self._repository.update(
            document
        )

    def record_embedding_metadata(
        self,
        document: Document,
        *,
        embedding_model: str,
        embedding_dimension: int,
        chunk_count: int,
    ) -> Document:

        document.embedding_model = embedding_model
        document.embedding_dimension = embedding_dimension
        document.chunk_count = chunk_count

        return self._repository.update(
            document
        )

    def mark_failed(
        self,
        document: Document,
        error_message: str,
    ) -> Document:

        document.status = DocumentStatus.FAILED
        document.error_message = error_message

        return self._repository.update(
            document
        )

    def delete_document(
        self,
        document_id: str,
    ) -> Document | None:

        return self._repository.soft_delete(
            document_id
        )

    def restore_document(
        self,
        document_id: str,
    ) -> Document | None:

        return self._repository.restore(
            document_id
        )