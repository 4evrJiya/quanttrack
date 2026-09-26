import streamlit as st
import yfinance as yf
from datetime import date
import pandas as pd
import numpy as np
from ta.trend import ADXIndicator
from prophet import Prophet

st.title("QuantTrack — Trading Strategy Backtester")

ticker = st.text_input("Enter stock ticker (e.g. RELIANCE.NS)", "RELIANCE.NS")
strategy_choice = st.selectbox("Choose a strategy", ["Moving Average Crossover", "Momentum", "Mean Reversion"])
run_button = st.button("Run Backtest")

def fetch_stock_data(ticker, start_date="2015-01-01"):
    data = yf.download(ticker, start=start_date, end=date.today(), auto_adjust=True)
    if data.empty:
        return None
    data.columns = data.columns.get_level_values(0)
    return data

def moving_average_crossover(data, short_window=20, long_window=50):
    df = data.copy()
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
    df["Signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df

def momentum_strategy(data, lookback=20, threshold=0.05):
    df = data.copy()
    df["Momentum"] = df["Close"].pct_change(periods=lookback)
    df["Signal"] = 0
    df.loc[df["Momentum"] > threshold, "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df

def mean_reversion_strategy(data, window=20, std_multiplier=1):
    df = data.copy()
    df["Rolling_Mean"] = df["Close"].rolling(window=window).mean()
    df["Rolling_Std"] = df["Close"].rolling(window=window).std()
    df["Lower_Band"] = df["Rolling_Mean"] - (std_multiplier * df["Rolling_Std"])
    df["Signal"] = 0
    df.loc[df["Close"] < df["Lower_Band"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df

def add_adx(data, period=14):
    df = data.copy()
    adx_indicator = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=period)
    df["ADX"] = adx_indicator.adx()
    return df

def classify_regime(adx_value, threshold=25):
    return "Trending" if adx_value >= threshold else "Sideways"

def recommend_strategy(regime):
    if regime == "Trending":
        return "Moving Average Crossover or Momentum (trend-following suits trending markets)"
    else:
        return "Mean Reversion (suits sideways/ranging markets)"

def calculate_equity_curve(data):
    df = data.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Signal"].shift(1) * df["Daily_Return"]
    df["Equity_Curve"] = (1 + df["Strategy_Return"]).cumprod()
    return df

def calculate_metrics(equity_df):
    returns = equity_df["Strategy_Return"].dropna()
    total_return = equity_df["Equity_Curve"].iloc[-1] - 1
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
    running_max = equity_df["Equity_Curve"].cummax()
    drawdown = (equity_df["Equity_Curve"] - running_max) / running_max
    max_drawdown = drawdown.min()
    volatility = returns.std() * np.sqrt(252)
    active_returns = returns[returns != 0]
    win_rate = (active_returns > 0).sum() / len(active_returns)
    return {
        "Total Return (%)": round(total_return * 100, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Max Drawdown (%)": round(max_drawdown * 100, 2),
        "Volatility (%)": round(volatility * 100, 2),
        "Win Rate (%)": round(win_rate * 100, 2)
    }

def run_portfolio_backtest(tickers, strategy_func, start_date="2015-01-01"):
    results = {}
    for t in tickers:
        d = fetch_stock_data(t, start_date)
        if d is None:
            continue
        strategy_result = strategy_func(d)
        equity_df = calculate_equity_curve(strategy_result)
        results[t] = equity_df
    return results

def build_portfolio_returns(portfolio_results):
    returns_df = pd.DataFrame()
    for t, d in portfolio_results.items():
        returns_df[t] = d["Strategy_Return"]
    returns_df["Portfolio_Return"] = returns_df.mean(axis=1)
    returns_df["Portfolio_Equity"] = (1 + returns_df["Portfolio_Return"]).cumprod()
    return returns_df

def compare_portfolio_vs_best_single(portfolio_results, portfolio_df):
    best_ticker = max(portfolio_results, key=lambda t: portfolio_results[t]["Equity_Curve"].iloc[-1])
    best_stock_df = portfolio_results[best_ticker]
    portfolio_metrics = calculate_metrics(portfolio_df.rename(columns={
        "Portfolio_Return": "Strategy_Return", "Portfolio_Equity": "Equity_Curve"
    }))
    best_stock_metrics = calculate_metrics(best_stock_df)
    comparison = pd.DataFrame({
        "Portfolio (5 stocks)": portfolio_metrics,
        f"Best Single Stock ({best_ticker})": best_stock_metrics
    })
    return comparison

def generate_forecast(data, forecast_days=30):
    df = data.reset_index()[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
    model = Prophet(daily_seasonality=False)
    model.fit(df)
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)
    return forecast

if run_button:
    data = fetch_stock_data(ticker)

    if data is None:
        st.error(f"No data found for ticker '{ticker}'. Check the symbol.")
    else:
        if strategy_choice == "Moving Average Crossover":
            result = moving_average_crossover(data)
        elif strategy_choice == "Momentum":
            result = momentum_strategy(data)
        else:
            result = mean_reversion_strategy(data)

        equity_result = calculate_equity_curve(result)
        metrics = calculate_metrics(equity_result)

        adx_data = add_adx(data)
        latest_adx = adx_data["ADX"].iloc[-1]
        current_regime = classify_regime(latest_adx)
        recommendation = recommend_strategy(current_regime)

        st.subheader("Market Regime Detection")
        st.write(f"**Latest ADX:** {latest_adx:.2f}")
        st.write(f"**Market Regime:** {current_regime}")
        st.write(f"**Recommended Approach:** {recommendation}")

        st.subheader("Price Chart")
        st.line_chart(data["Close"])

        st.subheader("Equity Curve")
        st.line_chart(equity_result["Equity_Curve"])

        st.subheader("Performance Metrics")
        st.table(pd.DataFrame(metrics, index=["Value"]).T)

st.divider()
st.header("Multi-Stock Portfolio Comparison")

tickers_input = st.text_input("Enter up to 5 tickers, comma-separated", "RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ITC.NS")
portfolio_strategy = st.selectbox("Choose strategy for portfolio", ["Moving Average Crossover", "Momentum", "Mean Reversion"], key="portfolio_strategy")
portfolio_button = st.button("Run Portfolio Backtest")

if portfolio_button:
    tickers = [t.strip() for t in tickers_input.split(",")][:5]

    if portfolio_strategy == "Moving Average Crossover":
        strat_func = moving_average_crossover
    elif portfolio_strategy == "Momentum":
        strat_func = momentum_strategy
    else:
        strat_func = mean_reversion_strategy

    portfolio_results = run_portfolio_backtest(tickers, strat_func)
    portfolio_df = build_portfolio_returns(portfolio_results)
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

        st.subheader("Forecasted Price (next 30 days)")
        forecast_chart_data = forecast_result[["ds", "yhat", "yhat_lower", "yhat_upper"]].set_index("ds").tail(30)
        st.line_chart(forecast_chart_data)

        st.subheader("Forecast Table")
        st.dataframe(forecast_chart_data.tail(10))