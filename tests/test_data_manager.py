from stockbuddy.data.data_manager import DataManager

def test_get_stock_data():
    dm = DataManager()
    data = dm.get_stock_data("AAPL")
    assert not data.empty

def test_get_index_data():
    dm = DataManager()
    tickers = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
    data = dm.get_index_data(tickers)
    assert not data.empty
