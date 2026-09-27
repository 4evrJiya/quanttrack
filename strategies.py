"""
Strategy Engine — implements all trading strategies.
Each strategy returns a dataframe with a 'Signal' and 'Position' column.
"""

from config import (
    MA_SHORT_WINDOW, MA_LONG_WINDOW,
    MOMENTUM_LOOKBACK, MOMENTUM_THRESHOLD,
    MEANREV_WINDOW, MEANREV_STD_MULTIPLIER
)


def moving_average_crossover(data, short_window=MA_SHORT_WINDOW, long_window=MA_LONG_WINDOW):
    """Calculates short and long moving averages and generates buy/sell signals."""
    df = data.copy()
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
    df["Signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df


def momentum_strategy(data, lookback=MOMENTUM_LOOKBACK, threshold=MOMENTUM_THRESHOLD):
    """Generates buy signals when price has risen more than threshold% over the lookback period."""
    df = data.copy()
    df["Momentum"] = df["Close"].pct_change(periods=lookback)
    df["Signal"] = 0
    df.loc[df["Momentum"] > threshold, "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df


def mean_reversion_strategy(data, window=MEANREV_WINDOW, std_multiplier=MEANREV_STD_MULTIPLIER):
    """Generates buy signals when price drops more than std_multiplier standard deviations below the rolling mean."""
    df = data.copy()
    df["Rolling_Mean"] = df["Close"].rolling(window=window).mean()
    df["Rolling_Std"] = df["Close"].rolling(window=window).std()
    df["Lower_Band"] = df["Rolling_Mean"] - (std_multiplier * df["Rolling_Std"])
    df["Signal"] = 0
    df.loc[df["Close"] < df["Lower_Band"], "Signal"] = 1
    df["Position"] = df["Signal"].diff()
    return df


# Lets other modules loop through all strategies generically (used later in portfolio/UI)
STRATEGY_REGISTRY = {
    "Moving Average Crossover": moving_average_crossover,
    "Momentum": momentum_strategy,
    "Mean Reversion": mean_reversion_strategy,
}