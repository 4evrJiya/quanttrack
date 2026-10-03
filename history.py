"""
Backtest History Module — lets logged-in users save and view past backtest results.
"""

import sqlite3


def init_history_table(db_path="quanttrack.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS backtest_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            strategy TEXT NOT NULL,
            total_return REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            run_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_backtest(user_id, ticker, strategy, metrics, db_path="quanttrack.db"):
    init_history_table(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO backtest_history
           (user_id, ticker, strategy, total_return, sharpe_ratio, max_drawdown)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, ticker.upper(), strategy,
         metrics["Total Return (%)"], metrics["Sharpe Ratio"], metrics["Max Drawdown (%)"])
    )
    conn.commit()
    conn.close()


def get_history(user_id, db_path="quanttrack.db"):
    init_history_table(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """SELECT ticker, strategy, total_return, sharpe_ratio, max_drawdown, run_at
           FROM backtest_history WHERE user_id = ? ORDER BY run_at DESC LIMIT 20""",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows