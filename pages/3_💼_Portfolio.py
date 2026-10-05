"""
QuantTrack — Multi-Stock Portfolio Comparison Page
"""

import streamlit as st

from config import MAX_PORTFOLIO_STOCKS
from strategies import STRATEGY_REGISTRY
from portfolio import run_portfolio_backtest, build_portfolio_returns, compare_portfolio_vs_best_single
from history import save_portfolio_result

st.set_page_config(page_title="Portfolio - QuantTrack", page_icon="💼", layout="wide")

from ui_helpers import apply_custom_css, render_sidebar_status
apply_custom_css()
render_sidebar_status()

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
        st.session_state["portfolio_display"] = None
        st.error("Couldn't fetch valid data for any of the entered tickers. Check the symbols.")
    else:
        comparison = compare_portfolio_vs_best_single(portfolio_results, portfolio_df)
        st.session_state["portfolio_display"] = {
            "tickers": tickers,
            "strategy": portfolio_strategy_choice,
            "portfolio_df": portfolio_df,
            "comparison": comparison
        }

if "portfolio_display" in st.session_state and st.session_state["portfolio_display"] is not None:
    d = st.session_state["portfolio_display"]

    st.subheader("Portfolio Equity Curve")
    st.line_chart(d["portfolio_df"]["Portfolio_Equity"])

    st.subheader("Portfolio vs Best Single Stock")
    st.table(d["comparison"])

    st.info("💡 Notice: diversification often means *lower* total return than the single best stock, but usually with a *smaller* worst-case drawdown. That tradeoff is the whole point of spreading your money across multiple stocks.")

    if "logged_in_user" in st.session_state:
        if st.button("💾 Save this portfolio result to my history"):
            portfolio_metrics = d["comparison"]["Portfolio (5 stocks)"].to_dict()
            save_portfolio_result(st.session_state["logged_in_user"], d["tickers"], d["strategy"], portfolio_metrics)
            st.success("Saved to your history! View it on the Account page.")
    else:
        st.caption("🔒 Log in on the Account page to save this result to your history.")

elif "portfolio_display" not in st.session_state:
    st.info("Enter up to 5 tickers above, then click **Run Portfolio Backtest** to begin.")