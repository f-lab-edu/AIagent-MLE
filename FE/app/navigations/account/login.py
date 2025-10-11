import streamlit as st
from api.auth import login
from utils.auth import get_current_user_authority_level

st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not email or not password:
        st.warning("이메일과 비밀번호를 모두 입력해주세요.")
    else:
        response = login(email, password)

        if response and response.status == "Success":
            st.session_state["access_token"] = response.data["access_token"]
            st.session_state["authority_level"] = get_current_user_authority_level()
            st.rerun()
        elif response:
            st.error(response.message)
            st.stop()
