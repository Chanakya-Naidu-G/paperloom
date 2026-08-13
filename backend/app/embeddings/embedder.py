from sentence_transformers import SentenceTransformer
from app.models.embedding import EmbeddingConfig, DEFAULT_EMBEDDING_CONFIG  
from app.models.chunk import Chunk
from app.models.embeddedChunk import EmbeddedChunk
class Embedder:

    QUERY_PREFIX = (
        "Represent this sentence for searching "
        "relevant passages: "
    )

    def __init__(self, config: EmbeddingConfig = DEFAULT_EMBEDDING_CONFIG):
        self.config = config
        self.model = SentenceTransformer(self.config.model_name, device=self.config.device)

    def embed(self, text: str) -> list[float]:
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()
    def embed_batch(self, texts: list[str],batch_size: int = 32) -> list[list[float]]:
        vectors = self.model.encode(texts, batch_size=batch_size, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]
    def embed_chunks(
        self,
        chunks: list[Chunk],
        batch_size: int = 32,
    ) -> list[EmbeddedChunk]:

        if not chunks:
            return []

        embedded_chunks: list[EmbeddedChunk] = []

        for start in range(0, len(chunks), batch_size):

            batch = chunks[start:start + batch_size]

            texts = [chunk.text for chunk in batch]

            embeddings = self.embed_batch(
                texts,
                batch_size=batch_size,
            )

            embedded_chunks.extend(
                EmbeddedChunk.from_chunk(chunk, embedding)
                for chunk, embedding in zip(batch, embeddings)
            )

        return embedded_chunks
    def embed_query(self, query: str) -> list[float]:
        query_with_prefix = self.QUERY_PREFIX + query
        return self.embed(query_with_prefix)