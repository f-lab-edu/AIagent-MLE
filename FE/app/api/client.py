"""
백엔드 API 서버와 통신하기 위한 공유 HTTP 클라이언트를 설정합니다.

이 모듈은 `httpx.Client`의 단일 인스턴스를 생성하고 설정합니다.
- `base_url`은 `core.config`의 `settings.API_URL`에서 가져옵니다.
- 애플리케이션 전체에서 이 클라이언트 인스턴스를 재사용하여 API 요청을 보냅니다.
"""

import httpx
from core.config import settings

# 백엔드 API 서버에 요청을 보내는 데 사용될 httpx 클라이언트 인스턴스
client = httpx.Client(base_url=settings.API_URL)
