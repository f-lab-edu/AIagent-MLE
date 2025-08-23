"""
문서 관리 관련 비즈니스 로직을 처리하는 서비스 모듈입니다.
데이터베이스 및 벡터 저장소(Qdrant)와 상호작용하여 문서를 조회, 업로드, 삭제, 수정합니다.
"""

from services.qdrant_service import QdrantService
from crud.document import (
    get_document_list,
    create_document_info,
    delete_document_info_by_page_id,
    update_document_info,
)
from schemas.schemas import DocumentMetadata
from utils.data_loader import get_data_loader
from utils.datasource_url import extract_page_id
from db.models import DataSource, DocumentTB
from db.database import AsyncSession


async def get_documents(session: AsyncSession, datasource: DataSource | None = None):
    """
    데이터베이스에 저장된 문서 목록을 조회합니다.

    Args:
        session (AsyncSession): 데이터베이스 세션.
        datasource (DataSource | None, optional): 필터링할 데이터 소스.

    Returns:
        list[DocumentTB]: 문서 정보 객체 목록.
    """
    return await get_document_list(session=session, datasource=datasource)


async def upload_documents(
    datasource: DataSource,
    user_groups: list[str],
    document_urls: list[str],
    session: AsyncSession,
):
    """
    지정된 URL의 문서를 로드하여 벡터 저장소에 업로드하고,
    관련 메타데이터를 데이터베이스에 저장합니다.

    Args:
        datasource (DataSource): 문서의 데이터 소스 (예: notion).
        user_groups (list[str]): 문서에 접근 권한을 가질 사용자 그룹 목록.
        document_urls (list[str]): 업로드할 문서의 URL 목록.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        str: 성공 메시지 "Success".
    """

    data_loader = get_data_loader(datasource=datasource)

    page_id_list = [extract_page_id(url, datasource) for url in document_urls]

    documents = [
        DocumentTB(
            page_id=page_id,
            datasource=datasource.value,
            user_groups=user_groups,
        )
        for page_id in page_id_list
    ]
    await create_document_info(session=session, documents=documents)

    for page_id in page_id_list:
        await data_loader.upload_documents(page_id=page_id, user_groups=user_groups)

    return "Success"


async def delete_documents(
    datasource: DataSource, page_ids: list[str], session: AsyncSession
):
    """
    특정 문서들을 데이터베이스와 벡터 저장소에서 모두 삭제합니다.

    Args:
        datasource (DataSource): 삭제할 문서의 데이터 소스.
        page_ids (list[str]): 삭제할 문서의 페이지 ID 목록.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        str: 성공 메시지 "Success".
    """
    qdrant = QdrantService()

    await delete_document_info_by_page_id(
        session=session, page_ids=page_ids, datasource=datasource.value
    )

    for page_id in page_ids:
        await qdrant.delete_document(
            conditions=DocumentMetadata(
                datasource=datasource.value, page_id=page_id
            ).model_dump(exclude_none=True)
        )

    return "Success"


async def update_document_user_groups(
    datasource: DataSource,
    page_id: str,
    user_groups: list[str],
    session: AsyncSession,
):
    """
    특정 문서의 접근 권한(사용자 그룹)을 데이터베이스와 벡터 저장소에서 수정합니다.

    Args:
        datasource (DataSource): 수정할 문서의 데이터 소스.
        page_id (str): 수정할 문서의 페이지 ID.
        user_groups (list[str]): 새로 설정할 사용자 그룹 목록.
        session (AsyncSession): 데이터베이스 세션.

    Returns:
        str: 성공 메시지 "Success".
    """
    qdrant = QdrantService()

    await update_document_info(
        session=session,
        datasource=datasource.value,
        page_id=page_id,
        user_groups=user_groups,
    )

    await qdrant.update_document_payload(
        datasource=datasource,
        page_id=page_id,
        update_metadata=DocumentMetadata(user_groups=user_groups),
    )

    return "Success"
