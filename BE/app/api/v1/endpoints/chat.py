"""
채팅 관련 API 엔드포인트를 제공합니다. (실시간 스트리밍, 대화 내역 조회 및 관리)
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from api.v1.schemas.chat import (
    ChatRequest,
    SaveConversationRequest,
    DeleteConversationRequest,
)
from services.auth import validate_token
from services.chat import (
    stream_graph_events,
    get_conversation_by_user_id,
    get_messages_by_id,
    save_conversations,
    delete_conversations,
)
from db.database import get_session, AsyncSession
from core.exception import CustomException, ExceptionCase
from schemas.schemas import CustomAPIResponse

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.post("/stream")
async def chat_stream(
    chat_data: ChatRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    실시간 채팅 스트리밍을 처리합니다.

    Args:
        chat_data (ChatRequest): 메시지를 포함한 채팅 요청 데이터.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        StreamingResponse: 그래프 이벤트를 포함한 스트리밍 응답.
    """
    if not user_id:
        raise CustomException(exception_case=ExceptionCase.AUTH_UNAUTHORIZED_ERROR)

    return StreamingResponse(
        stream_graph_events(user_id, chat_data.messages, session),
    )


@chat_router.get("/history/conversation/list", response_model=CustomAPIResponse)
async def get_conversation_list(
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    현재 사용자의 대화 목록을 조회합니다.

    Args:
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 대화 목록을 포함한 응답.
    """
    if not user_id:
        raise CustomException(exception_case=ExceptionCase.AUTH_UNAUTHORIZED_ERROR)

    conversation_list = await get_conversation_by_user_id(user_id, session)
    return CustomAPIResponse(data=conversation_list)


@chat_router.get(
    "/history/{conversation_id}/messages", response_model=CustomAPIResponse
)
async def get_message_list(
    conversation_id: str,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    특정 대화의 메시지 목록을 조회합니다.

    Args:
        conversation_id (str): 대화 ID.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 메시지 목록을 포함한 응답.
    """
    if not user_id:
        raise CustomException(exception_case=ExceptionCase.AUTH_UNAUTHORIZED_ERROR)

    message_list = await get_messages_by_id(conversation_id, session)
    return CustomAPIResponse(data=message_list)


@chat_router.post("/history/conversation/save", response_model=CustomAPIResponse)
async def save_conversation(
    conversation_data: SaveConversationRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    대화를 저장합니다.

    Args:
        conversation_data (SaveConversationRequest): 저장할 대화 데이터.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 대화 저장이 성공했음을 나타내는 빈 응답.
    """
    if not user_id:
        raise CustomException(exception_case=ExceptionCase.AUTH_UNAUTHORIZED_ERROR)

    await save_conversations(
        user_id=user_id,
        title=conversation_data.title,
        messages=conversation_data.messages,
        session=session,
    )

    return CustomAPIResponse()


@chat_router.post("/history/conversation/delete", response_model=CustomAPIResponse)
async def delete_conversation(
    conversation_data: DeleteConversationRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    대화를 삭제합니다.

    Args:
        conversation_data (DeleteConversationRequest): 삭제할 대화 ID를 포함한 요청.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 대화 삭제가 성공했음을 나타내는 빈 응답.
    """
    if not user_id:
        raise CustomException(exception_case=ExceptionCase.AUTH_UNAUTHORIZED_ERROR)

    await delete_conversations(
        conversation_id=conversation_data.conversation_id, session=session
    )

    return CustomAPIResponse()
