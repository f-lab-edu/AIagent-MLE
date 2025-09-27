"""
인증 관련 API(로그인, 회원가입) 통신을 담당하는 모듈입니다.
"""

from api.client import client
from core.exception import get_exception_message
from schema.response import ResponseModel
import streamlit as st


def login(email: str, password: str) -> ResponseModel:
    """
    사용자의 이메일과 비밀번호를 받아 백엔드에 로그인을 요청합니다.

    Args:
        email (str): 사용자 이메일
        password (str): 사용자 비밀번호

    Returns:
        ResponseModel: 로그인 성공 시 성공 상태와 `access_token`을 포함한 응답 객체를 반환합니다.
                       실패 시 실패 상태와 에러 메시지를 포함한 응답 객체를 반환합니다.
    """
    try:
        data = {"email": email, "password": password}
        response = client.post("/auth/login", json=data)
        response_json = response.json()
        if response.status_code == 200:
            return ResponseModel(
                status="Success",
                detail=response_json.get("detail"),
                data=response_json["data"],
            )
        else:
            # API에서 정의한 에러 케이스에 맞는 사용자 친화적 메시지를 가져옴
            error_case = response_json["message"]
            error_message = get_exception_message(error_case)
            return ResponseModel(
                status="Fail",
                detail=response_json.get("detail"),
                message=error_message,
                error_code=response_json.get("code"),
            )

    except Exception as e:
        # 네트워크 오류 등 예기치 못한 예외 처리
        st.error(str(e))


def join(email: str, password: str, name: str, user_group_id: str):
    """
    새로운 사용자를 등록(회원가입)하기 위해 백엔드에 요청합니다.
    이 기능은 관리자 등 특정 권한을 가진 사용자만 수행할 수 있으며,
    요청 시 헤더에 인증 토큰이 필요합니다.

    Args:
        email (str): 신규 사용자 이메일
        password (str): 신규 사용자 비밀번호
        name (str): 신규 사용자 이름
        user_group_id (str): 신규 사용자가 속할 그룹의 ID
    """
    try:
        data = {
            "email": email,
            "password": password,
            "name": name,
            "user_group_id": user_group_id,
        }
        # 회원가입 요청은 관리자 권한이 필요하므로, 현재 로그인된 사용자의 토큰을 헤더에 담아 전송
        response = client.post(
            "auth/join",
            json=data,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"},
        )
        response_json = response.json()
        if response.status_code == 200:
            return ResponseModel(status="Success", data=response_json["data"])
        else:
            error_case = response_json["message"]
            error_message = get_exception_message(error_case)
            st.error(error_message)
            st.stop()

    except Exception as e:
        st.error(str(e))
