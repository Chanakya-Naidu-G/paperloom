from pathlib import Path

from app.ingestion.service import IngestionService
from app.models.storage import StoredFile


path = Path(
    "data/uploads/ANN-Introduction, MP, Hebb.pdf"
)

stored_file = StoredFile(
    filename=path.name,
    path=path,
)

service = IngestionService()

result = service.ingest(
    stored_file,
    "debug-document",
)

print("CHUNKS:", len(result.chunks))

for chunk in result.chunks[:30]:
    print(
        f"{chunk.chunk_index}: "
        f"section={chunk.section} "
        f"pages={chunk.page_start}-{chunk.page_end} "
        f"words={chunk.word_count}"
    )