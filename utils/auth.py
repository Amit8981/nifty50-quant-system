"""
Authentication and Session Security Module.
Provides secure SHA-256 password verification, session management,
and a modern login interface with role-based access control.
"""

import hashlib
from typing import Dict, Any, Optional
import streamlit as st

# Predefined default credentials with SHA-256 hashed passwords
# Admin: admin / admin@nifty50
# Investor: investor / invest@nifty50
DEFAULT_USERS = {
    "admin": {
        "name": "Portfolio Admin",
        "password_hash": hashlib.sha256("admin@nifty50".encode("utf-8")).hexdigest(),
        "role": "admin",
        "email": "admin@niftyquant.local",
    },
    "investor": {
        "name": "Institutional Investor",
        "password_hash": hashlib.sha256("invest@nifty50".encode("utf-8")).hexdigest(),
        "role": "viewer",
        "email": "investor@client.local",
    },
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    username_clean = username.strip().lower()
    if username_clean in DEFAULT_USERS:
        user_info = DEFAULT_USERS[username_clean]
        if user_info["password_hash"] == hash_password(password.strip()):
            return {
                "username": username_clean,
                "name": user_info["name"],
                "role": user_info["role"],
                "email": user_info["email"],
            }
    return None


def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None


def logout():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()


def render_login_screen() -> bool:
    """
    Renders a centered, sleek login dialog if the user is not authenticated.
    Returns True if authenticated, False otherwise.
    """
    init_session_state()

    if st.session_state.authenticated:
        return True

    # Center-aligned Login Container
    _, col, _ = st.columns([1, 1.3, 1])

    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: linear-gradient(145deg, #1E222D, #262B36); padding: 32px 36px; border-radius: 12px; border: 1px solid #363C4E; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                <div style="text-align: center; margin-bottom: 24px;">
                    <span style="font-size: 42px;">🔐</span>
                    <h2 style="color: #FFFFFF; margin-top: 10px; font-size: 1.6rem;">NIFTY 50 Quant Portal</h2>
                    <p style="color: #A0AEC0; font-size: 0.88rem;">Secure Quantitative Strategy & Validation System</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username_input = st.text_input("User ID / Username", placeholder="Enter username (e.g. admin or investor)")
            password_input = st.text_input("Password", type="password", placeholder="Enter password")
            submit_login = st.form_submit_button("Sign In to Portal", use_container_width=True)

            if submit_login:
                user = authenticate(username_input, password_input)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Please check your credentials.")

        # Collapsible hint for convenience
        with st.expander("🔑 View Demo Credentials"):
            st.markdown(
                """
                - **Administrator (Full Access + Admin Console)**:
                  - User ID: `admin`
                  - Password: `admin@nifty50`
                - **Investor / Client (Analytics View)**:
                  - User ID: `investor`
                  - Password: `invest@nifty50`
                """
            )

        st.markdown("</div>", unsafe_allow_html=True)

    return False
