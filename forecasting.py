"""
Forecasting Module — generates short-term price predictions using Prophet.
"""

from prophet import Prophet
from config import FORECAST_DAYS


def generate_forecast(data, forecast_days=FORECAST_DAYS):
    """Generates a price forecast using Prophet for the given number of future days.
    Returns None if there isn't enough historical data for Prophet to fit a model."""

    if data is None or len(data) < 30:
        # Prophet needs a reasonable amount of history to produce a meaningful fit
        return None

    df = data.reset_index()[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})

    try:
        model = Prophet(daily_seasonality=False)
        model.fit(df)
        future = model.make_future_dataframe(periods=forecast_days)
        forecast = model.predict(future)
        return forecast
    except Exception as e:
        print(f"Forecasting failed: {e}")
        return None