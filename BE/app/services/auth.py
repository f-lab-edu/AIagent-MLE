"""
인증 관련 비즈니스 로직을 처리하는 서비스 모듈입니다.
토큰 생성, 사용자 유효성 검사, 회원가입 등의 기능을 제공합니다.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from core.exception import CustomException, ExceptionCase
from utils import jwt_handler, hash_handler
from api.v1.schemas.auth import Token
from db.database import AsyncSession
from db.models import User, AuthorityLevel
from crud.user import get_user_by_email, create_user, get_user

# OAuth2PasswordBearer: 'auth/login' 엔드포인트에서 토큰을 가져오는 보안 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_token(id: str) -> Token:
    """
    사용자 ID를 기반으로 JWT 액세스 토큰을 생성합니다.

    Args:
        id (str): 사용자 고유 ID.

    Returns:
        Token: 생성된 액세스 토큰과 토큰 타입을 포함하는 객체.
    """
    access_token = jwt_handler.create_access_token(id)
    return Token(access_token=access_token, token_type="bearer")


def validate_token(token: str = Depends(oauth2_scheme)) -> str | None:
    """
    제공된 JWT 토큰의 유효성을 검사하고, 디코딩된 토큰에서 사용자 ID를 추출합니다.
    FastAPI 의존성으로 사용됩니다.

    Args:
        token (str, optional): OAuth2 스키마로부터 주입된 JWT 토큰.

    Returns:
        str | None: 유효한 경우 사용자 ID, 그렇지 않으면 None.
    """
    decode_token = jwt_handler.decode_access_token(token)
    id = decode_token.get("id")
    return id


async def validate_user(email: str, password: str, session: AsyncSession) -> str:
    """
    사용자 로그인 정보를 검증합니다.
    이메일로 사용자를 찾고, 제공된 비밀번호와 저장된 해시 비밀번호를 비교합니다.

    Args:
        email (str): 사용자 이메일.
        password (str): 사용자 비밀번호.
        session (AsyncSession): 데이터베이스 세션.

    Raises:
        CustomException: 사용자가 없거나 비밀번호가 일치하지 않을 경우 발생.

    Returns:
        str: 유효한 사용자의 ID.
    """
    user = await get_user_by_email(session, email)
    if not user:
        raise CustomException(
            case=ExceptionCase.AUTH_LOGIN_ERROR, detail="User not found"
        )
    if hash_handler.verify_password(password, user.hashed_password):
        return user.id
    else:
        raise CustomException(
            case=ExceptionCase.AUTH_LOGIN_ERROR, detail="Invalid password"
        )


async def join_user(
    user_id: str,
    email: str,
    password: str,
    name: str,
    user_group_id: str,
    session: AsyncSession,
):
    """
    새로운 사용자를 등록(회원가입)합니다.
    오직 관리자(ADMIN) 권한을 가진 사용자만 다른 사용자를 등록할 수 있습니다.

    Args:
        user_id (str): 작업을 요청한 현재 사용자의 ID.
        email (str): 신규 사용자의 이메일.
        password (str): 신규 사용자의 비밀번호.
        name (str): 신규 사용자의 이름.
        user_group_id (str): 신규 사용자가 속할 그룹의 ID.
        session (AsyncSession): 데이터베이스 세션.

    Raises:
        CustomException: 요청한 사용자가 관리자가 아닐 경우 발생.

    Returns:
        User: 생성된 사용자 객체.
    """
    current_user = await get_user(session, user_id)
    if current_user.user_group.authority_level != AuthorityLevel.ADMIN:
        raise CustomException(
            case=ExceptionCase.AUTH_PERMISSION_ERROR,
            detail="Only admin accounts are allowed.",
        )

    user = User(
        email=email,
        hashed_password=hash_handler.hash_password(password),
        name=name,
        user_group_id=user_group_id,
    )
    created_user = await create_user(session, user)
    return created_user
