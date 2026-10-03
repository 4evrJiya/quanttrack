"""
QuantTrack — Single-Stock Backtest Page
"""

import streamlit as st
import pandas as pd

from data_ingestion import fetch_stock_data
from strategies import STRATEGY_REGISTRY
from regime_detector import get_regime_summary
from analytics import calculate_equity_curve, calculate_metrics, calculate_buy_and_hold_benchmark

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

if run_button:
    data = fetch_stock_data(ticker)

    if data is None:
        st.error(f"No data found for ticker '{ticker}'. Check the symbol.")
    else:
        strategy_func = STRATEGY_REGISTRY[strategy_choice]
        result = strategy_func(data)
        equity_result = calculate_equity_curve(result)
        metrics = calculate_metrics(equity_result)
        regime_info = get_regime_summary(data)

        regime_color = "🟢" if regime_info["regime"] == "Trending" else "🟡"
        st.info(f"{regime_color} **Market Regime:** {regime_info['regime']} (ADX: {regime_info['adx']:.2f}) — **Recommended:** {regime_info['recommendation']}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Price Chart")
            st.line_chart(data["Close"])

        benchmark = calculate_buy_and_hold_benchmark(data)
        comparison_chart = equity_result[["Equity_Curve"]].join(benchmark)
        comparison_chart.columns = ["Strategy", "Buy & Hold Benchmark"]

        with col2:
            st.subheader("Strategy vs. Buy & Hold")
            st.line_chart(comparison_chart)

        benchmark_return = round((benchmark["Benchmark_Equity"].iloc[-1] - 1) * 100, 2)
        strategy_return = metrics["Total Return (%)"]

        if strategy_return > benchmark_return:
            st.success(f"✅ Strategy outperformed Buy & Hold by {round(strategy_return - benchmark_return, 2)} percentage points")
        else:
            st.warning(f"⚠️ Strategy underperformed Buy & Hold by {round(benchmark_return - strategy_return, 2)} percentage points")

        st.subheader("Performance Metrics")
        display_metrics_cards(metrics)
        st.caption(f"Buy & Hold Benchmark: {benchmark_return}% total return | 0.1% transaction cost applied per trade")

        # Store result in session so the "Save to History" button (added later) can access it
        st.session_state["last_backtest"] = {
            "ticker": ticker,
            "strategy": strategy_choice,
            "metrics": metrics
        }
else:
    st.info("Enter a ticker and strategy above, then click **Run Backtest** to begin.")