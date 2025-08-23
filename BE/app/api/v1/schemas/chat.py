"""
채팅(Chat) API 엔드포인트에서 사용되는 Pydantic 스키마를 정의합니다.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from db.models import Conversation, ChatMessage


class ChatRequest(BaseModel):
    """
    채팅 스트림 요청 시 사용되는 스키마입니다.
    """

    messages: list[str]


class GetConversationListResponse(BaseModel):
    """
    대화 목록 조회 응답 스키마입니다.
    SQLAlchemy 모델(Conversation)을 Pydantic 모델로 변환합니다.
    """

    model_config = ConfigDict(from_attributes=True)

    data: List[Conversation]


class GetMessageListRequest(BaseModel):
    """
    특정 대화의 메시지 목록 조회 요청 스키마입니다.
    """

    conversation_id: str


class GetMessageListResponse(BaseModel):
    """
    메시지 목록 조회 응답 스키마입니다.
    SQLAlchemy 모델(ChatMessage)을 Pydantic 모델로 변환합니다.
    """

    model_config = ConfigDict(from_attributes=True)

    data: List[ChatMessage]


class SaveConversationRequest(BaseModel):
    """
    대화 저장 요청 시 사용되는 스키마입니다.
    """

    title: Optional[str] = None
    messages: List[str]


class DeleteConversationRequest(BaseModel):
    """
    대화 삭제 요청 시 사용되는 스키마입니다.
    """

    conversation_id: str
