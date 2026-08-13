from app.context.builder import ContextBuilder
from app.embeddings.embedder import Embedder
from app.retrieval.service import RetrievalService
from app.vectorstore.chroma import ChromaDB


embedder = Embedder()
vector_store = ChromaDB()

retrieval_service = RetrievalService(
    embedder=embedder,
    vector_store=vector_store,
)

results = retrieval_service.search(
    "What is Hebb learning?",
    top_k=5,
)

builder = ContextBuilder()

context = builder.build(results)

print(context)