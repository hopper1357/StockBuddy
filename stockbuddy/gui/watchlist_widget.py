from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import QTimer
from stockbuddy.core.preset_manager import PresetManager
from stockbuddy.core.settings_manager import SettingsManager
from stockbuddy.data.data_manager import DataManager
from stockbuddy.core.recommendation_engine import RecommendationEngine

class WatchlistWidget(QWidget):
    def __init__(self, settings_manager: SettingsManager, preset_manager: PresetManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.preset_manager = preset_manager
        self.tickers = [] # Manage tickers directly in the widget
        self.data_manager = DataManager()
        self.recommendation_engine = RecommendationEngine()

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
        self.watchlist_table.setColumnCount(6)
        self.watchlist_table.setHorizontalHeaderLabels([
            "Symbol", "Price", "Change", "% Change", "Volume", "Signal"
        ])
        self.watchlist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.watchlist_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.watchlist_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.watchlist_table.setSortingEnabled(True)

        layout.addWidget(self.watchlist_table)

        # --- Refresh Message ---
        self.refresh_label = QLabel("Updating...")
        self.refresh_label.setStyleSheet("font-style: italic; color: grey;")
        layout.addWidget(self.refresh_label)

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
        ticker = self.ticker_input.text().strip().upper()
        if not ticker:
            return

        if ticker not in self.tickers:
            self.tickers.append(ticker)
            self.ticker_input.clear()
            self.update_watchlist()  # Refresh immediately
        else:
            QMessageBox.information(self, "Stock Exists", f"'{ticker}' is already in the watchlist.")

    def remove_stock(self):
        selected_rows = self.watchlist_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row_index = selected_rows[0].row()
        ticker_item = self.watchlist_table.item(row_index, 0)
        if ticker_item:
            ticker = ticker_item.text()
            if ticker in self.tickers:
                self.tickers.remove(ticker)
                self.update_watchlist()

    def update_watchlist(self):
        if not self.tickers:
            self.watchlist_table.setRowCount(0)
            return

        self.watchlist_table.setRowCount(len(self.tickers))

        # Get the active preset rules
        active_preset_name = self.settings_manager.get_active_preset()
        active_preset = self.preset_manager.get_preset(active_preset_name)
        rules = active_preset.get("rules", []) if active_preset else []


        for i, ticker in enumerate(self.tickers):
            try:
                historical_data = self.data_manager.get_historical_data(ticker)
                if historical_data.empty:
                    raise ValueError("No data returned")

                latest_row = historical_data.iloc[-1]
                price = latest_row['Close']
                volume = latest_row['Volume']
                open_price = historical_data.iloc[-2]['Close'] if len(historical_data) > 1 else price

                change = price - open_price
                percent_change = (change / open_price) * 100 if open_price != 0 else 0

                self.watchlist_table.setItem(i, 0, QTableWidgetItem(ticker))
                self.watchlist_table.setItem(i, 1, QTableWidgetItem(f"{price:.2f}"))
                self.watchlist_table.setItem(i, 2, QTableWidgetItem(f"{change:+.2f}"))
                self.watchlist_table.setItem(i, 3, QTableWidgetItem(f"{percent_change:+.2f}%"))
                self.watchlist_table.setItem(i, 4, QTableWidgetItem(f"{volume:,}"))

                # Generate signal using the active preset's rules
                signal = self.recommendation_engine.generate_signals(historical_data, rules)
                self.watchlist_table.setItem(i, 5, QTableWidgetItem(signal))

            except Exception as e:
                self.watchlist_table.setItem(i, 0, QTableWidgetItem(ticker))
                for j in range(1, 6):
                    self.watchlist_table.setItem(i, j, QTableWidgetItem("N/A"))

        # Update the timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.refresh_label.setText(f"Last updated at: {timestamp}. Auto-refreshes every 60 seconds.")
