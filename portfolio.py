"""
Multi-Stock Portfolio Module — runs a strategy across multiple stocks and
compares an equally-weighted portfolio against the single best-performing stock.
"""

import pandas as pd
from config import DEFAULT_START_DATE, MAX_PORTFOLIO_STOCKS
from data_ingestion import fetch_stock_data
from analytics import calculate_equity_curve, calculate_metrics


def run_portfolio_backtest(tickers, strategy_func, start_date=DEFAULT_START_DATE):
    """Runs a given strategy on multiple tickers, returns a dict of equity results per stock."""
    tickers = tickers[:MAX_PORTFOLIO_STOCKS]  # enforce the 5-stock limit here, not just in the UI
    results = {}

    for ticker in tickers:
        data = fetch_stock_data(ticker, start_date)
        if data is None:
            print(f"Skipping {ticker} — no data")
            continue
        strategy_result = strategy_func(data)
        equity_df = calculate_equity_curve(strategy_result)
        results[ticker] = equity_df

    return results


def build_portfolio_returns(portfolio_results):
    """Combines individual stock returns into one equally-weighted portfolio return series."""
    if not portfolio_results:
        return None

    returns_df = pd.DataFrame()
    for ticker, df in portfolio_results.items():
        returns_df[ticker] = df["Strategy_Return"]

    returns_df["Portfolio_Return"] = returns_df.mean(axis=1)
    returns_df["Portfolio_Equity"] = (1 + returns_df["Portfolio_Return"]).cumprod()
    return returns_df


def compare_portfolio_vs_best_single(portfolio_results, portfolio_df):
    """Compares portfolio metrics against the single best-performing stock."""
    if not portfolio_results or portfolio_df is None:
        return None

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