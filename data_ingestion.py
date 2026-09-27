"""
Data Ingestion Module — fetches, cleans, and stores historical stock data.
"""

import yfinance as yf
from datetime import date
import sqlite3
import time
import streamlit as st
from config import DEFAULT_START_DATE


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(ticker, start_date=DEFAULT_START_DATE, max_retries=3):
    """Fetches historical adjusted price data for a given stock ticker.
    Cached for 1 hour so repeated backtests on the same ticker don't re-download.
    Retries on transient network failures before giving up.
    Returns None if the ticker is invalid or no data is found after retries."""

    for attempt in range(max_retries):
        try:
            data = yf.download(ticker, start=start_date, end=date.today(), auto_adjust=True, progress=False)

            if data.empty:
                # Empty result means invalid ticker, not a network issue — no point retrying
                print(f"No data found for ticker '{ticker}'. Check the symbol and try again.")
                return None

            data.columns = data.columns.get_level_values(0)
            return data

        except Exception as e:
            print(f"Attempt {attempt + 1} failed for '{ticker}': {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # brief pause before retrying, avoids hammering the API instantly
            else:
                print(f"All {max_retries} attempts failed for '{ticker}'.")
                return None


def save_to_database(data, table_name="stock_data", db_path="quanttrack.db"):
    """Saves a dataframe to the SQLite database."""
    conn = sqlite3.connect(db_path)
    data.to_sql(table_name, conn, if_exists="replace", index=True)
    conn.close()