import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data"

OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY: Optional[str] = os.getenv("WEAVIATE_API_KEY")
WEAVIATE_INDEX_NAME: str = os.getenv("WEAVIATE_INDEX_NAME", "DebateAI")

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

VECTORSTORE_DIR = DATA_DIR / "vectorstore"
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

DEBATE_MAX_TURNS: int = int(os.getenv("DEBATE_MAX_TURNS", "8"))
DEBATE_TURN_TIMEOUT: int = int(os.getenv("DEBATE_TURN_TIMEOUT", "120"))

CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

RETRIEVER_TOP_K: int = int(os.getenv("RETRIEVER_TOP_K", "5"))
