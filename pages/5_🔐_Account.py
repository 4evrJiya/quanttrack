"""
QuantTrack — Account Page (Signup / Login / Logout / Watchlist / History)
"""

import streamlit as st
import pandas as pd
from auth import create_user, verify_user
from watchlist import get_watchlist, add_to_watchlist, remove_from_watchlist
from history import get_history

st.set_page_config(page_title="Account - QuantTrack", page_icon="🔐", layout="wide")

st.title("🔐 Account")

if "logged_in_user" in st.session_state:
    user_id = st.session_state["logged_in_user"]
    st.success(f"You're logged in as **{st.session_state['logged_in_username']}**")

    st.subheader("⭐ Your Watchlist")
    watchlist = get_watchlist(user_id)

    if not watchlist:
        st.info("Your watchlist is empty. Add a stock below.")
    else:
        for stock in watchlist:
            col1, col2 = st.columns([4, 1])
            col1.write(stock)
            if col2.button("Remove", key=f"remove_{stock}"):
                remove_from_watchlist(user_id, stock)
                st.rerun()

    new_ticker = st.text_input("Add a ticker to your watchlist", key="new_watchlist_ticker")
    if st.button("Add to Watchlist"):
        if new_ticker:
            success, message = add_to_watchlist(user_id, new_ticker)
            st.success(message) if success else st.warning(message)
            st.rerun()

    st.divider()
    st.subheader("📜 Your Backtest History")
    history_rows = get_history(user_id)

    if not history_rows:
        st.info("No saved backtests yet. Run a backtest and save it to see it here.")
    else:
        history_df = pd.DataFrame(
            history_rows,
            columns=["Ticker", "Strategy", "Total Return (%)", "Sharpe Ratio", "Max Drawdown (%)", "Run At"]
        )
        st.dataframe(history_df, use_container_width=True)

    st.divider()
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
                st.session_state["logged_in_user"] = result
                st.session_state["logged_in_username"] = login_username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error(result)

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