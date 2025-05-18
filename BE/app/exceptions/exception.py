from enum import Enum
from fastapi import HTTPException
from fastapi import status


class ExceptionCase(Enum):
    INVALID_INPUT = (status.HTTP_400_BAD_REQUEST, "1100", "Invalid Input")

    UNEXPECTED_ERROR = (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "9001",
        "Unexpected Error",
    )

    def __init__(self, status_code: int, error_code: str, msg: str):
        self._status_code = status_code
        self._error_code = error_code
        self._msg = msg

    @property
    def status_code(self):
        return self._status_code

    @property
    def code(self):
        return self._error_code

    @property
    def msg(self):
        return self._msg


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
