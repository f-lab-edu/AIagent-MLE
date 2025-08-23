"""
Conversation 모델에 대한 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 정의합니다.
"""

from sqlmodel import select
from core.exception import CustomException, ExceptionCase
from db.models import Conversation
from db.database import AsyncSession


async def get_conversation(session: AsyncSession, conversation_id: str):
    """
    특정 ID를 가진 대화 정보를 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        conversation_id (str): 조회할 대화의 ID.

    Returns:
        Conversation | None: 조회된 대화 객체 또는 None.
    """
    try:
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.exec(statement)
        conversation = result.first()
        return conversation
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def get_conversation_list(session: AsyncSession, user_id: str):
    """
    특정 사용자의 모든 대화 목록을 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        user_id (str): 사용자의 ID.

    Returns:
        list[Conversation]: 대화 객체 목록.
    """
    try:
        statement = select(Conversation).where(Conversation.user_id == user_id)
        result = await session.exec(statement)
        conversations = result.all()
        return conversations
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def create_conversation(session: AsyncSession, conversation: Conversation):
    """
    새로운 대화를 데이터베이스에 생성합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        conversation (Conversation): 생성할 대화 객체.

    Returns:
        Conversation: 생성된 대화 객체.
    """
    try:
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def delete_conversation(session: AsyncSession, conversation_id: str):
    """
    특정 ID를 가진 대화를 데이터베이스에서 삭제합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        conversation_id (str): 삭제할 대화의 ID.

    Returns:
        bool: 삭제 성공 시 True.
    """
    try:
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.exec(statement)
        conversation = result.first()
        await session.delete(conversation)
        await session.commit()
        return True
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))
