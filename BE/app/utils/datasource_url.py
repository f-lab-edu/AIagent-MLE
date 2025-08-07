"""
데이터소스(ex. notion)의 url을 생성하거나 page_id를 추출하는 전처리 모듈
"""

from typing import Literal
from core.exception import CustomException, ExceptionCase


def context_url(datasource: Literal["notion"], page_id: str) -> str:
    if datasource == "notion":
        return f"https://www.notion.so/{page_id}"
    else:
        raise CustomException(
            exception_case=ExceptionCase.INVALID_INPUT, detail="Invalid datasource"
        )


def extract_page_id(url: str, datasource: Literal["notion"]) -> str:
    if datasource == "notion":
        return url.split("?")[0].split("/")[-1].split("-")[-1]
