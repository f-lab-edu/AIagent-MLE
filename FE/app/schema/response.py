"""
API 응답의 표준 데이터 구조를 정의하는 모듈입니다.

Pydantic의 `BaseModel`을 사용하여 API로부터 받는 응답의 형식을 지정하고,
데이터 유효성 검사 및 타입 힌팅에 활용합니다.
"""

from pydantic import BaseModel
from typing import Literal, Optional


class ResponseModel(BaseModel):
    """
    API 응답의 표준 형식을 나타내는 Pydantic 모델입니다.

    모든 API 응답은 이 구조를 따르도록 하여 일관성을 유지합니다.

    Attributes:
        status (Literal["Success", "Fail"]): API 요청의 성공 또는 실패 상태를 나타냅니다.
        message (Optional[str]): 사용자에게 보여줄 메시지입니다. (예: 에러 메시지)
        detail (Optional[str]): 개발 및 디버깅을 위한 상세 정보입니다.
        data (Optional[dict]): 요청이 성공했을 때 반환되는 실제 데이터입니다.
        error_code (Optional[str]): 에러 발생 시 백엔드에서 정의한 고유 에러 코드입니다.
    """

    status: Literal["Success", "Fail"]
    message: Optional[str] = None
    detail: Optional[str] = None
    data: Optional[dict | list | str] = None
    error_code: Optional[str] = None
