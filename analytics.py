"""
Analytics Module — computes equity curves and performance metrics.
"""

import numpy as np
from config import TRADING_DAYS_PER_YEAR

# Approximate annual risk-free rate (e.g., Indian government bond / FD yield).
# A real product might fetch this live; a fixed reasonable estimate is a legitimate starting point.
RISK_FREE_RATE_ANNUAL = 0.065  # ~6.5%, roughly in line with recent Indian G-Sec yields

# Assumed cost per trade as a fraction of trade value (brokerage + slippage combined estimate)
TRANSACTION_COST_PCT = 0.001  # 0.1% per trade, a common conservative retail estimate


def calculate_equity_curve(data, apply_transaction_costs=True):
    """Takes a dataframe with a 'Signal' column and computes daily strategy returns and cumulative equity.
    Signal is shifted forward by 1 day to avoid lookahead bias. Optionally deducts an
    estimated transaction cost every time a trade actually occurs (a Position change)."""
    df = data.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Signal"].shift(1) * df["Daily_Return"]

    if apply_transaction_costs:
        # A trade happens whenever Position is nonzero (a fresh buy or sell signal fired)
        trade_occurred = df["Position"].fillna(0) != 0
        df.loc[trade_occurred, "Strategy_Return"] -= TRANSACTION_COST_PCT

    df["Equity_Curve"] = (1 + df["Strategy_Return"]).cumprod()
    return df


def calculate_buy_and_hold_benchmark(data):
    """Computes a simple buy-and-hold equity curve for the same stock, as a benchmark
    to compare any strategy against."""
    df = data.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["Benchmark_Equity"] = (1 + df["Daily_Return"]).cumprod()
    return df[["Benchmark_Equity"]]


def calculate_metrics(equity_df):
    """Computes the five key performance metrics from an equity curve,
    using a non-zero risk-free rate in the Sharpe Ratio calculation."""
    returns = equity_df["Strategy_Return"].dropna()

    if len(returns) == 0 or returns.std() == 0:
        return {
            "Total Return (%)": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown (%)": 0.0,
            "Volatility (%)": 0.0,
            "Win Rate (%)": 0.0
        }

    total_return = equity_df["Equity_Curve"].iloc[-1] - 1

    daily_risk_free = RISK_FREE_RATE_ANNUAL / TRADING_DAYS_PER_YEAR
    excess_returns = returns - daily_risk_free
    sharpe_ratio = (excess_returns.mean() / returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)

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