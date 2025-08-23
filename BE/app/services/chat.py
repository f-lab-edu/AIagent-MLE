"""
채팅 관련 비즈니스 로직을 처리하는 서비스 모듈입니다.
RAG 그래프를 이용한 스트리밍 응답 생성, 대화 내역 조회/저장/삭제 기능을 제공합니다.
"""

from langchain_core.messages import HumanMessage, AIMessage
from rag_graph.edge import get_graph
from rag_graph.state import GraphState
from db.database import AsyncSession
from db.models import Conversation, ChatMessage, MessageRole
from crud.user import get_user
from crud.conversation import (
    get_conversation_list,
    create_conversation,
    delete_conversation,
)
from crud.chatmessage import get_message_list, create_message_list


async def stream_graph_events(user_id: str, messages: list[str], session: AsyncSession):
    """
    RAG 그래프를 통해 채팅 응답을 스트리밍으로 생성합니다.

    Args:
        user_id (str): 현재 사용자 ID.
        messages (list[str]): 사용자와 AI가 주고받은 메시지 목록.
        session (AsyncSession): 데이터베이스 세션.

    Yields:
        str: AI 모델이 생성하는 응답 스트림의 각 청크(chunk).
    """
    graph = get_graph()

    user = await get_user(session, user_id)

    base_messages = [
        HumanMessage(content=message) if i % 2 == 0 else AIMessage(content=message)
        for i, message in enumerate(messages)
    ]

    async for event in graph.astream_events(
        input=GraphState(messages=base_messages, authority_group=user.user_group_id)
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield content


async def get_conversation_by_user_id(user_id: str, session: AsyncSession):
    """
    특정 사용자의 모든 대화 목록을 조회합니다.

    Args:
        user_id (str): 사용자 ID.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        list[Conversation]: 대화 객체 목록.
    """
    return await get_conversation_list(session, user_id)


async def get_messages_by_id(conversation_id: str, session: AsyncSession):
    """
    특정 대화 ID에 속한 모든 메시지 목록을 조회합니다.

    Args:
        conversation_id (str): 대화 ID.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        list[ChatMessage]: 메시지 객체 목록.
    """
    return await get_message_list(session, conversation_id)


async def save_conversations(
    user_id: str, title: str | None, messages: list[str], session: AsyncSession
):
    """
    대화 내용(제목, 메시지 목록)을 데이터베이스에 저장합니다.

    Args:
        user_id (str): 대화를 저장할 사용자 ID.
        title (str | None): 대화 제목. 지정되지 않으면 첫 번째 메시지로 자동 설정됩니다.
        messages (list[str]): 저장할 메시지 목록.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        str: 생성된 대화의 ID.
    """
    if not title:
        title = messages[0]

    conversation = Conversation(title=title, user_id=user_id)
    created_conversation = await create_conversation(session, conversation)

    chat_messages = []
    for i, message in enumerate(messages):
        role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
        chat_messages.append(
            ChatMessage(
                conversation_id=created_conversation.id,
                role=role,
                order_num=i + 1,
                content=message,
            )
        )
    await create_message_list(session, chat_messages)
    return created_conversation.id


async def delete_conversations(conversation_id: str, session: AsyncSession):
    """
    특정 대화를 데이터베이스에서 삭제합니다.
    연관된 메시지들도 함께 삭제됩니다 (cascade).

    Args:
        conversation_id (str): 삭제할 대화의 ID.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        bool: 삭제 성공 시 True.
    """
    await delete_conversation(session, conversation_id)
    return True
