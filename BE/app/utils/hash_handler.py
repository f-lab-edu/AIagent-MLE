"""
비밀번호 해싱 및 검증 관련 유틸리티 함수를 제공합니다.
passlib.context.CryptContext를 사용하여 bcrypt 알고리즘으로 비밀번호를 안전하게 처리합니다.
"""

from core.exception import CustomException, ExceptionCase
from passlib.context import CryptContext
from core.config import settings

# 환경 변수에서 시크릿 키를 가져와 해싱에 사용 (솔트 역할)
SECRET_KEY = settings.SECRET_KEY
# bcrypt 알고리즘을 사용하는 CryptContext 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    일반 텍스트 비밀번호를 해시 처리합니다.
    비밀번호에 시크릿 키를 더해 보안을 강화합니다.

    Args:
        password (str): 해시할 원본 비밀번호.

    Returns:
        str: 해시된 비밀번호 문자열.
    """
    try:
        return pwd_context.hash(password + SECRET_KEY)
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.AUTH_ERROR, detail=str(e))


def verify_password(password: str, hashed_password: str) -> bool:
    """
    일반 텍스트 비밀번호와 해시된 비밀번호가 일치하는지 검증합니다.

    Args:
        password (str): 검증할 원본 비밀번호.
        hashed_password (str): 데이터베이스에 저장된 해시된 비밀번호.

    Returns:
        bool: 비밀번호가 일치하면 True, 그렇지 않으면 False.
    """
    try:
        verify_result = pwd_context.verify(
            secret=password + SECRET_KEY, hash=hashed_password
        )
        return verify_result
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.AUTH_ERROR, detail=str(e))
