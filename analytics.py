"""
Analytics Module — computes equity curves and performance metrics.
"""

import numpy as np
from config import TRADING_DAYS_PER_YEAR


def calculate_equity_curve(data):
    """Takes a dataframe with a 'Signal' column and computes daily strategy returns and cumulative equity.
    Signal is shifted forward by 1 day to avoid lookahead bias — you can only act on
    yesterday's signal, since today's closing price isn't known until the market shuts."""
    df = data.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Signal"].shift(1) * df["Daily_Return"]
    df["Equity_Curve"] = (1 + df["Strategy_Return"]).cumprod()
    return df


def calculate_metrics(equity_df):
    """Computes the five key performance metrics from an equity curve."""
    returns = equity_df["Strategy_Return"].dropna()

    if len(returns) == 0 or returns.std() == 0:
        # Guards against division-by-zero if a strategy never actually traded
        return {
            "Total Return (%)": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown (%)": 0.0,
            "Volatility (%)": 0.0,
            "Win Rate (%)": 0.0
        }

    total_return = equity_df["Equity_Curve"].iloc[-1] - 1
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)

    running_max = equity_df["Equity_Curve"].cummax()
    drawdown = (equity_df["Equity_Curve"] - running_max) / running_max
    max_drawdown = drawdown.min()

    volatility = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    active_returns = returns[returns != 0]
    win_rate = (active_returns > 0).sum() / len(active_returns) if len(active_returns) > 0 else 0.0

    return {
        "Total Return (%)": round(total_return * 100, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Max Drawdown (%)": round(max_drawdown * 100, 2),
        "Volatility (%)": round(volatility * 100, 2),
        "Win Rate (%)": round(win_rate * 100, 2)
    }