"""
애플리케이션의 메인 페이지 역할을 하는 로그인 페이지 스크립트입니다.

- 사용자가 처음 접속했을 때 보여지는 페이지입니다.
- 이미 로그인된 사용자(세션에 access_token이 있는 경우)는 자동으로 다른 페이지로 리디렉션됩니다.
- 사용자로부터 이메일과 비밀번호를 입력받아 백엔드에 로그인을 요청합니다.
- 로그인 성공 시, 발급받은 토큰을 세션에 저장하고 지정된 페이지로 이동합니다.
- 로그인 실패 시, 사용자에게 에러 메시지를 표시합니다.
"""

import streamlit as st
from api.auth import login

# --- 페이지 시작 시 실행되는 로직 ---

# 1. 자동 리디렉션: 이미 로그인되어 있는지 확인
# st.session_state에 'access_token'이 존재하면, 사용자는 이미 로그인된 상태입니다.
if "access_token" in st.session_state:
    # 로그인된 사용자는 바로 업로드 페이지로 이동시킵니다.
    st.switch_page("pages/1_Upload.py")

# --- 로그인 UI 구성 ---

st.title("로그인")

# 사용자 입력을 받기 위한 텍스트 필드를 생성합니다.
email = st.text_input("Email")
password = st.text_input(
    "Password", type="password"
)  # type="password"로 입력 내용 가리기

# --- 로그인 버튼 클릭 시 실행되는 로직 ---

if st.button("로그인"):
    # 1. 입력 값 검증
    if not email or not password:
        st.warning("Email과 비밀번호를 모두 입력해주세요.")
    else:
        # 2. API를 통해 로그인 요청
        response = login(email, password)

        # 3. 로그인 결과 처리
        if response and response.status == "Success":
            # 성공 시: access_token을 세션 상태에 저장
            st.session_state["access_token"] = response.data["access_token"]
            # 로그인 후 이동할 기본 페이지로 전환
            st.switch_page("pages/1_Upload.py")
        elif response:
            # 실패 시: API로부터 받은 에러 메시지를 화면에 표시
            st.error(response.message)
            st.stop()  # 스크립트 실행을 중지하여 더 이상 진행되지 않도록 함
        # response가 None인 경우는 login 함수 내부에서 예외 처리된 경우
