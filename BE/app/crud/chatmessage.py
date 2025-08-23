"""
ChatMessage 모델에 대한 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 정의합니다.
"""

from sqlmodel import select
from core.exception import CustomException, ExceptionCase
from db.models import ChatMessage
from db.database import AsyncSession


async def get_message_list(session: AsyncSession, conversation_id: str):
    """
    특정 대화 ID에 해당하는 모든 메시지 목록을 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        conversation_id (str): 조회할 대화의 ID.

    Returns:
        list[ChatMessage]: 메시지 객체 목록.
    """
    try:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.order_num)
        )
        result = await session.exec(statement)
        messages = result.all()
        return messages
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def create_message_list(session: AsyncSession, messages: list[ChatMessage]):
    """
    여러 개의 메시지를 데이터베이스에 한 번에 생성합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        messages (list[ChatMessage]): 생성할 메시지 객체 목록.

    Returns:
        list[ChatMessage]: 생성된 메시지 객체 목록.
    """
    try:
        for message in messages:
            session.add(message)
        await session.commit()
        for message in messages:
            await session.refresh(message)
        return messages
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def delete_message_list(session: AsyncSession, messages: list[ChatMessage]):
    """
    여러 개의 메시지를 데이터베이스에서 삭제합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        messages (list[ChatMessage]): 삭제할 메시지 객체 목록.

    Returns:
        bool: 삭제 성공 시 True.
    """
    try:
        for message in messages:
            await session.delete(message)
        await session.commit()
        return True
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))
