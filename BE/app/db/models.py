"""
애플리케이션에서 사용하는 데이터베이스 테이블 모델을 정의합니다.
SQLModel을 사용하여 각 테이블의 스키마와 관계를 설정합니다.
"""

import datetime
import enum
import uuid
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship, JSON
from sqlalchemy import Column, DateTime, func, Enum as SAEnum, Text, CHAR


class DataSource(str, enum.Enum):
    """
    문서의 데이터 출처를 나타내는 Enum입니다.
    """

    NOTION = "notion"


class AuthorityLevel(str, enum.Enum):
    """
    사용자 그룹의 권한 수준을 나타내는 Enum입니다.
    """

    ADMIN = "admin"
    TEAM = "team"
    GUEST = "guest"


class MessageRole(str, enum.Enum):
    """
    메시지 발송 주체를 나타내는 Enum입니다.
    """

    USER = "user"  # 사용자가 보낸 메시지
    ASSISTANT = "assistant"  # 챗봇(AI)이 보낸 메시지


class User(SQLModel, table=True):
    """
    사용자 정보를 저장하는 테이블 모델입니다.
    UserGroup과 다대일 관계를 가집니다.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(
            CHAR(36),
            primary_key=True,
            index=True,
            nullable=False,
        ),
        description="사용자 고유 식별 UUID",
    )
    email: str = Field(unique=True, index=True, description="사용자 Email")
    hashed_password: str = Field(description="해시된 사용자 PW")
    name: str = Field(description="사용자 이름")

    user_group_id: Optional[str] = Field(
        default=None, foreign_key="usergroup.id", description="사용자가 속한 그룹의 ID"
    )

    created_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        description="생성 날짜",
    )
    update_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
        description="마지막 수정일",
    )

    # UserGroup과의 다대일 관계
    user_group: "UserGroup" = Relationship(back_populates="users")
    # Conversation과의 일대다 관계
    conversations: List["Conversation"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class UserGroup(SQLModel, table=True):
    """
    사용자 그룹 정보를 저장하는 테이블 모델입니다.
    User와 일대다 관계를 가집니다.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(
            CHAR(36),
            primary_key=True,
            index=True,
            nullable=False,
        ),
        description="그룹 고유 식별 UUID",
    )
    name: str = Field(description="그룹 이름", unique=True)

    authority_level: str = Field(
        sa_column=Column(
            SAEnum(AuthorityLevel),
            nullable=False,
            index=True,
        ),
        description="그룹 권한 수준",
    )

    description: Optional[str] = Field(default=None, description="그룹에 대한 설명")

    # User와의 일대다 관계
    users: List["User"] = Relationship(back_populates="user_group")


class Conversation(SQLModel, table=True):
    """
    사용자와 챗봇 간의 대화 정보를 저장하는 테이블 모델입니다.
    User와 다대일, ChatMessage와 일대다 관계를 가집니다.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(
            CHAR(36),
            primary_key=True,
            index=True,
            nullable=False,
        ),
        description="대화 고유 식별 UUID",
    )
    title: str = Field(
        index=True, description="대화 제목 (예: 첫 질문을 기반으로 자동 생성)"
    )

    user_id: str = Field(
        foreign_key="user.id", index=True, description="대화를 생성한 사용자 ID"
    )

    created_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        description="생성 날짜",
    )
    update_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
        description="마지막 수정일",
    )

    # User와의 다대일 관계
    user: User = Relationship(back_populates="conversations")
    # ChatMessage와의 일대다 관계
    messages: List["ChatMessage"] = Relationship(
        back_populates="conversation", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class ChatMessage(SQLModel, table=True):
    """
    개별 채팅 메시지를 저장하는 테이블 모델입니다.
    Conversation과 다대일 관계를 가집니다.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(
            CHAR(36),
            primary_key=True,
            index=True,
            nullable=False,
        ),
        description="메시지 고유 식별 UUID",
    )

    conversation_id: str = Field(
        foreign_key="conversation.id", index=True, description="메시지가 속한 대화의 ID"
    )

    role: MessageRole = Field(
        sa_column=Column(SAEnum(MessageRole), nullable=False),
        description="메시지 발송 주체 (user/assistant)",
    )

    order_num: int = Field(index=True, description="대화 내 메시지 순서")

    content: str = Field(
        sa_column=Column(Text, nullable=False), description="메시지 내용"
    )

    created_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            index=True,
            nullable=False,
        ),
        description="생성 날짜",
    )

    # Conversation과의 다대일 관계
    conversation: Conversation = Relationship(back_populates="messages")


class DocumentTB(SQLModel, table=True):
    """
    업로드된 문서의 메타데이터를 저장하는 테이블 모델입니다.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(
            CHAR(36),
            primary_key=True,
            index=True,
            nullable=False,
        ),
        description="업로드한 문서 고유 식별 UUID",
    )
    page_id: str = Field(
        index=True,
        unique=True,
        description="데이터 소스 내 문서의 고유 ID (예: Notion 페이지 ID)",
    )
    datasource: str = Field(
        sa_column=Column(
            SAEnum(DataSource),
            nullable=False,
            index=True,
        ),
        description="데이터 출처 (예: notion)",
    )
    user_groups: list[str] = Field(
        sa_column=Column(JSON, index=True),
        description="문서에 접근 가능한 사용자 그룹 ID 목록",
    )
    created_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        description="생성 날짜",
    )
    update_date: datetime.datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
        description="마지막 수정일",
    )
