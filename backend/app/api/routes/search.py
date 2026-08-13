from fastapi import APIRouter, Depends

from app.api.dependencies import get_retrieval_service
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


@router.post(
    "",
    response_model=SearchResponse,
)
async def search(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(
        get_retrieval_service
    ),
) -> SearchResponse:

    results = retrieval_service.search(
        request.query,
        top_k=request.top_k,
        document_ids=request.document_ids,
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