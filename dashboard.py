"""
QuantTrack Dashboard — Streamlit UI layer.
All actual logic lives in the imported modules; this file only handles
user input, calling the right functions, and displaying results.
"""

import streamlit as st
import pandas as pd

from config import MAX_PORTFOLIO_STOCKS
from data_ingestion import fetch_stock_data
from strategies import STRATEGY_REGISTRY
from regime_detector import get_regime_summary
from analytics import calculate_equity_curve, calculate_metrics, calculate_buy_and_hold_benchmark
from portfolio import run_portfolio_backtest, build_portfolio_returns, compare_portfolio_vs_best_single
from forecasting import generate_forecast

st.title("QuantTrack — Trading Strategy Backtester")

ticker = st.text_input("Enter stock ticker (e.g. RELIANCE.NS)", "RELIANCE.NS")
strategy_choice = st.selectbox("Choose a strategy", list(STRATEGY_REGISTRY.keys()))
run_button = st.button("Run Backtest")

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

        st.subheader("Market Regime Detection")
        st.write(f"**Latest ADX:** {regime_info['adx']:.2f}")
        st.write(f"**Market Regime:** {regime_info['regime']}")
        st.write(f"**Recommended Approach:** {regime_info['recommendation']}")

        st.subheader("Price Chart")
        st.line_chart(data["Close"])

        benchmark = calculate_buy_and_hold_benchmark(data)
        comparison_chart = equity_result[["Equity_Curve"]].join(benchmark)
        comparison_chart.columns = ["Strategy", "Buy & Hold Benchmark"]

        st.subheader("Strategy vs. Buy & Hold Benchmark")
        st.line_chart(comparison_chart)

        benchmark_return = round((benchmark["Benchmark_Equity"].iloc[-1] - 1) * 100, 2)
        strategy_return = metrics["Total Return (%)"]

        if strategy_return > benchmark_return:
            st.success(f"Strategy outperformed Buy & Hold by {round(strategy_return - benchmark_return, 2)} percentage points")
        else:
            st.warning(f"Strategy underperformed Buy & Hold by {round(benchmark_return - strategy_return, 2)} percentage points")

        st.subheader("Performance Metrics")
        st.table(pd.DataFrame(metrics, index=["Value"]).T)
        st.caption(f"Buy & Hold Benchmark Total Return: {benchmark_return}% | Transaction costs of 0.1% per trade applied to strategy returns")

st.divider()
st.header("Multi-Stock Portfolio Comparison")

tickers_input = st.text_input(
    f"Enter up to {MAX_PORTFOLIO_STOCKS} tickers, comma-separated",
    "RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ITC.NS"
)
portfolio_strategy_choice = st.selectbox("Choose strategy for portfolio", list(STRATEGY_REGISTRY.keys()), key="portfolio_strategy")
portfolio_button = st.button("Run Portfolio Backtest")

if portfolio_button:
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    strat_func = STRATEGY_REGISTRY[portfolio_strategy_choice]

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

st.divider()
st.header("30-Day Price Forecast")

forecast_ticker = st.text_input("Enter ticker for forecast", "RELIANCE.NS", key="forecast_ticker")
forecast_button = st.button("Generate Forecast")

if forecast_button:
    forecast_data = fetch_stock_data(forecast_ticker)

    if forecast_data is None:
        st.error(f"No data found for ticker '{forecast_ticker}'. Check the symbol.")
    else:
        with st.spinner("Generating forecast..."):
            forecast_result = generate_forecast(forecast_data)

        if forecast_result is None:
            st.warning("Not enough historical data to generate a reliable forecast for this stock.")
        else:
            st.subheader("Forecasted Price (next 30 days)")
            forecast_chart_data = forecast_result[["ds", "yhat", "yhat_lower", "yhat_upper"]].set_index("ds").tail(30)
            st.line_chart(forecast_chart_data)

            st.subheader("Forecast Table")
            st.dataframe(forecast_chart_data.tail(10))