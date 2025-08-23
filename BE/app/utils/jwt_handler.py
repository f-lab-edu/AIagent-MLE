"""
JWT(JSON Web Token) 생성 및 검증 관련 유틸리티 함수를 제공합니다.
사용자 인증을 위한 액세스 토큰을 처리합니다.
"""

import jwt
import datetime
import pytz
from typing import Optional
from core.config import settings
from core.exception import CustomException, ExceptionCase


def create_access_token(id: str) -> dict:
    """
    사용자 ID를 받아 JWT 액세스 토큰을 생성합니다.
    토큰에는 만료 시간과 사용자 ID가 포함됩니다.

    Args:
        id (str): 토큰에 포함될 사용자 ID.

    Returns:
        dict: 인코딩된 JWT 토큰 문자열.
    """
    try:
        payload = {
            "exp": datetime.datetime.now(tz=pytz.timezone("Asia/Seoul"))
            + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "id": id,
        }
        encoded = jwt.encode(
            payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded

    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.AUTH_ERROR, detail=str(e))


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT 액세스 토큰을 디코딩하여 페이로드(payload)를 반환합니다.
    토큰 만료 또는 형식 오류 발생 시 예외를 처리합니다.

    Args:
        token (str): 디코딩할 JWT 토큰 문자열.

    Raises:
        CustomException: 토큰이 만료되었거나 유효하지 않을 경우 발생.

    Returns:
        Optional[dict]: 디코딩된 페이로드 딕셔너리.
    """
    try:
        decode_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )

    except jwt.ExpiredSignatureError as e:
        raise CustomException(
            exception_case=ExceptionCase.AUTH_UNAUTHORIZED_ERROR, detail=str(e)
        )
    except jwt.InvalidTokenError as e:
        raise CustomException(
            exception_case=ExceptionCase.AUTH_INVALID_TOKEN_ERROR, detail=str(e)
        )
    else:
        return decode_token
