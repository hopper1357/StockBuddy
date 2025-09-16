from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import QTimer
from stockbuddy.core.watchlist import Watchlist
from stockbuddy.data.data_manager import DataManager

class WatchlistWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.watchlist = Watchlist()
        self.data_manager = DataManager()

        layout = QVBoxLayout(self)

        # --- Input and Buttons ---
        input_layout = QHBoxLayout()
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Enter Ticker Symbol (e.g., AAPL)")
        self.add_button = QPushButton("Add Stock")
        self.remove_button = QPushButton("Remove Selected")

        input_layout.addWidget(self.ticker_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)
        layout.addLayout(input_layout)

        # --- Watchlist Table ---
        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(5)
        self.watchlist_table.setHorizontalHeaderLabels([
            "Symbol", "Price", "Change", "% Change", "Volume"
        ])
        self.watchlist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.watchlist_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.watchlist_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.watchlist_table.setSortingEnabled(True)

        layout.addWidget(self.watchlist_table)
        self.setLayout(layout)

        # --- Connect Signals ---
        self.add_button.clicked.connect(self.add_stock)
        self.remove_button.clicked.connect(self.remove_stock)
        self.ticker_input.returnPressed.connect(self.add_stock)

        # --- Timer for Updates ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_watchlist)
        self.timer.start(60000)  # Update every 60 seconds

        # Initial load
        self.update_watchlist()

    def add_stock(self):
        ticker = self.ticker_input.text().strip()
        if not ticker:
            return

        if self.watchlist.add_ticker(ticker):
            self.ticker_input.clear()
            self.update_watchlist()  # Refresh immediately
        else:
            QMessageBox.information(self, "Stock Exists", f"'{ticker.upper()}' is already in the watchlist.")

    def remove_stock(self):
        selected_rows = self.watchlist_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row_index = selected_rows[0].row()
        ticker_item = self.watchlist_table.item(row_index, 0)
        if ticker_item:
            ticker = ticker_item.text()
            if self.watchlist.remove_ticker(ticker):
                self.update_watchlist()

    def update_watchlist(self):
        tickers = self.watchlist.get_tickers()
        if not tickers:
            self.watchlist_table.setRowCount(0) # Clear table
            return

        data = self.data_manager.get_watchlist_data(tickers)
        if data is None or data.empty:
            return # No data to display

        self.watchlist_table.setRowCount(len(tickers))

        # yfinance returns a multi-index header when fetching multiple tickers
        # We need to access the correct columns
        price_data = data['Close']
        volume_data = data['Volume']
        open_data = data['Open']

        for i, ticker in enumerate(tickers):
            if ticker in price_data and ticker in volume_data and ticker in open_data:
                price = price_data[ticker].iloc[-1]
                volume = volume_data[ticker].iloc[-1]
                open_price = open_data[ticker].iloc[-1]
                change = price - open_price
                percent_change = (change / open_price) * 100 if open_price != 0 else 0

                self.watchlist_table.setItem(i, 0, QTableWidgetItem(ticker))
                self.watchlist_table.setItem(i, 1, QTableWidgetItem(f"{price:.2f}"))
                self.watchlist_table.setItem(i, 2, QTableWidgetItem(f"{change:+.2f}"))
                self.watchlist_table.setItem(i, 3, QTableWidgetItem(f"{percent_change:+.2f}%"))
                self.watchlist_table.setItem(i, 4, QTableWidgetItem(f"{volume:,}"))
            else:
                # Handle cases where data for a specific ticker might fail
                self.watchlist_table.setItem(i, 0, QTableWidgetItem(ticker))
                self.watchlist_table.setItem(i, 1, QTableWidgetItem("N/A"))
                self.watchlist_table.setItem(i, 2, QTableWidgetItem("N/A"))
                self.watchlist_table.setItem(i, 3, QTableWidgetItem("N/A"))
                self.watchlist_table.setItem(i, 4, QTableWidgetItem("N/A"))
