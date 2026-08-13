from app.models.retrieval import RetrievalResult

from app.context.builder import ContextBuilder
from app.generation.prompts import build_rag_prompt


class AnswerGenerator:

    def __init__(
        self,
        client,
        context_builder: ContextBuilder,
    ) -> None:

        self._client = client
        self._context_builder = context_builder

    def generate(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> str:

        context = self._context_builder.build(
            results
        )

        prompt = build_rag_prompt(
            query,
            context,
        )

        return self._client.generate(
            prompt
        )