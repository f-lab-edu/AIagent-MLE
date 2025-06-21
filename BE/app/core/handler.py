import logging
from fastapi import status
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exception import ExceptionCase, CustomException

logger = logging.getLogger(__name__)


def set_error_handlers(app: FastAPI):

    @app.exception_handler(CustomException)
    async def custom_exception_handler(
        request: Request, exception: CustomException
    ) -> JSONResponse:
        """
        사전에 정의된 에러
        """

        if exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            # 500 server 에러일 경우: logger.exception
            logger.exception(
                f"Server error: {exception.code} - {exception.msg} - {exception.detail}"
            )
        else:
            # 500 server 이외의 client 에러일 경우: logger.warning
            logger.warning(
                f"Client error: {exception.code} - {exception.msg} - {exception.detail}"
            )
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
        서버에서 발생한 예측되지 않은 예외.
        """
        logger.exception(f"Unexpected error: {exception}")
        return JSONResponse(
            status_code=ExceptionCase.UNEXPECTED_ERROR.status_code,
            content={
                "code": ExceptionCase.UNEXPECTED_ERROR.code,
                "message": ExceptionCase.UNEXPECTED_ERROR.msg,
                "detail": str(exception),
            },
        )
