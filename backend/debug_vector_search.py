from app.embeddings.embedder import Embedder
from app.vectorstore.chroma import ChromaDB

query = "What is Hebb learning?"

embedder = Embedder()
vector_store = ChromaDB()

query_vector = embedder.embed_query(query)

results = vector_store.query(
    query_vector,
    top_k=15,
)

print(f"RAW CHROMA RESULTS: {len(results)}")
print()

for i,result in enumerate(results):
    print(
        f"{i}: "
        f"distance={result.distance:.4f} "
        f"similarity={1.0-result.distance:.4f} "
        f"section={result.section} "
        f"chunk={result.chunk_index} "
        f"pages={result.page_start}-{result.page_end}"
    )