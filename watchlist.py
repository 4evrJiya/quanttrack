"""
Watchlist Module — lets logged-in users save and manage favorite tickers.
"""

import sqlite3


def init_watchlist_table(db_path="quanttrack.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, ticker)
        )
    """)
    conn.commit()
    conn.close()


def add_to_watchlist(user_id, ticker, db_path="quanttrack.db"):
    init_watchlist_table(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)", (user_id, ticker.upper()))
        conn.commit()
        return True, f"{ticker.upper()} added to watchlist."
    except sqlite3.IntegrityError:
        return False, f"{ticker.upper()} is already in your watchlist."
    finally:
        conn.close()


def remove_from_watchlist(user_id, ticker, db_path="quanttrack.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker.upper()))
    conn.commit()
    conn.close()


def get_watchlist(user_id, db_path="quanttrack.db"):
    init_watchlist_table(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT ticker FROM watchlist WHERE user_id = ? ORDER BY added_at DESC", (user_id,)).fetchall()
    conn.close()
    return [row[0] for row in rows]