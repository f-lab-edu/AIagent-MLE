"""
UserGroup 모델에 대한 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 정의합니다.
"""

from sqlmodel import select
from core.exception import CustomException, ExceptionCase
from db.models import UserGroup
from db.database import AsyncSession


async def get_all_user_groups(session: AsyncSession) -> list[UserGroup] | None:
    """
    모든 사용자 그룹 목록을 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        list[UserGroup] | None: 사용자 그룹 객체 목록 또는 None.
    """
    try:
        statement = select(UserGroup)
        result = await session.exec(statement)
        user_groups = result.all()
        return user_groups
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def create_user_group(user_group: UserGroup, session: AsyncSession):
    """
    새로운 사용자 그룹을 데이터베이스에 생성합니다.

    Args:
        user_group (UserGroup): 생성할 사용자 그룹 객체.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        UserGroup: 생성된 사용자 그룹 객체.
    """
    try:
        session.add(user_group)
        await session.commit()
        await session.refresh(user_group)
        return user_group
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def delete_user_group(id: str, session: AsyncSession):
    """
    ID를 기준으로 사용자 그룹을 삭제합니다.

    Args:
        id (str): 삭제할 사용자 그룹의 ID.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        UserGroup: 삭제된 사용자 그룹 객체.
    """
    try:
        statement = select(UserGroup).where(UserGroup.id == id)
        result = await session.exec(statement)
        user_group = result.first()

        await session.delete(user_group)
        await session.commit()
        return user_group
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))
