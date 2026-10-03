"""
QuantTrack — Multi-Stock Portfolio Comparison Page
"""

import streamlit as st

from config import MAX_PORTFOLIO_STOCKS
from strategies import STRATEGY_REGISTRY
from portfolio import run_portfolio_backtest, build_portfolio_returns, compare_portfolio_vs_best_single

st.set_page_config(page_title="Portfolio - QuantTrack", page_icon="💼", layout="wide")

st.title("💼 Multi-Stock Portfolio Comparison")
st.caption(f"Compare an equally-weighted portfolio of up to {MAX_PORTFOLIO_STOCKS} stocks against the single best performer.")

tickers_input = st.text_input(
    f"Enter up to {MAX_PORTFOLIO_STOCKS} tickers, comma-separated",
    "RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ITC.NS"
)
portfolio_strategy_choice = st.selectbox("Choose strategy for portfolio", list(STRATEGY_REGISTRY.keys()))
portfolio_button = st.button("Run Portfolio Backtest")

if portfolio_button:
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    strat_func = STRATEGY_REGISTRY[portfolio_strategy_choice]

    with st.spinner("Running backtest across all stocks..."):
        portfolio_results = run_portfolio_backtest(tickers, strat_func)
        portfolio_df = build_portfolio_returns(portfolio_results)

    if portfolio_df is None:
        st.error("Couldn't fetch valid data for any of the entered tickers. Check the symbols.")
    else:
        comparison = compare_portfolio_vs_best_single(portfolio_results, portfolio_df)

        st.subheader("Portfolio Equity Curve")
        st.line_chart(portfolio_df["Portfolio_Equity"])

        st.subheader("Portfolio vs Best Single Stock")
        st.table(comparison)

        st.info("💡 Notice: diversification often means *lower* total return than the single best stock, but usually with a *smaller* worst-case drawdown. That tradeoff is the whole point of spreading your money across multiple stocks.")
else:
    st.info("Enter up to 5 tickers above, then click **Run Portfolio Backtest** to begin.")