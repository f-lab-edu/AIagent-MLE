import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentInput(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentOutput(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
