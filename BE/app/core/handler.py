from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exception import ExceptionCase, CustomException


def set_error_handlers(app: FastAPI):

    @app.exception_handler(CustomException)
    async def custom_exception_handler(
        request: Request, exception: CustomException
    ) -> JSONResponse:
        """
        클라이언트 요청에 따라 발생하는 400번대 응답.
        """
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "code": exception.code,
                "message": exception.msg,
                "detail": exception.detail,
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error_exception_handler(
        request: Request, exception: Exception
    ) -> JSONResponse:
        """
        서버에서 발생한 500번대 응답.
        """
        return JSONResponse(
            status_code=ExceptionCase.UNEXPECTED_ERROR.status_code,
            content={
                "code": ExceptionCase.UNEXPECTED_ERROR.code,
                "message": ExceptionCase.UNEXPECTED_ERROR.msg,
                "detail": str(exception),
            },
        )
