"""
DocumentTB 모델에 대한 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 정의합니다.
"""

from sqlmodel import select, and_
from core.exception import CustomException, ExceptionCase
from db.models import DocumentTB
from db.database import AsyncSession


async def get_document_list(session: AsyncSession, datasource: str | None = None):
    """
    데이터베이스에서 문서 목록을 조회합니다. 데이터 소스로 필터링할 수 있습니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        datasource (str | None, optional): 필터링할 데이터 소스. Defaults to None.

    Returns:
        list[DocumentTB]: 문서 정보 객체 목록.
    """
    try:
        statement = select(DocumentTB)
        if datasource:
            statement = statement.where(DocumentTB.datasource == datasource)
        result = await session.exec(statement)
        documents = result.all()
        return documents
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def get_document_info_by_page_id(
    session: AsyncSession, datasource: str, page_id: str
):
    """
    데이터 소스와 페이지 ID를 기준으로 특정 문서 정보를 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        datasource (str): 문서의 데이터 소스.
        page_id (str): 문서의 페이지 ID.

    Returns:
        DocumentTB | None: 조회된 문서 정보 객체 또는 None.
    """
    try:
        statement = select(DocumentTB).where(
            and_(DocumentTB.datasource == datasource, DocumentTB.page_id == page_id)
        )
        result = await session.exec(statement)
        document = result.first()
        return document
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def create_document_info(session: AsyncSession, documents: list[DocumentTB]):
    """
    여러 개의 문서 정보를 데이터베이스에 생성합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        documents (list[DocumentTB]): 생성할 문서 정보 객체 목록.

    Returns:
        DocumentTB: 마지막으로 생성된 문서 정보 객체.
    """
    try:
        for document in documents:
            session.add(document)
        await session.commit()
        await session.refresh(document)
        return document
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def delete_document_info_by_page_id(
    session: AsyncSession, datasource: str, page_ids: list[str]
):
    """
    데이터 소스와 페이지 ID 목록을 기준으로 여러 문서 정보를 삭제합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        datasource (str): 삭제할 문서들의 데이터 소스.
        page_ids (list[str]): 삭제할 문서들의 페이지 ID 목록.

    Returns:
        bool: 삭제 성공 시 True.
    """
    try:
        delete_document_list = []
        for page_id in page_ids:
            statement = select(DocumentTB).where(
                and_(DocumentTB.page_id == page_id, DocumentTB.datasource == datasource)
            )
            result = await session.exec(statement)
            document = result.first()
            delete_document_list.append(document)
        for document in delete_document_list:
            await session.delete(document)
        await session.commit()
        return True
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))


async def update_document_info(
    session: AsyncSession, datasource: str, page_id: str, user_groups: list[str]
):
    """
    특정 문서 정보의 사용자 그룹을 수정합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        datasource (str): 수정할 문서의 데이터 소스.
        page_id (str): 수정할 문서의 페이지 ID.
        user_groups (list[str]): 새로 할당할 사용자 그룹 목록.

    Returns:
        DocumentTB: 수정된 문서 정보 객체.
    """
    try:
        statement = select(DocumentTB).where(
            and_(DocumentTB.datasource == datasource, DocumentTB.page_id == page_id)
        )
        result = await session.exec(statement)
        document = result.first()
        document.user_groups = user_groups

        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document
    except Exception as e:
        raise CustomException(exception_case=ExceptionCase.DB_OP_ERROR, detail=str(e))
