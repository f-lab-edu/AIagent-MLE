"""
인증(Auth) API 엔드포인트에서 사용되는 Pydantic 스키마를 정의합니다.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    로그인 요청 시 사용되는 스키마입니다.
    """

    email: str
    password: str


class JoinRequest(BaseModel):
    """
    회원가입 요청 시 사용되는 스키마입니다.
    """

    email: str
    password: str
    name: str
    user_group_id: str | None


class Token(BaseModel):
    """
    JWT 토큰 정보를 담는 스키마입니다.
    """

    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    """
    사용자 정보를 나타내는 기본 스키마입니다.
    """

    email: str
    name: str
    authority_level: str


class UserInDB(User):
    """
    데이터베이스에 저장된 사용자 정보를 나타내는 스키마입니다.
    해시된 비밀번호를 포함합니다.
    """

    hashed_password: str
