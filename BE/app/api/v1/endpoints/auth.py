"""
사용자 인증 관련 API 엔드포인트를 제공합니다. (로그인, 회원가입)
"""

from fastapi import APIRouter, Depends
from api.v1.schemas.auth import LoginRequest, JoinRequest
from services.auth import create_token, validate_user, join_user, validate_token
from db.database import get_session, AsyncSession
from schemas.schemas import CustomAPIResponse

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=CustomAPIResponse)
async def login(login_data: LoginRequest, session: AsyncSession = Depends(get_session)):
    """
    사용자 로그인을 처리합니다.

    Args:
        login_data (LoginRequest): 로그인 정보 (이메일, 비밀번호).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Returns:
        CustomAPIResponse: 인증 토큰을 포함한 응답.
    """
    user_id = await validate_user(
        email=login_data.email, password=login_data.password, session=session
    )
    return CustomAPIResponse(data=create_token(user_id))


@auth_router.post("/join", response_model=CustomAPIResponse)
async def join(
    user_data: JoinRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    신규 사용자 회원가입을 처리합니다.

    Args:
        user_data (JoinRequest): 사용자 회원가입 정보.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 회원가입 성공을 나타내는 빈 응답.
    """

    await join_user(
        user_id=user_id,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        user_group_id=user_data.user_group_id,
        session=session,
    )

    return CustomAPIResponse()
