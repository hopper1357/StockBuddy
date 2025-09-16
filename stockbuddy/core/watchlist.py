class Watchlist:
    def __init__(self):
        self._tickers = []

    def add_ticker(self, ticker):
        """Adds a ticker to the watchlist if it's not already there."""
        ticker = ticker.upper()
        if ticker not in self._tickers:
            self._tickers.append(ticker)
            return True
        return False

    def remove_ticker(self, ticker):
        """Removes a ticker from the watchlist."""
        ticker = ticker.upper()
        if ticker in self._tickers:
            self._tickers.remove(ticker)
            return True
        return False

    def get_tickers(self):
        """Returns the list of tickers in the watchlist."""
        return self._tickers
