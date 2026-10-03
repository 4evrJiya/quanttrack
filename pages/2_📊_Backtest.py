"""
QuantTrack — Single-Stock Backtest Page
"""

import streamlit as st
import pandas as pd

from data_ingestion import fetch_stock_data
from strategies import STRATEGY_REGISTRY
from regime_detector import get_regime_summary
from analytics import calculate_equity_curve, calculate_metrics, calculate_buy_and_hold_benchmark
from history import save_backtest

st.set_page_config(page_title="Backtest - QuantTrack", page_icon="📊", layout="wide")

METRIC_TOOLTIPS = {
    "Total Return (%)": "The overall percentage gain or loss over the selected period.",
    "Sharpe Ratio": "Return earned per unit of risk taken. Above 1 is generally good; above 2 is very good.",
    "Max Drawdown (%)": "The largest peak-to-trough decline — the worst loss you'd have experienced at any point.",
    "Volatility (%)": "How much the strategy's value swings day to day, annualized.",
    "Win Rate (%)": "The percentage of active trading days that were profitable."
}


def display_metrics_cards(metrics):
    cols = st.columns(5)
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label, value, help=METRIC_TOOLTIPS.get(label, ""))


st.title("📊 Single-Stock Backtest")
st.caption("Test a trading strategy on real historical data for one stock.")

col_input1, col_input2, col_input3 = st.columns([2, 2, 1])
with col_input1:
    ticker = st.text_input("Stock ticker", "RELIANCE.NS", help="e.g. RELIANCE.NS for NSE, AAPL for US stocks")
with col_input2:
    strategy_choice = st.selectbox("Strategy", list(STRATEGY_REGISTRY.keys()))
with col_input3:
    st.write("")
    st.write("")
    run_button = st.button("Run Backtest", use_container_width=True)

# When Run Backtest is clicked, COMPUTE everything and STORE it in session_state
if run_button:
    data = fetch_stock_data(ticker)

    if data is None:
        st.session_state["backtest_display"] = None
        st.error(f"No data found for ticker '{ticker}'. Check the symbol.")
    else:
        strategy_func = STRATEGY_REGISTRY[strategy_choice]
        result = strategy_func(data)
        equity_result = calculate_equity_curve(result)
        metrics = calculate_metrics(equity_result)
        regime_info = get_regime_summary(data)
        benchmark = calculate_buy_and_hold_benchmark(data)

        # Save everything needed to redisplay this result, even after other buttons are clicked later
        st.session_state["backtest_display"] = {
            "ticker": ticker,
            "strategy": strategy_choice,
            "data": data,
            "equity_result": equity_result,
            "metrics": metrics,
            "regime_info": regime_info,
            "benchmark": benchmark
        }

# ALWAYS render from session_state, not directly from run_button —
# this is what survives the "Save to History" button's own rerun
if "backtest_display" in st.session_state and st.session_state["backtest_display"] is not None:
    d = st.session_state["backtest_display"]

    regime_color = "🟢" if d["regime_info"]["regime"] == "Trending" else "🟡"
    st.info(f"{regime_color} **Market Regime:** {d['regime_info']['regime']} (ADX: {d['regime_info']['adx']:.2f}) — **Recommended:** {d['regime_info']['recommendation']}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Price Chart")
        st.line_chart(d["data"]["Close"])

    comparison_chart = d["equity_result"][["Equity_Curve"]].join(d["benchmark"])
    comparison_chart.columns = ["Strategy", "Buy & Hold Benchmark"]

    with col2:
        st.subheader("Strategy vs. Buy & Hold")
        st.line_chart(comparison_chart)

    benchmark_return = round((d["benchmark"]["Benchmark_Equity"].iloc[-1] - 1) * 100, 2)
    strategy_return = d["metrics"]["Total Return (%)"]

    if strategy_return > benchmark_return:
        st.success(f"✅ Strategy outperformed Buy & Hold by {round(strategy_return - benchmark_return, 2)} percentage points")
    else:
        st.warning(f"⚠️ Strategy underperformed Buy & Hold by {round(benchmark_return - strategy_return, 2)} percentage points")

    st.subheader("Performance Metrics")
    display_metrics_cards(d["metrics"])
    st.caption(f"Buy & Hold Benchmark: {benchmark_return}% total return | 0.1% transaction cost applied per trade")

    if "logged_in_user" in st.session_state:
        if st.button("💾 Save this backtest to my history"):
            save_backtest(st.session_state["logged_in_user"], d["ticker"], d["strategy"], d["metrics"])
            st.success("Saved to your history! View it on the Account page.")
    else:
        st.caption("🔒 Log in on the Account page to save this backtest to your history.")

elif "backtest_display" not in st.session_state:
    st.info("Enter a ticker and strategy above, then click **Run Backtest** to begin.")