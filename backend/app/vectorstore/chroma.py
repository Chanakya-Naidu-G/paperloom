import os

import chromadb
from chromadb.api.models.Collection import Collection

from app.models.embeddedChunk import EmbeddedChunk
from app.vectorstore.base import VectorStore
from app.models.retrieval import RetrievalResult

VECTOR_DB_PATH = os.environ.get("VECTOR_DB_PATH", "vector_db")
COLLECTION_NAME = os.environ.get("VECTOR_DB_COLLECTION", "research_documents")


class ChromaDB(VectorStore):

    def __init__(
        self,
        path: str | None = None,
        collection_name: str | None = None,
    ) -> None:

        self._client = chromadb.PersistentClient(
            path=path or VECTOR_DB_PATH,
        )

        self._collection: Collection = (
            self._client.get_or_create_collection(
                name=collection_name or COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        )

    @property
    def collection(self) -> Collection:
        return self._collection

    def count(self) -> int:
        return self._collection.count()

    def add_documents(
        self,
        embedded_chunks: list[EmbeddedChunk],
        batch_size: int = 100,
    ) -> None:

        for start in range(0, len(embedded_chunks), batch_size):

            batch = embedded_chunks[start:start + batch_size]

            ids: list[str] = []
            embeddings: list[list[float]] = []
            texts: list[str] = []
            metadatas: list[dict] = []

            for embedded_chunk in batch:
                id_, embedding, text, metadata = embedded_chunk.to_chroma()

                ids.append(id_)
                embeddings.append(embedding)
                texts.append(text)
                metadatas.append(metadata)

            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

    def document_exists(
        self,
        document_id: str,
    ) -> bool:

        result = self._collection.get(
            where={
                "document_id": document_id,
            },
            limit=1,
        )

        return len(result["ids"]) > 0

    def delete_document(
        self,
        document_id: str,
    ) -> None:

        self._collection.delete(
            where={
                "document_id": document_id,
            }
        )
    def query(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:

        if not query_vector:
            raise ValueError(
                "query_vector must not be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        if document_ids is not None and not document_ids:
            return []

        where_filter = (
            {"document_id": {"$in": document_ids}}
            if document_ids is not None
            else None
        )

        try:

            results = self._collection.query(
                query_embeddings=[list(query_vector)],
                n_results=top_k,
                where=where_filter,
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

        except Exception as exc:

            raise RuntimeError(
                "vector store query failed"
            ) from exc

        if not results:
            return []

        try:

            ids = results["ids"][0]
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

        except (KeyError, IndexError, TypeError) as exc:

            raise RuntimeError(
                "Invalid response received from vector store"
            ) from exc

        if not (
            len(ids)
            == len(documents)
            == len(metadatas)
            == len(distances)
        ):
            raise RuntimeError(
                "Inconsistent response received from vector store"
            )

        retrieval_results: list[RetrievalResult] = []

        for (
            chunk_id,
            document,
            metadata,
            distance,
        ) in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):

            if not isinstance(metadata, dict):
                raise RuntimeError(
                    "Invalid metadata received from vector store"
                )

            retrieval_results.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    text=document,
                    distance=distance,
                    chunk_index=metadata["chunk_index"],
                    section=metadata["section"],
                    page_start=metadata["page_start"],
                    page_end=metadata["page_end"],
                    character_count=metadata["character_count"],
                    word_count=metadata["word_count"],
                )
            )

        return retrieval_results
    def get_embedding(
        self,
        chunk_id: str,
    ) -> list[float] | None:

        results = self._collection.get(
            ids=[chunk_id],
            include=["embeddings"],
        )

        embeddings = results.get("embeddings")

        if embeddings is None or len(embeddings) == 0:
            return None

        embedding = embeddings[0]

        if embedding is None:
            return None

        return embedding.tolist()