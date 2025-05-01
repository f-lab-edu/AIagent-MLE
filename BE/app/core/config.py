import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    NOTION_API_KEY: str

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file='.env',
        env_file_encoding='utf-8'
    )
    

settings = Settings()