"""
사용자 그룹(User Group) API 엔드포인트에서 사용되는 Pydantic 스키마를 정의합니다.
"""

from pydantic import BaseModel, ConfigDict
from typing import List
from db.models import UserGroup, AuthorityLevel


class GetUserGroupsResponse(BaseModel):
    """
    사용자 그룹 목록 조회 응답 스키마입니다.
    SQLAlchemy 모델(UserGroup)을 Pydantic 모델로 변환합니다.
    """

    model_config = ConfigDict(from_attributes=True)

    data: List[UserGroup]


class AddUserGroupRequest(BaseModel):
    """
    사용자 그룹 추가 요청 시 사용되는 스키마입니다.
    """

    name: str
    authority_level: AuthorityLevel


class DeleteUserGroupRequest(BaseModel):
    """
    사용자 그룹 삭제 요청 시 사용되는 스키마입니다.
    """

    id: str
