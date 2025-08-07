"""
Langgraph의 각 Node에서 사용되는 LLM 호출에 대한 출력 구조를 정의하는 모듈.
"""

from typing import Literal, List
from pydantic import BaseModel, Field


class RefineQuestion(BaseModel):
    """
    1. 이전 대화 내역을 바탕으로 쿼리를 재작성 해주는 노드에 사용되는 LLM 모델 출력 구조.
    """

    rewritten_question: str = Field(
        ...,
        description="The rewritten question based on the previous conversation.",
    )


class RouteQuery(BaseModel):
    """
    2. 쿼리를 보고 컨텍스트 검색이 필요한지 결정하는 노드에 사용되는 LLM 모델 출력 구조.
    """

    decision: Literal["context required", "context not required"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )


class CheckContextLatest(BaseModel):
    data_source: str = Field(..., description="Data source")
    page_id: str = Field(..., description="Page ID")
    last_edited_time: str = Field(..., description="Last edited time")


class CheckContextLatestList(BaseModel):
    """
    4. 컨텍스트의 최신성을 검증하는 노드에 사용되는 LLM 모델 출력 구조.
    """

    data: List[CheckContextLatest] = Field(
        ..., description="List of page IDs and their last edited times."
    )
