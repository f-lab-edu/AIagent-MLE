"""
애플리케이션의 환경 변수 및 설정을 관리하는 모듈입니다.

Pydantic-settings 라이브러리를 사용하여 `.env` 파일에서 환경 변수를 로드하고,
애플리케이션 전역에서 사용될 `settings` 객체를 생성합니다.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션에서 사용되는 환경 변수들을 정의하는 클래스입니다.

    Attributes:
        SECRET_KEY (str): JWT 토큰 암호화에 사용되는 비밀 키입니다.
        ALGORITHM (Optional[str]): JWT 암호화 알고리즘입니다. (기본값: "HS256")
        API_URL (Optional[str]): 통신할 백엔드 API 서버의 기본 URL입니다. (기본값: "http://127.0.0.1:8000")
    """

    SECRET_KEY: str
    ALGORITHM: Optional[str] = "HS256"
    API_URL: Optional[str] = "http://127.0.0.1:8000"

    # Pydantic 모델의 설정을 구성합니다.
    model_config = SettingsConfigDict(
        case_sensitive=True,  # 환경 변수 이름의 대소문자를 구분합니다.
        env_file="../.env",  # 상위 디렉토리의 .env 파일을 환경 변수 파일로 사용합니다.
        env_file_encoding="utf-8",
    )


try:
    # Settings 클래스의 인스턴스를 생성하여 애플리케이션 전역에서 사용합니다.
    settings = Settings()
except Exception as e:
    # .env 파일 로딩 실패 또는 필수 환경 변수 누락 시 에러를 발생시킵니다.
    raise RuntimeError("Fail to load environment vars") from e
