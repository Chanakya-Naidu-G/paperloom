import asyncio
import hashlib
import logging

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exc

from app.core.storage import UPLOAD_DIR
from app.core.storage import get_upload_path
from app.models.response import UploadResponse
from app.models.storage import StoredFile
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.utils.file_utils import generate_filename, validate_file

logger = logging.getLogger(__name__)


class UploadService:

    def __init__(
        self,
        document_processing_service: DocumentProcessingService,
    ) -> None:

        self._document_processing_service = (
            document_processing_service
        )

    async def save_file(
        self,
        file: UploadFile,
    ) -> StoredFile:

        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        stored_filename = generate_filename(
            file.filename
        )

        file_path = get_upload_path(
            stored_filename
        )

        # Stream file to disk to avoid loading whole file into memory
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(65536)
                if not chunk:
                    break
                buffer.write(chunk)

        # Reset read pointer in case caller expects it (safe no-op here)
        try:
            await file.seek(0)
        except Exception:
            pass

        return StoredFile(
            filename=stored_filename,
            path=file_path,
        )

    async def process_upload(
        self,
        file: UploadFile,
        *,
        user_id: str | None = None,
    ) -> UploadResponse:

        await validate_file(file)

        stored_file = await self.save_file(file)

        try:
            file_hash = hashlib.sha256(
                stored_file.path.read_bytes()
            ).hexdigest()

            document, ingestion_result = await asyncio.to_thread(
                self._document_processing_service.process_stored_file,
                stored_file,
                original_filename=file.filename,
                mime_type=file.content_type or "application/octet-stream",
                file_size=stored_file.path.stat().st_size,
                file_hash=file_hash,
                user_id=user_id,
            )

        except ValueError as exc:

            logger.warning(
                "Rejected upload for %s: %s",
                file.filename,
                exc,
            )

            try:
                if stored_file.path.exists():
                    stored_file.path.unlink()
            except Exception:
                logger.exception(
                    "Failed to remove stored file after rejected upload: %s",
                    stored_file.path,
                )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

        except Exception as exc:

            logger.exception(
                "Failed to process uploaded document: %s",
                stored_file.path,
            )

            try:
                if stored_file.path.exists():
                    stored_file.path.unlink()
            except Exception:
                logger.exception(
                    "Failed to remove stored file after processing failure: %s",
                    stored_file.path,
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process document. Please try again or upload a different file.",
            ) from exc
        logger.info(
            "Uploaded and processed file: %s -> %s",
            file.filename,
            stored_file.filename,
        )

        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            document_id=document.document_id,
            original_filename=file.filename,
            pages=ingestion_result.parsed_document.page_count,
            characters=ingestion_result.parsed_document.characters,
            chunk_count=len(ingestion_result.chunks),
        )