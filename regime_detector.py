"""
Market Regime Detection Module — classifies market condition using ADX
and recommends a suitable strategy type.
"""

from ta.trend import ADXIndicator
from config import ADX_PERIOD, ADX_TREND_THRESHOLD


def add_adx(data, period=ADX_PERIOD):
    """Adds ADX (trend strength) to the dataframe."""
    df = data.copy()
    adx_indicator = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=period)
    df["ADX"] = adx_indicator.adx()
    return df


def classify_regime(adx_value, threshold=ADX_TREND_THRESHOLD):
    """Classifies market regime based on ADX value."""
    return "Trending" if adx_value >= threshold else "Sideways"


def recommend_strategy(regime):
    """Recommends a strategy type based on market regime."""
    if regime == "Trending":
        return "Moving Average Crossover or Momentum (trend-following strategies suit trending markets)"
    else:
        return "Mean Reversion (suits sideways/ranging markets)"


def get_regime_summary(data):
    """Convenience function: runs the full regime detection pipeline on price data
    and returns the latest ADX, regime classification, and recommendation together."""
    adx_data = add_adx(data)
    latest_adx = adx_data["ADX"].iloc[-1]
    regime = classify_regime(latest_adx)
    recommendation = recommend_strategy(regime)
    return {
        "adx": latest_adx,
        "regime": regime,
        "recommendation": recommendation
    }