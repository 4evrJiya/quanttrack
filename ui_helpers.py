"""
UI Helpers — shared styling and sidebar elements used across every page.
"""

import streamlit as st


def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .block-container {
            padding-top: 2rem;
        }

        h1 {
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }
        h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }

        div.stButton > button {
            border-radius: 6px;
            font-weight: 600;
            border: 1px solid #2D333B;
            transition: all 0.15s ease;
        }
        div.stButton > button:hover {
            border-color: #00C896;
            color: #00C896;
        }
        div.stButton > button[kind="primary"] {
            background-color: #00C896;
            border: none;
            color: #0E1117;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #00E3AD;
            color: #0E1117;
        }

        [data-testid="stMetric"] {
            background-color: #1C2128;
            border: 1px solid #2D333B;
            border-radius: 12px;
            padding: 16px 18px;
        }
        [data-testid="stMetricLabel"] {
            font-weight: 500;
            opacity: 0.75;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            border-radius: 6px 6px 0 0;
        }

        [data-testid="stSidebar"] {
            background-color: #151922;
            border-right: 1px solid #2D333B;
        }

        .brand-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 4px;
        }
        .brand-logo {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, #00C896, #00E3AD);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #0E1117;
            font-size: 18px;
        }
        .brand-name {
            font-weight: 800;
            font-size: 20px;
            letter-spacing: -0.02em;
        }
        </style>
    """, unsafe_allow_html=True)


def render_brand_header():
    st.markdown("""
        <div class="brand-header">
            <div class="brand-logo">Q</div>
            <div class="brand-name">QuantTrack</div>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar_status():
    with st.sidebar:
        render_brand_header()
        st.divider()
        if "logged_in_username" in st.session_state:
            st.caption(f":material/account_circle: Logged in as **{st.session_state['logged_in_username']}**")
        else:
            st.caption(":material/account_circle: Not logged in")