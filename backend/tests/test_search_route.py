from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.models.request import SearchRequest
from app.api.dependencies import (
    get_document_service,
    get_retrieval_service,
)
from app.api.routes.search import router
from app.auth.dependencies import get_current_user
from app.database.entities import Document, DocumentStatus, User
from app.database.service import DocumentService
from app.models.retrieval import RetrievalResult

TEST_USER = User(id=1, username="tester", hashed_password="x")


class FakeRetrievalService:

    def __init__(
        self,
        results: list[RetrievalResult] | None = None,
    ) -> None:

        self.results = results or []

        self.calls: list[
            tuple[
                str,
                int,
                list[str] | None,
            ]
        ] = []

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:

        self.calls.append(
            (
                query,
                top_k,
                document_ids,
            )
        )

        return self.results[:top_k]


def make_result(
    chunk_id: str,
    document_id: str,
    distance: float,
    *,
    section: str = "Introduction",
    chunk_index: int = 0,
) -> RetrievalResult:

    return RetrievalResult(
        chunk_id=chunk_id,
        document_id=document_id,
        text=f"Text for {chunk_id}",
        distance=distance,
        chunk_index=chunk_index,
        section=section,
        page_start=1,
        page_end=2,
        character_count=20,
        word_count=4,
    )


class FakeDocumentService:

    def __init__(
        self,
        document_ids: list[str] | None = None,
    ) -> None:
        # Default user owns doc-1 and doc-2 so scoped search still works
        ids = document_ids if document_ids is not None else ["doc-1", "doc-2"]
        self._documents = [
            Document(
                document_id=doc_id,
                user_id="1",
                original_filename=f"{doc_id}.pdf",
                stored_filename=f"{doc_id}.pdf",
                parsed_filename="",
                mime_type="application/pdf",
                file_size=1024,
                file_hash="a" * 64,
                page_count=1,
                character_count=100,
                chunk_count=1,
                embedding_model="",
                embedding_dimension=0,
                status=DocumentStatus.INDEXED,
            )
            for doc_id in ids
        ]

    def list_documents(
        self,
        user_id: str | None = None,
        include_deleted: bool = False,
    ):
        return self._documents


def create_client(
    results: list[RetrievalResult] | None = None,
    document_ids: list[str] | None = None,
):

    retrieval_service = FakeRetrievalService(
        results
    )
    document_service = FakeDocumentService(document_ids)

    app = FastAPI()

    app.include_router(
        router,
        prefix="/api/v1",
    )

    app.dependency_overrides[
        get_retrieval_service
    ] = lambda: retrieval_service
    app.dependency_overrides[
        get_document_service
    ] = lambda: document_service
    app.dependency_overrides[
        get_current_user
    ] = lambda: TEST_USER

    client = TestClient(app)

    return client, retrieval_service


def test_search_returns_results():

    results = [
        make_result(
            "chunk-1",
            "doc-1",
            0.1,
        ),
        make_result(
            "chunk-2",
            "doc-1",
            0.2,
            section="Methods",
            chunk_index=1,
        ),
    ]

    client, service = create_client(
        results
    )

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is machine learning?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == (
        "What is machine learning?"
    )

    assert len(data["results"]) == 2

    assert data["results"][0] == {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "text": "Text for chunk-1",
        "distance": 0.1,
        "chunk_index": 0,
        "section": "Introduction",
        "page_start": 1,
        "page_end": 2,
        "character_count": 20,
        "word_count": 4,
    }

    assert service.calls == [
        (
            "What is machine learning?",
            5,
            ["doc-1", "doc-2"],
        )
    ]


def test_search_passes_top_k():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
            "top_k": 10,
        },
    )

    assert response.status_code == 200

    assert service.calls == [
        (
            "What is AI?",
            10,
            ["doc-1", "doc-2"],
        )
    ]


def test_search_passes_document_ids():

    client, service = create_client()

    document_ids = [
        "doc-1",
        "doc-2",
    ]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
            "top_k": 5,
            "document_ids": document_ids,
        },
    )

    assert response.status_code == 200

    assert service.calls == [
        (
            "What is AI?",
            5,
            document_ids,
        )
    ]


def test_search_uses_default_top_k():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
        },
    )

    assert response.status_code == 200

    assert service.calls == [
        (
            "What is AI?",
            5,
            ["doc-1", "doc-2"],
        )
    ]


def test_search_without_document_ids():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
        },
    )

    assert response.status_code == 200

    assert service.calls[0][2] == ["doc-1", "doc-2"]


def test_search_returns_empty_results():

    client, service = create_client(
        []
    )

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "What is AI?"
    assert data["results"] == []

    assert service.calls == [
        (
            "What is AI?",
            5,
            ["doc-1", "doc-2"],
        )
    ]

def test_search_rejects_unauthorized_document_ids():

    client, service = create_client(
        [make_result("chunk-1", "doc-1", 0.1)],
    )

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
            "document_ids": ["doc-1", "evil-doc"],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You do not have access to one or more requested documents."
    )

    # Retrieval must never run for an unauthorized request.
    assert service.calls == []
    
def test_scope_document_ids_rejects_unauthorized_ids():

    from app.api.routes.search import scope_document_ids
    from fastapi import HTTPException

    service = FakeDocumentService()

    request = SearchRequest(
        query="What is AI?",
        document_ids=["doc-1", "evil-doc"],
    )

    with pytest.raises(HTTPException) as exc_info:
        scope_document_ids(
            request,
            TEST_USER,
            service,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == (
        "You do not have access to one or more requested documents."
    )
    
def test_search_empty_when_user_has_no_documents():

    client, service = create_client(
        [make_result("chunk-1", "doc-1", 0.1)],
        document_ids=[],
    )

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
        },
    )

    assert response.status_code == 200
    assert response.json()["results"] == []
    # retrieval never called because user has no documents to search
    assert service.calls == []


def test_search_rejects_empty_query():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "query": "",
        },
    )

    assert response.status_code == 422

    assert service.calls == []


def test_search_rejects_invalid_top_k():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
            "top_k": 0,
        },
    )

    assert response.status_code == 422

    assert service.calls == []


def test_search_rejects_missing_query():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "top_k": 5,
        },
    )

    assert response.status_code == 422

    assert service.calls == []


def test_search_rejects_invalid_top_k_type():

    client, service = create_client()

    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is AI?",
            "top_k": "invalid",
        },
    )

    assert response.status_code == 422

    assert service.calls == []