import logging
from fastapi import FastAPI
from core.handler import set_error_handlers
from core.exception import CustomException, ExceptionCase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI()

set_error_handlers(app)


@app.get("/")
def test_exception():
    raise CustomException(exception_case=ExceptionCase.UNEXPECTED_ERROR, detail="test")


@app.get("/unexpected")
def test_unexpected_exception():
    # from a import b

    pass