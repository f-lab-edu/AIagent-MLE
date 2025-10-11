import streamlit as st
from api.auth import join
from navigations.user_group.user_group import init_user_grouo_list_session


st.title("Join")

authority_level = st.session_state["authority_level"]
if authority_level != "admin":
    st.error("관리자 권한이 필요합니다.")
    st.stop()

if "user_group_dict" not in st.session_state:
    init_user_grouo_list_session()

user_group_dict = st.session_state["user_group_dict"]


email = st.text_input("Email")
password = st.text_input("Password", type="password")
name = st.text_input("Name")
selected_user_group = st.selectbox(
    "User Group",
    options=["[Select User Group]"]
    + [
        f"{name} ({user_group_dict[name]['authority_level']})"
        for name in user_group_dict.keys()
    ],
)

if st.button("Join"):
    if not email or not password or not name or not selected_user_group:
        st.warning("모든 항목을 입력해주세요.")
    else:
        selected_user_group_name = selected_user_group.split(" (")[0]
        selected_user_group_id = user_group_dict[selected_user_group_name]["id"]
        response = join(email, password, name, selected_user_group_id)
        print(response)
        if response and response.status == "Success":
            st.success("회원가입이 완료되었습니다.")
            st.rerun()
        elif response and response.status == "Fail":
            st.error(response.message)
            st.stop()
