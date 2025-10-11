import streamlit as st

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "authority_level" not in st.session_state:
    st.session_state["authority_level"] = None
if "user_group_list" not in st.session_state:
    st.session_state["user_group_list"] = None


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


authority_level = st.session_state["authority_level"]


login_page = st.Page(
    "navigations/account/login.py", title="Log in", icon=":material/login:"
)

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

join_page = st.Page(
    "navigations/account/join.py",
    title="Join",
    icon=":material/join:",
    default=(authority_level == "admin"),
)

user_group_page = st.Page(
    "navigations/user_group/user_group.py",
    title="User Group",
    icon=":material/group:",
)


if st.session_state["access_token"]:
    pg = st.navigation(
        {"Account": [logout_page, join_page], "User Group": [user_group_page]}
    )
else:
    pg = st.navigation(
        {
            "Account": [login_page],
        }
    )

pg.run()
