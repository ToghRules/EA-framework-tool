"""
Auth Module — Login & Register UI
Renders the authentication screen when the user is not logged in.
"""

import streamlit as st
from database import register_user, login_user

AUTH_CSS = """
<style>
.auth-container {
    max-width: 420px;
    margin: 3rem auto;
    background: linear-gradient(135deg, #1a1d27 0%, #13151f 100%);
    border: 1px solid #2a2d3e;
    border-radius: 16px;
    padding: 2.5rem 2rem;
}
.auth-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    color: #e8e8e8;
    margin-bottom: 0.2rem;
    text-align: center;
}
.auth-subtitle {
    font-size: 0.82rem;
    color: #6c7599;
    text-align: center;
    margin-bottom: 1.8rem;
}
.auth-divider {
    border: none;
    border-top: 1px solid #2a2d3e;
    margin: 1.5rem 0;
}
</style>
"""


def show_auth_page():
    """
    Render the login/register page.
    Sets st.session_state.user on successful login.
    Returns True if the user is now authenticated, False otherwise.
    """
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    
    _, col, _ = st.columns([1, 2, 1])

    with col:
        st.markdown("<div class='auth-title'>🏛️ EA Framework Selector</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-subtitle'>Master's Thesis Prototype · WSM Engine</div>", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username", placeholder="your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login →", key="btn_login", use_container_width=True):
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    success, user, msg = login_user(username, password)
                    if success:
                        st.session_state.user = user
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            new_username = st.text_input("Username", key="reg_username", placeholder="choose a username")
            new_email    = st.text_input("Email",    key="reg_email",    placeholder="you@example.com")
            new_pass     = st.text_input("Password", type="password", key="reg_password", placeholder="min. 6 characters")
            new_pass2    = st.text_input("Confirm password", type="password", key="reg_password2", placeholder="repeat password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create account →", key="btn_register", use_container_width=True):
                if not all([new_username, new_email, new_pass, new_pass2]):
                    st.error("Please fill in all fields.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                else:
                    success, msg = register_user(new_username, new_email, new_pass)
                    if success:
                        st.success(msg + " You can now log in.")
                    else:
                        st.error(msg)

    return "user" in st.session_state and st.session_state.user is not None
