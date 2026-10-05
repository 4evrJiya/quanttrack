"""
QuantTrack — Home Page
"""

import streamlit as st

st.set_page_config(page_title="QuantTrack", page_icon="assets/favicon.png" if False else "📈", layout="wide")

from ui_helpers import apply_custom_css, render_sidebar_status
apply_custom_css()
render_sidebar_status()

st.title("QuantTrack")
st.subheader("Test trading strategies on real market data — before risking real money")

st.markdown("""
QuantTrack lets you see how a trading strategy would have performed historically,
compares spreading your capital across multiple stocks versus concentrating in one,
and projects short-term price trends — all backed by real market data.
""")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Backtest")
    st.caption("Test a strategy on a single stock using real historical price data.")

with col2:
    st.markdown("### Portfolio")
    st.caption("Compare a diversified portfolio against concentrating in one stock.")

with col3:
    st.markdown("### Forecast")
    st.caption("View a 30-day price projection based on historical patterns.")

st.divider()
st.markdown("**New here?** Visit **Learn** in the sidebar for a plain-language explanation of every concept used in this platform. Visit **Account** to create a free account and save your results.")

st.caption(":material/warning: Educational tool only. Not financial advice. Past performance does not guarantee future results.")