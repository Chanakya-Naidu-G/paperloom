from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.storage import get_upload_path
from app.database.connection import get_db
from app.database.entities import User
from app.database.service import DocumentService
from app.models.response import DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:

    document_service = DocumentService(db)

    documents = document_service.list_documents(
        user_id=str(current_user.id),
    )

    return [
        DocumentResponse(
            document_id=document.document_id,
            original_filename=document.original_filename,
            file_size=document.file_size,
            page_count=document.page_count,
            character_count=document.character_count,
            chunk_count=document.chunk_count,
            status=document.status.value,
            uploaded_at=document.uploaded_at,
        )
        for document in documents
    ]


@router.get(
    "/{document_id}/pdf",
)
def get_document_pdf(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document_service = DocumentService(db)
    document = document_service.get_document(document_id)

    if document is None or document.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    # Ownership check: document must belong to current user
    # Orphaned docs (user_id is None) are hidden from everyone
    if document.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = get_upload_path(document.stored_filename)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on server.",
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type or "application/pdf",
        filename=document.original_filename,
        headers={
            "Content-Disposition": f'inline; filename="{document.original_filename}"'
        },
    )
