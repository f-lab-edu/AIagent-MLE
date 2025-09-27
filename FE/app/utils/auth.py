"""
인증 및 권한 부여와 관련된 유틸리티 함수를 제공하는 모듈입니다.

주로 Streamlit 세션에 저장된 JWT(JSON Web Token)를 처리하는 기능을 포함합니다.
"""

import jwt
from core.config import settings
import streamlit as st


# JWT 디코딩에 사용될 비밀 키와 알고리즘을 `settings`에서 가져옵니다.
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def get_current_user_authority_level() -> str | None:
    """
    세션에 저장된 access_token을 디코딩하여 현재 사용자의 권한 수준을 반환합니다.

    토큰이 없거나, 만료되었거나, 유효하지 않은 경우 None을 반환하여
    인증되지 않았거나 유효하지 않은 세션임을 나타냅니다.

    Returns:
        str | None: 사용자의 권한 수준 문자열(예: "admin", "user") 또는 None.
    """
    if "access_token" not in st.session_state:
        # 세션에 토큰이 없으면 사용자가 로그인하지 않은 상태입니다.
        return None

    token = st.session_state["access_token"]
    try:
        # JWT 토큰을 디코딩하여 payload(내용)를 추출합니다.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # payload에서 'authority_level' 클레임을 가져옵니다.
        authority_level = payload.get("authority_level")
        return authority_level
    except jwt.ExpiredSignatureError:
        # 토큰이 만료된 경우
        return None
    except jwt.InvalidTokenError:
        # 토큰이 유효하지 않은 경우 (서명 불일치 등)
        return None
    except Exception:
        # 그 외 예기치 않은 오류 발생 시
        return None
