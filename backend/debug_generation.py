from app.context.builder import ContextBuilder
from app.embeddings.embedder import Embedder
from app.generation.generator import AnswerGenerator
from app.retrieval.service import RetrievalService
from app.vectorstore.chroma import ChromaDB


class DebugClient:

    def generate(self, prompt: str) -> str:
        print("\n========== GENERATED PROMPT ==========\n")
        print(prompt)
        print("\n========== END PROMPT ==========\n")

        return "DEBUG: Generation pipeline executed successfully."


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

generator = AnswerGenerator(
    client=DebugClient(),
    context_builder=ContextBuilder(),
)

answer = generator.generate(
    query="What is Hebb learning?",
    results=results,
)

print("ANSWER:")
print(answer)