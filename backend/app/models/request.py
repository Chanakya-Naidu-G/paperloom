from pydantic import BaseModel, Field


class SearchRequest(BaseModel):

    query: str = Field(
        min_length=1,
        description="Search query",
    )

    top_k: int = Field(
        default=5,
        gt=0,
        description="Number of results to return",
    )

    document_ids: list[str] | None = None