"""
Data Ingestion Module — fetches, cleans, and stores historical stock data.
"""

import yfinance as yf
from datetime import date
import sqlite3
from config import DEFAULT_START_DATE


def fetch_stock_data(ticker, start_date=DEFAULT_START_DATE):
    """Fetches historical adjusted price data for a given stock ticker.
    Returns None if the ticker is invalid or no data is found."""
    data = yf.download(ticker, start=start_date, end=date.today(), auto_adjust=True)

    if data.empty:
        print(f"No data found for ticker '{ticker}'. Check the symbol and try again.")
        return None

    data.columns = data.columns.get_level_values(0)
    return data


def save_to_database(data, table_name="stock_data", db_path="quanttrack.db"):
    """Saves a dataframe to the SQLite database."""
    conn = sqlite3.connect(db_path)
    data.to_sql(table_name, conn, if_exists="replace", index=True)
    conn.close()