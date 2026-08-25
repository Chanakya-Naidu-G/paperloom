from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import (
    get_document_service,
    get_retrieval_service,
)
from app.auth.dependencies import get_current_user
from app.database.entities import User
from app.database.service import DocumentService
from app.models.request import SearchRequest
from app.models.response import (
    RetrievedChunkResponse,
    SearchResponse,
)
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


def scope_document_ids(
    request: SearchRequest,
    current_user: User,
    document_service: DocumentService,
) -> list[str]:

    user_document_ids = [
        document.document_id
        for document in document_service.list_documents(
            user_id=str(current_user.id),
        )
    ]

    if not request.document_ids:
        return user_document_ids

    allowed = set(user_document_ids)

    requested = list(dict.fromkeys(request.document_ids))

    if not all(document_id in allowed for document_id in requested):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have access to one or more "
                "requested documents."
            ),
        )

    return requested

@router.post(
    "",
    response_model=SearchResponse,
)
async def search(
    request: SearchRequest,
    current_user: User = Depends(
        get_current_user
    ),
    document_service: DocumentService = Depends(
        get_document_service
    ),
    retrieval_service: RetrievalService = Depends(
        get_retrieval_service
    ),
) -> SearchResponse:

    document_ids = scope_document_ids(
        request,
        current_user,
        document_service,
    )

    if not document_ids:
        return SearchResponse(
            query=request.query,
            results=[],
        )

    results = retrieval_service.search(
        request.query,
        top_k=request.top_k,
        document_ids=document_ids,
    )

    return SearchResponse(
        query=request.query,
        results=[
            RetrievedChunkResponse(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                text=result.text,
                distance=result.distance,
                chunk_index=result.chunk_index,
                section=result.section,
                page_start=result.page_start,
                page_end=result.page_end,
                character_count=result.character_count,
                word_count=result.word_count,
            )
            for result in results
        ],
    )
