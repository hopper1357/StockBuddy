import yfinance as yf

class DataManager:
    def get_stock_data(self, ticker):
        stock = yf.Ticker(ticker)
        return stock.history(period="1d")

    def get_index_data(self, tickers):
        data = yf.download(tickers, period="1d", auto_adjust=True)
        return data

    def get_watchlist_data(self, tickers):
        """Fetches the latest data for a list of tickers."""
        if not tickers:
            return None
        data = yf.download(tickers, period="1d", auto_adjust=True)
        return data
