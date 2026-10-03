"""
QuantTrack — Home Page
"""

import streamlit as st

st.set_page_config(page_title="QuantTrack", page_icon="📈", layout="wide")

st.title("📈 Welcome to QuantTrack")
st.subheader("Test trading strategies on real data — before risking real money")

st.markdown("""
QuantTrack lets you see how a trading strategy *would have* performed historically,
compares spreading your money across multiple stocks versus picking just one,
and gives you a short-term price forecast — all backed by real stock market data.

**New here? Use the sidebar on the left to get started:**
- 🔐 **Account** — sign up or log in to save your backtests and build a watchlist
- 📊 **Backtest** — test a strategy on a single stock
- 💼 **Portfolio** — compare a diversified portfolio against picking one stock
- 🔮 **Forecast** — see a 30-day price projection
- 📚 **Learn** — new to trading or investing? Start here first.
""")

st.divider()
st.caption("⚠️ Educational tool only. Not financial advice. Past performance does not guarantee future results.")