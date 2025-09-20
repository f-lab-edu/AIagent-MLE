"""
검색 대상 문서 관리를 위한 API 엔드포인트를 제공합니다. (데이터 소스 목록 조회, 문서 업로드/삭제/수정)
"""

from fastapi import APIRouter, Depends
from api.v1.schemas.document import (
    UploadDocumentRequest,
    DeleteDocumentRequest,
    UpdateDocuemntRequest,
)
from services.auth import validate_token
from db.models import DataSource
from db.database import get_session, AsyncSession
from services.document import (
    get_documents,
    upload_documents,
    delete_documents,
    update_document_user_groups,
)
from schemas.schemas import CustomAPIResponse


docs_router = APIRouter(prefix="/docs", tags=["Retrieval Document"])


@docs_router.get("/datasource/list", response_model=CustomAPIResponse)
async def get_data_sources():
    """
    사용 가능한 데이터 소스 목록을 조회합니다.

    Returns:
        CustomAPIResponse: 데이터 소스 이름 목록을 포함한 응답.
    """
    return CustomAPIResponse(data=list(DataSource._value2member_map_.keys()))


@docs_router.get("/list", response_model=CustomAPIResponse)
async def get_document_list(
    datasource: DataSource | None = None,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    문서 목록을 조회합니다. 데이터 소스로 필터링할 수 있습니다.

    Args:
        datasource (DataSource | None, optional): 필터링할 데이터 소스. Defaults to None.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 문서 목록을 포함한 응답.
    """

    document_list = await get_documents(session=session, datasource=datasource)

    return CustomAPIResponse(data=document_list)


@docs_router.post("/upload", response_model=CustomAPIResponse)
async def upload_document(
    documents_data: UploadDocumentRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    새로운 문서를 업로드합니다.

    Args:
        documents_data (UploadDocumentRequest): 업로드할 문서 데이터.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 업로드 성공을 나타내는 빈 응답.
    """

    await upload_documents(
        datasource=documents_data.datasource,
        user_groups=documents_data.user_groups,
        document_urls=documents_data.document_urls,
        session=session,
    )

    return CustomAPIResponse()


@docs_router.post("/delete", response_model=CustomAPIResponse)
async def delete_document(
    documents_data: DeleteDocumentRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    문서를 삭제합니다.

    Args:
        documents_data (DeleteDocumentRequest): 삭제할 문서 데이터.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 삭제 성공을 나타내는 빈 응답.
    """

    await delete_documents(
        datasource=documents_data.datasource,
        page_ids=documents_data.page_ids,
        session=session,
    )

    return CustomAPIResponse()


@docs_router.post("/update", response_model=CustomAPIResponse)
async def update_document(
    documents_data: UpdateDocuemntRequest,
    user_id: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    """
    문서에 연결된 사용자 그룹을 수정합니다.

    Args:
        documents_data (UpdateDocuemntRequest): 문서 수정 데이터.
        user_id (str, optional): 토큰에서 검증된 사용자 ID. Defaults to Depends(validate_token).
        session (AsyncSession, optional): 데이터베이스 세션. Defaults to Depends(get_session).

    Raises:
        CustomException: 인증되지 않은 사용자인 경우 발생.

    Returns:
        CustomAPIResponse: 수정 성공을 나타내는 빈 응답.
    """

    await update_document_user_groups(
        datasource=documents_data.datasource,
        page_id=documents_data.page_id,
        user_groups=documents_data.user_groups,
        session=session,
    )

    return CustomAPIResponse()
