from dataclasses import dataclass


@dataclass(slots=True,frozen=True)
class EmbeddingConfig:
    model_name: str
    dimension: int
    device: str
DEFAULT_EMBEDDING_CONFIG = EmbeddingConfig(
    model_name="BAAI/bge-small-en-v1.5",
    dimension=384,
    device="cpu",
)