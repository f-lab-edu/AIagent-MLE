"""
User 모델에 대한 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 정의합니다.
"""

from sqlmodel import select
from core.exception import CustomException, ExceptionCase
from db.models import User
from db.database import AsyncSession


async def get_user(session: AsyncSession, id: str) -> User | None:
    """
    ID를 기준으로 사용자를 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        id (str): 조회할 사용자의 ID.

    Returns:
        User | None: 조회된 사용자 객체 또는 None.
    """
    try:
        statement = select(User).where(User.id == id)
        result = await session.exec(statement)
        user = result.first()
        return user
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """
    이메일을 기준으로 사용자를 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        email (str): 조회할 사용자의 이메일.

    Returns:
        User | None: 조회된 사용자 객체 또는 None.
    """
    try:
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def create_user(session: AsyncSession, user: User) -> User:
    """
    새로운 사용자를 데이터베이스에 생성합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        user (User): 생성할 사용자 객체.

    Returns:
        User: 생성된 사용자 객체.
    """
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))
