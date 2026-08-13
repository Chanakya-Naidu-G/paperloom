from app.models.retrieval import RetrievalResult


class ContextBuilder:

    def build(
        self,
        results: list[RetrievalResult],
    ) -> str:

        if not results:
            return ""

        sources: list[str] = []

        for index, result in enumerate(results, start=1):

            page_range = (
                f"{result.page_start}-{result.page_end}"
                if result.page_start != result.page_end
                else str(result.page_start)
            )

            sources.append(
                f"[Source {index}]\n"
                f"Section: {result.section}\n"
                f"Pages: {page_range}\n"
                f"Chunk: {result.chunk_index}\n\n"
                f"{result.text}"
            )

        return "\n\n".join(sources)