import uuid
from typing import Optional, List, Annotated, TypeVar, Generic
from pydantic import BaseModel, Field

"""
metadata
    - user_groups: list[str] = ['*']
    - content: str
    - datasource: str (ex. notion)
    - updated_at: datetime
    - page_id: str
"""
T = TypeVar("T")


class CustomAPIResponse(BaseModel, Generic[T]):
    detail: str | None = ""
    data: T = "Success"


class Document(BaseModel):
    content: Optional[Annotated[str, "document content"]] = None
    datasource: Optional[Annotated[str, "datasource (ex. notion)"]] = None
    updated_at: Optional[Annotated[str, "updated_at"]] = None
    page_id: Optional[Annotated[str, "page_id of datasource"]] = None


class DocumentMetadata(Document):
    user_groups: Optional[Annotated[List[str], "user_groups"]] = None


class DocumentInput(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    embedding: List[float]
    metadata: DocumentMetadata = Field(default_factory=dict)


class DocumentOutput(BaseModel):
    id: str
    score: Optional[float] = None
    metadata: DocumentMetadata = Field(default_factory=dict)
