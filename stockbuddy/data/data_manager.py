import yfinance as yf

class DataManager:
    def get_stock_data(self, ticker):
        stock = yf.Ticker(ticker)
        return stock.history(period="1d")

    def get_index_data(self, tickers):
        data = yf.download(tickers, period="1d")
        return data
