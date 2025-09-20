"""
사용자 그룹 관리를 위한 API 엔드포인트를 제공합니다. (목록 조회, 생성, 삭제)
"""

from fastapi import APIRouter, Depends
from api.v1.schemas.user_group import (
    AddUserGroupRequest,
    DeleteUserGroupRequest,
)
from services.auth import validate_token
from services.user_group import get_user_groups, add_user_group, delete_user_group_by_id
from db.database import get_session, AsyncSession
from db.models import AuthorityLevel
from schemas.schemas import CustomAPIResponse


user_group_router = APIRouter(prefix="/user-group", tags=["User Group"])


@user_group_router.get("/list", response_model=CustomAPIResponse)
async def get_user_groups_list(
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    모든 사용자 그룹 목록을 조회합니다.

    Args:
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 사용자 그룹 목록을 포함한 응답.
    """

    user_groups = await get_user_groups(session=session)
    return CustomAPIResponse(data=user_groups)


@user_group_router.get("/authority-level/list", response_model=CustomAPIResponse)
async def get_authority_level_list(user_id: str = Depends(validate_token)):
    """
    사용자 그룹에 할당 가능한 권한 등급 목록을 조회합니다.

    Args:
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 권한 등급 목록을 포함한 응답.
    """

    return CustomAPIResponse(data=list(AuthorityLevel._value2member_map_.keys()))


@user_group_router.post("/create", response_model=CustomAPIResponse)
async def create_user_group(
    user_group_data: AddUserGroupRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    새로운 사용자 그룹을 생성합니다.

    Args:
        user_group_data (AddUserGroupRequest): 생성할 사용자 그룹 데이터.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 생성 성공을 나타내는 빈 응답.
    """

    await add_user_group(
        name=user_group_data.name,
        authority_level=user_group_data.authority_level,
        session=session,
    )

    return CustomAPIResponse()


@user_group_router.post("/delete", response_model=CustomAPIResponse)
async def delete_user_group(
    user_group_data: DeleteUserGroupRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    사용자 그룹을 삭제합니다.

    Args:
        user_group_data (DeleteUserGroupRequest): 삭제할 사용자 그룹의 ID를 포함한 요청.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 삭제 성공을 나타내는 빈 응답.
    """

    await delete_user_group_by_id(id=user_group_data.id, session=session)

    return CustomAPIResponse()
