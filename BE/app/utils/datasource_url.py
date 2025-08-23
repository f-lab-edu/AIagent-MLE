"""
데이터소스(ex. notion)의 url을 생성하거나 page_id를 추출하는 전처리 모듈
"""

from db.models import DataSource
from core.exception import CustomException, ExceptionCase


def context_url(datasource: DataSource, page_id: str) -> str:
    if datasource == DataSource.NOTION:
        return f"https://www.notion.so/{page_id}"
    else:
        raise CustomException(
            exception_case=ExceptionCase.INVALID_INPUT, detail="Invalid datasource"
        )


def extract_page_id(url: str, datasource: DataSource) -> str:
    try:
        if datasource == DataSource.NOTION:
            return url.split("?")[0].split("/")[-1].split("-")[-1]
        else:
            raise CustomException(
                exception_case=ExceptionCase.INVALID_INPUT, detail="Invalid datasource"
            )
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.INVALID_INPUT,
            detail=f"Unexpected url format.: {e}",
        )
