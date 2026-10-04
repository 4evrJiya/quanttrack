"""
Backtest History Module — lets logged-in users save and view past results
across single-stock backtests, portfolio runs, and forecasts.
"""

import sqlite3


def init_history_table(db_path="quanttrack.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS backtest_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            result_type TEXT NOT NULL,
            ticker TEXT NOT NULL,
            strategy TEXT,
            total_return REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            notes TEXT,
            run_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_backtest(user_id, ticker, strategy, metrics, db_path="quanttrack.db"):
    """Saves a single-stock backtest result."""
    init_history_table(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO backtest_history
           (user_id, result_type, ticker, strategy, total_return, sharpe_ratio, max_drawdown)
           VALUES (?, 'Backtest', ?, ?, ?, ?, ?)""",
        (user_id, ticker.upper(), strategy,
         metrics["Total Return (%)"], metrics["Sharpe Ratio"], metrics["Max Drawdown (%)"])
    )
    conn.commit()
    conn.close()


def save_portfolio_result(user_id, tickers, strategy, portfolio_metrics, db_path="quanttrack.db"):
    """Saves a portfolio backtest result. tickers is a list; stored as a comma-separated string."""
    init_history_table(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO backtest_history
           (user_id, result_type, ticker, strategy, total_return, sharpe_ratio, max_drawdown)
           VALUES (?, 'Portfolio', ?, ?, ?, ?, ?)""",
        (user_id, ", ".join(tickers), strategy,
         portfolio_metrics["Total Return (%)"], portfolio_metrics["Sharpe Ratio"], portfolio_metrics["Max Drawdown (%)"])
    )
    conn.commit()
    conn.close()


def save_forecast_result(user_id, ticker, final_predicted_price, db_path="quanttrack.db"):
    """Saves a forecast result. Reuses total_return column to store the predicted price for simplicity."""
    init_history_table(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO backtest_history
           (user_id, result_type, ticker, notes)
           VALUES (?, 'Forecast', ?, ?)""",
        (user_id, ticker.upper(), f"30-day predicted price: {final_predicted_price:.2f}")
    )
    conn.commit()
    conn.close()


def get_history(user_id, db_path="quanttrack.db"):
    init_history_table(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """SELECT result_type, ticker, strategy, total_return, sharpe_ratio, max_drawdown, notes, run_at
           FROM backtest_history WHERE user_id = ? ORDER BY run_at DESC LIMIT 20""",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows