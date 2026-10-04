import sqlite3

conn = sqlite3.connect('quanttrack.db')
conn.execute('DROP TABLE IF EXISTS backtest_history')
conn.commit()
conn.close()

print("Done — old backtest_history table removed.")