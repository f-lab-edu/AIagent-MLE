"""RAG 서버 설정 파일"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경변수 설정"""

    GEMINI_API_KEY: str
    NOTION_API_KEY: str

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file="../.env", env_file_encoding="utf-8"
    )


settings = Settings()
