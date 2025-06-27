"""RAG 서버 설정 파일"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional


class Settings(BaseSettings):
    """환경변수 설정"""

    GEMINI_API_KEY: str
    NOTION_API_KEY: str

    QDRANT_SERVER: Optional[str] = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: Optional[str] = "test_collection"
    VECTOR_SIZE: Optional[int] = 3072
    DISTANCE_METRIC: Literal["DOT", "COSINE", "EUCLID", "MANHATTAN"] = "COSINE"

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8"
    )


try:
    settings = Settings()
except Exception as e:
    raise RuntimeError("Fail to load environment vars") from e
