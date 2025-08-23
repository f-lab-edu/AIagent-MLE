"""
문서(Document) API 엔드포인트에서 사용되는 Pydantic 스키마를 정의합니다.
"""

from pydantic import BaseModel
from db.models import DataSource


class UploadDocumentRequest(BaseModel):
    """
    문서 업로드 요청 시 사용되는 스키마입니다.
    """

    datasource: DataSource
    user_groups: list[str]
    document_urls: list[str]


class DeleteDocumentRequest(BaseModel):
    """
    문서 삭제 요청 시 사용되는 스키마입니다.
    """

    datasource: DataSource
    page_ids: list[str]


class UpdateDocuemntRequest(BaseModel):
    """
    문서 정보 수정 요청 시 사용되는 스키마입니다.
    """

    datasource: DataSource
    page_id: str
    user_groups: list[str] | None = None
