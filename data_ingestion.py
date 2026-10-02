"""
Data Ingestion Module — fetches, cleans, and stores historical stock data.
"""

import yfinance as yf
from datetime import date
import sqlite3
import time
import re
import streamlit as st
from config import DEFAULT_START_DATE


def validate_ticker(ticker):
    """Checks that a ticker string is reasonably well-formed before even attempting a fetch.
    Returns (is_valid, cleaned_ticker_or_error_message)."""
    if not ticker or not ticker.strip():
        return False, "Ticker cannot be empty."

    ticker = ticker.strip().upper()

    if not re.match(r'^[A-Z0-9.\-]+$', ticker):
        return False, f"'{ticker}' contains invalid characters. Use only letters, numbers, dots, and hyphens."

    if len(ticker) > 20:
        return False, f"'{ticker}' is too long to be a valid ticker symbol."

    return True, ticker


def _fetch_stock_data_uncached(ticker, start_date, max_retries):
    """The actual fetch logic, never cached directly — only successful results get cached,
    by the public fetch_stock_data() wrapper below."""
    is_valid, result = validate_ticker(ticker)
    if not is_valid:
        print(f"Validation failed: {result}")
        return None
    ticker = result

    for attempt in range(max_retries):
        try:
            data = yf.download(ticker, start=start_date, end=date.today(), auto_adjust=True, progress=False)

            if data.empty:
                print(f"No data found for ticker '{ticker}'. Check the symbol and try again.")
                return None

            data.columns = data.columns.get_level_values(0)
            return data

        except Exception as e:
            print(f"Attempt {attempt + 1} failed for '{ticker}': {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"All {max_retries} attempts failed for '{ticker}'.")
                return None


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_fetch(ticker, start_date, max_retries):
    """Only this layer is cached, and only ever called when we already know we want to cache it."""
    return _fetch_stock_data_uncached(ticker, start_date, max_retries)


def fetch_stock_data(ticker, start_date=DEFAULT_START_DATE, max_retries=3):
    """Public entry point. Tries the cache first; if the cached result is None
    (a past failure), it retries fresh instead of trusting a stale failure."""
    result = _cached_fetch(ticker, start_date, max_retries)

    if result is None:
        # Clear this specific bad cache entry and try once more, fresh
        _cached_fetch.clear()
        result = _fetch_stock_data_uncached(ticker, start_date, max_retries)

    return result


def save_to_database(data, table_name="stock_data", db_path="quanttrack.db"):
    """Saves a dataframe to the SQLite database."""
    conn = sqlite3.connect(db_path)
    data.to_sql(table_name, conn, if_exists="replace", index=True)
    conn.close()