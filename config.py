"""
Central configuration for QuantTrack.
Change any default parameter here — nowhere else.
"""

# Data settings
DEFAULT_START_DATE = "2015-01-01"

# Moving Average Crossover
MA_SHORT_WINDOW = 20
MA_LONG_WINDOW = 50

# Momentum
MOMENTUM_LOOKBACK = 20
MOMENTUM_THRESHOLD = 0.05

# Mean Reversion
MEANREV_WINDOW = 20
MEANREV_STD_MULTIPLIER = 1

# Market Regime Detection
ADX_PERIOD = 14
ADX_TREND_THRESHOLD = 25

# Analytics
TRADING_DAYS_PER_YEAR = 252

# Portfolio
MAX_PORTFOLIO_STOCKS = 5

# Forecasting
FORECAST_DAYS = 30