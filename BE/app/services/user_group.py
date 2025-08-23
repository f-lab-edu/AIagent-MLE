"""
사용자 그룹 관련 비즈니스 로직을 처리하는 서비스 모듈입니다.
CRUD 작업을 오케스트레이션하여 사용자 그룹을 조회, 추가, 삭제합니다.
"""

from crud.user_group import get_all_user_groups, create_user_group, delete_user_group
from db.database import AsyncSession
from db.models import UserGroup, AuthorityLevel


async def get_user_groups(session: AsyncSession) -> list[UserGroup]:
    """
    모든 사용자 그룹 목록을 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        list[UserGroup]: 사용자 그룹 객체 목록.
    """
    user_groups = await get_all_user_groups(session)
    return user_groups


async def add_user_group(
    name: str, authority_level: AuthorityLevel, session: AsyncSession
):
    """
    새로운 사용자 그룹을 생성합니다.

    Args:
        name (str): 생성할 그룹의 이름.
        authority_level (AuthorityLevel): 생성할 그룹의 권한 수준.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        UserGroup: 생성된 사용자 그룹 객체.
    """
    user_group = UserGroup(name=name, authority_level=authority_level)
    created_user_group = await create_user_group(user_group=user_group, session=session)
    return created_user_group


async def delete_user_group_by_id(id: str, session: AsyncSession):
    """
    ID를 기준으로 사용자 그룹을 삭제합니다.

    Args:
        id (str): 삭제할 사용자 그룹의 ID.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        UserGroup: 삭제된 사용자 그룹 객체.
    """
    deleted_user_group = await delete_user_group(id=id, session=session)
    return deleted_user_group
