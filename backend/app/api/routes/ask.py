from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_answer_generator,
    get_document_service,
    get_retrieval_service,
)
from app.api.routes.search import scope_document_ids
from app.auth.dependencies import get_current_user
from app.database.entities import User
from app.database.service import DocumentService
from app.generation.generator import AnswerGenerator
from app.models.request import SearchRequest
from app.models.response import AskResponse, SourceResponse
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/ask",
    tags=["Ask"],
)


@router.post(
    "",
    response_model=AskResponse,
)
async def ask(
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
    answer_generator: AnswerGenerator = Depends(
        get_answer_generator
    ),
) -> AskResponse:

    document_ids = scope_document_ids(
        request,
        current_user,
        document_service,
    )

    if not document_ids:
        return AskResponse(
            query=request.query,
            answer="You have no documents uploaded yet. Upload a PDF first, then ask your question.",
            sources=[],
        )

    results = retrieval_service.search(
        request.query,
        top_k=request.top_k,
        document_ids=document_ids,
    )

    answer = answer_generator.generate(
        request.query,
        results,
    )

    return AskResponse(
        query=request.query,
        answer=answer,
        sources=[
            SourceResponse(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                section=result.section,
                page_start=result.page_start,
                page_end=result.page_end,
            )
            for result in results
        ],
    )
