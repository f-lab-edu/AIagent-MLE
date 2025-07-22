import uuid
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field

"""
metadata
    - authority_group: list[str] = ['*']
    - content: str
    - datasource: str (ex. notion)
    - updated_at: datetime
    - page_id: str
"""


class Document(BaseModel):
    content: Optional[Annotated[str, "document content"]] = None
    datasource: Optional[Annotated[str, "datasource (ex. notion)"]] = None
    updated_at: Optional[Annotated[str, "updated_at"]] = None
    page_id: Optional[Annotated[str, "page_id of datasource"]] = None


class DocumentMetadata(Document):
    authority_group: Optional[Annotated[List[str], "authority_group"]] = None


class DocumentInput(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    embedding: List[float]
    metadata: DocumentMetadata = Field(default_factory=dict)


class DocumentOutput(BaseModel):
    id: str
    score: Optional[float] = None
    metadata: DocumentMetadata = Field(default_factory=dict)
