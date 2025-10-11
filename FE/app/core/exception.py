"""
백엔드 API로부터 받은 에러 코드를 사용자 친화적인 메시지로 변환하는 모듈입니다.

API 응답에 포함된 에러 코드(예: "AUTH_LOGIN_ERROR")를 기반으로,
미리 정의된 한글 메시지를 찾아 반환하는 기능을 제공합니다.
"""

from enum import Enum


class ExceptionCase(Enum):
    """
    API 에러 코드와 사용자 메시지, 내부 코드 번호를 매핑하는 Enum 클래스입니다.

    각 멤버는 (사용자에게 보여줄 메시지, 내부 에러 코드) 형태의 튜플 값을 가집니다.
    """

    AUTH_ERROR = ("로그인 중 오류가 발생했습니다.", "1001")
    AUTH_UNAUTHORIZED_ERROR = (
        "인증되지 않은 사용자입니다. 다시 로그인 해주세요.",
        "1002",
    )
    AUTH_INVALID_TOKEN_ERROR = ("인증되지 않은 사용자입니다.", "1003")
    AUTH_LOGIN_ERROR = (
        "로그인에 실패했습니다. Email 또는 Password를 다시 확인해주세요.",
        "1004",
    )
    AUTH_PERMISSION_ERROR = ("admin 권한이 필요합니다.", "1005")
    AUTH_JOIN_ERROR = ("이미 존재하는 사용자입니다.", "1006")

    DB_OP_ERROR = ("데이터베이스 오류가 발생했습니다.", "6002")

    def __init__(self, message: str, error_code: str):
        self._message = message
        self._error_code = error_code

    @property
    def message(self):
        """사용자에게 보여줄 에러 메시지를 반환합니다."""
        return self._message

    @property
    def error_code(self):
        """내부 에러 코드를 반환합니다."""
        return self._error_code


def get_exception_message(error_case: str) -> str:
    """
    API 응답으로 받은 에러 케이스 문자열에 해당하는 사용자 메시지를 반환합니다.

    Args:
        error_case (str): API 응답의 'message' 필드에 담긴 에러 케이스 문자열
                          (예: "AUTH_LOGIN_ERROR")

    Returns:
        str: ExceptionCase에 정의된 사용자 친화적 메시지.
             만약 해당하는 케이스가 없으면 빈 문자열을 반환합니다.
    """
    # 문자열을 기반으로 Enum 멤버를 찾습니다.
    error_enum_member = ExceptionCase._member_map_.get(error_case)
    if error_enum_member:
        return error_enum_member.message
    else:
        # 정의되지 않은 에러 케이스의 경우, 빈 문자열을 반환하여 UI에서 처리하도록 합니다.
        return ""
