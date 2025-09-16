import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="stockbuddy.db"):
        self.db_path = os.path.join(os.path.expanduser("~"), db_name)
        self._connect()
        self._create_tables()

    def __del__(self):
        self.close()

    def _connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                shares REAL NOT NULL,
                buy_price REAL NOT NULL
            )
        """)
        self.conn.commit()

    def get_watchlist(self):
        self.cursor.execute("SELECT ticker FROM watchlist ORDER BY ticker")
        return [row[0] for row in self.cursor.fetchall()]

    def add_stock_to_watchlist(self, ticker):
        try:
            self.cursor.execute("INSERT INTO watchlist (ticker) VALUES (?)", (ticker,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_stock_from_watchlist(self, ticker):
        self.cursor.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_portfolio(self):
        self.cursor.execute("SELECT ticker, shares, buy_price FROM portfolio ORDER BY ticker")
        return [{"ticker": row[0], "shares": row[1], "buy_price": row[2]} for row in self.cursor.fetchall()]

    def add_stock_to_portfolio(self, ticker, shares, buy_price):
        try:
            self.cursor.execute("INSERT INTO portfolio (ticker, shares, buy_price) VALUES (?, ?, ?)",
                                (ticker, shares, buy_price))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_stock_from_portfolio(self, ticker):
        self.cursor.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
