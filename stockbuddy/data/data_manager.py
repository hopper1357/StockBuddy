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

    def get_historical_data(self, ticker, period="1y"):
        """Fetches historical data for a single ticker."""
        stock = yf.Ticker(ticker)
        return stock.history(period=period)

    def get_annual_dividend(self, ticker):
        """
        Fetches the predicted annual dividend per share for a ticker.
        This method uses trailingAnnualDividendRate as a primary check for dividend payment.
        """
        stock_info = yf.Ticker(ticker).info

        # Use trailingAnnualDividendRate to check if the stock has a history of paying dividends.
        # This is more reliable than checking the dividends list, which can have incorrect future predictions.
        trailing_dividend_rate = stock_info.get('trailingAnnualDividendRate')
        if not trailing_dividend_rate or trailing_dividend_rate <= 0:
            return 0.0

        # If it's a dividend stock, prefer the forward-looking dividendRate for the prediction.
        dividend_rate = stock_info.get('dividendRate')
        if dividend_rate is not None and dividend_rate > 0:
            return dividend_rate

        # As a fallback, use the trailing rate if the forward rate is not available.
        return trailing_dividend_rate
