from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_answer_generator,
    get_retrieval_service,
)
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
    retrieval_service: RetrievalService = Depends(
        get_retrieval_service
    ),
    answer_generator: AnswerGenerator = Depends(
        get_answer_generator
    ),
) -> AskResponse:

    results = retrieval_service.search(
        request.query,
        top_k=request.top_k,
        document_ids=request.document_ids,
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