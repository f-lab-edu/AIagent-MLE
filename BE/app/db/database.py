"""
데이터베이스 연결 및 세션 관리를 위한 설정을 포함합니다.
데이터베이스 초기화 및 초기 데이터 생성을 위한 함수를 제공합니다.
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db.models import UserGroup, User
from utils import hash_handler
from core.exception import CustomException, ExceptionCase
from core.config import settings


# 데이터베이스 연결 URL 생성
database_url = f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"  # noqa: E501

# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(database_url, echo=True)
# 비동기 세션 생성기
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """
    데이터베이스의 모든 테이블을 생성합니다.
    SQLModel.metadata.create_all을 사용하여 정의된 모든 SQLModel 테이블을 생성합니다.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    API 요청 처리 중 사용할 데이터베이스 세션을 생성하고 제공하는 의존성 함수입니다.
    요청이 끝나면 세션은 자동으로 닫힙니다.

    Yields:
        AsyncSession: 비동기 데이터베이스 세션 객체.
    """
    async with async_session() as session:
        yield session


async def init_data():
    """
    애플리케이션 시작 시 초기 데이터를 생성합니다.
    (기본 사용자 그룹 및 관리자 사용자)
    이미 데이터가 존재하는 경우(IntegrityError), 생성을 건너뜁니다.
    """
    try:
        async with async_session() as session:
            user_group = UserGroup(
                name=settings.INIT_USER_GROUP_NAME,
                authority_level=settings.INIT_USER_GROUP_AUTHORITY_LEVEL,
            )
            session.add(user_group)

            user = User(
                email=settings.INIT_USER_EMAIL,
                hashed_password=hash_handler.hash_password(settings.INIT_USER_PASSWORD),
                name=settings.INIT_USER_NAME,
                user_group=user_group,
            )
            session.add(user)
            await session.commit()

            await session.refresh(user_group)
            await session.refresh(user)
    except IntegrityError:
        print("Already init data")
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.DB_OP_ERROR, detail=f"INIT DATA ERROR: {e}"
        )
