from pydantic import BaseModel


class UploadResponse(BaseModel):

    success: bool

    message: str

    original_filename: str | None = None

    stored_filename: str | None = None

    path: str | None = None

    pages: int | None = None

    characters: int | None = None

    chunk_count: int | None = None


class RetrievedChunkResponse(BaseModel):

    chunk_id: str

    document_id: str

    text: str

    distance: float

    chunk_index: int

    section: str

    page_start: int

    page_end: int

    character_count: int

    word_count: int


class SearchResponse(BaseModel):

    query: str

    results: list[RetrievedChunkResponse]
    
class SourceResponse(BaseModel):

    chunk_id: str

    document_id: str

    section: str

    page_start: int

    page_end: int


class AskResponse(BaseModel):

    query: str

    answer: str

    sources: list[SourceResponse]