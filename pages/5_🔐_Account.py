"""
QuantTrack — Account Page (Signup / Login / Logout)
"""

import streamlit as st
from auth import create_user, verify_user

st.set_page_config(page_title="Account - QuantTrack", page_icon="🔐", layout="wide")

st.title("🔐 Account")

# --- If already logged in, show that instead of login/signup forms ---
if "logged_in_user" in st.session_state:
    st.success(f"You're logged in as **{st.session_state['logged_in_username']}**")
    st.write("Head to the Backtest, Portfolio, or Forecast pages — your results can now be saved to your history and watchlist.")

    if st.button("Log Out"):
        del st.session_state["logged_in_user"]
        del st.session_state["logged_in_username"]
        st.rerun()

else:
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        st.subheader("Log In")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In"):
            success, result = verify_user(login_username, login_password)
            if success:
                st.session_state["logged_in_user"] = result  # this is the user_id
                st.session_state["logged_in_username"] = login_username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error(result)  # result is the error message in this case

    with tab_signup:
        st.subheader("Sign Up")
        signup_username = st.text_input("Choose a username", key="signup_username")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Choose a password", type="password", key="signup_password", help="At least 6 characters")

        if st.button("Create Account"):
            if not signup_username or not signup_email or not signup_password:
                st.error("Please fill in all fields.")
            else:
                success, message = create_user(signup_username, signup_email, signup_password)
                if success:
                    st.success(message + " You can now log in using the Log In tab.")
                else:
                    st.error(message)