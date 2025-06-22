from enum import Enum
from fastapi import HTTPException
from fastapi import status


class ExceptionCase(Enum):
    INVALID_INPUT = (status.HTTP_400_BAD_REQUEST, "1100")

    VECTOR_DB_INIT_ERROR = (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "8001",
    )
    VECTOR_DB_OP_ERROR = (status.HTTP_500_INTERNAL_SERVER_ERROR, "8002")
    UNEXPECTED_ERROR = (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "9001",
    )

    def __init__(self, status_code: int, error_code: str):
        self._status_code = status_code
        self._error_code = error_code

    @property
    def status_code(self):
        return self._status_code

    @property
    def code(self):
        return self._error_code

    @property
    def msg(self):
        return self.name


class CustomException(HTTPException):
    status_code: int
    code: str
    msg: str
    detail: str

    def __init__(
        self,
        exception_case: ExceptionCase = None,
        detail: str = None,
    ):
        super().__init__(status_code=exception_case.status_code, detail=detail)
        self.status_code = exception_case.status_code
        self.code = exception_case.code
        self.msg = exception_case.msg
