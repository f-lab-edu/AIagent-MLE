from fastapi import FastAPI
from exceptions.handler import set_error_handlers
from exceptions.exception import CustomException, ExceptionCase

app = FastAPI()

set_error_handlers(app)


@app.get("/")
def test_exception():
    raise CustomException(ExceptionCase.INVALID_INPUT, detail="exception test")


@app.get("/unexpected")
def test_unexpected_exception():
    # from a import b
    pass
