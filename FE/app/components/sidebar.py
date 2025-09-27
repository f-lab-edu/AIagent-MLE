"""
Streamlit 앱의 사이드바 UI 컴포넌트를 정의하는 모듈입니다.

이 모듈은 여러 페이지에서 공통으로 사용될 수 있는 사이드바 기능을 포함합니다.
예: 로그인 후 표시되는 공통 메뉴, 로그아웃 버튼 등
"""

import streamlit as st


def authenticated_sidebar():
    """
    로그인한 사용자를 위한 공통 사이드바를 표시합니다.

    이 사이드바에는 다음 기능이 포함됩니다:
    - '메뉴'라는 제목
    - '로그아웃' 버튼: 클릭 시 st.session_state를 초기화하고 로그인 페이지로 리디렉션합니다.
    """
    st.sidebar.title("메뉴")
    if st.sidebar.button("로그아웃"):
        # 로그아웃 시, 세션에 저장된 모든 정보(예: access_token)를 삭제합니다.
        # list()로 감싸서 순회 중 딕셔너리 변경에 따른 오류를 방지합니다.
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # 모든 세션 정보가 삭제된 후, 사용자를 로그인 페이지로 보냅니다.
        st.switch_page("1_Login.py")


# def chat_sidebar():
#     """채팅 페이지 전용 사이드바"""
#     authenticated_sidebar()  # 공통 사이드바 포함

#     st.sidebar.divider()
#     st.sidebar.header("채팅 관리")

#     # 새 채팅 시작 버튼
#     if st.sidebar.button("새 채팅 시작하기"):
#         if "messages" in st.session_state:
#             st.session_state.messages = []
#         st.rerun()

#     # 현재 채팅 저장 기능
#     if st.session_state.get("messages"):
#         st.sidebar.header("현재 대화 저장")
#         chat_title = st.sidebar.text_input("대화 제목을 입력하세요.")
#         if st.sidebar.button("저장하기"):
#             if chat_title:
#                 try:
#                     save_chat_history(chat_title, st.session_state.messages)
#                     st.sidebar.success(
#                         f"'{chat_title}' 제목으로 대화가 저장되었습니다."
#                     )
#                 except Exception as e:
#                     st.sidebar.error(f"저장 중 오류 발생: {e}")
#             else:
#                 st.sidebar.warning("대화 제목을 먼저 입력해주세요.")
