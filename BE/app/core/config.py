"""RAG 서버 설정 파일"""

import base64
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional


class Settings(BaseSettings):
    """환경변수 설정"""

    GEMINI_API_KEY: str
    NOTION_API_KEY: str
    SMITHERY_API_KEY: str = "2a8e8fb9-a326-4f4d-adfa-62f9ae1febb8"

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


class MCPConfig:
    """MCP 설정"""

    smithery_api_key = settings.SMITHERY_API_KEY
    notion_api_key = settings.NOTION_API_KEY

    @classmethod
    def get_mcp_config(cls, key: Literal["notion"]):
        if key == "notion":
            config = {"notionApiKey": cls.notion_api_key}
            config_b64 = base64.b64encode(json.dumps(config).encode()).decode()
            return {
                "notion": {
                    "url": f"https://server.smithery.ai/@smithery/notion/mcp?config={config_b64}&api_key={cls.smithery_api_key}",
                    "transport": "streamable_http",
                }
            }


try:
    mcp_config = MCPConfig()
except Exception as e:
    raise RuntimeError("Fail to load environment vars") from e
