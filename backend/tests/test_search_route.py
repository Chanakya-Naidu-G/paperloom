from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_retrieval_service
from app.api.routes.search import router
from app.models.retrieval import RetrievalResult


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


def create_client(
    results: list[RetrievalResult] | None = None,
):

    service = FakeRetrievalService(
        results
    )

    app = FastAPI()

    app.include_router(
        router,
        prefix="/api/v1",
    )

    app.dependency_overrides[
        get_retrieval_service
    ] = lambda: service

    client = TestClient(app)

    return client, service


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
            None,
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
            None,
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
            None,
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

    assert service.calls[0][2] is None


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
            None,
        )
    ]


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