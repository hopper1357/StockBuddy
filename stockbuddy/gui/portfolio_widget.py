from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
                             QFormLayout)
from PyQt5.QtCore import QTimer
from stockbuddy.data.data_manager import DataManager
from stockbuddy.data.database_manager import DatabaseManager

class PortfolioWidget(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.data_manager = DataManager()
        self.portfolio = self.db_manager.get_portfolio()

        layout = QVBoxLayout(self)

        # --- Input Form ---
        form_layout = QFormLayout()
        self.ticker_input = QLineEdit()
        self.shares_input = QLineEdit()
        self.buy_price_input = QLineEdit()
        self.add_button = QPushButton("Add to Portfolio")

        form_layout.addRow("Ticker:", self.ticker_input)
        form_layout.addRow("Shares:", self.shares_input)
        form_layout.addRow("Buy Price:", self.buy_price_input)
        form_layout.addRow(self.add_button)
        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.remove_button = QPushButton("Remove Selected")
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)


        # --- Portfolio Table ---
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(7)
        self.portfolio_table.setHorizontalHeaderLabels([
            "Symbol", "Shares", "Buy Price", "Current Price", "Cost Basis", "Current Value", "Gain/Loss"
        ])
        self.portfolio_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.portfolio_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.portfolio_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.portfolio_table.setSortingEnabled(True)

        layout.addWidget(self.portfolio_table)

        # --- Refresh Message ---
        self.refresh_label = QLabel("Updating...")
        self.refresh_label.setStyleSheet("font-style: italic; color: grey;")
        layout.addWidget(self.refresh_label)

        self.setLayout(layout)

        # --- Connect Signals ---
        self.add_button.clicked.connect(self.add_stock)
        self.remove_button.clicked.connect(self.remove_stock)

        # --- Timer for Updates ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_portfolio)
        self.timer.start(60000)  # Update every 60 seconds

        # Initial load
        self.update_portfolio()

    def add_stock(self):
        ticker = self.ticker_input.text().strip().upper()
        shares_str = self.shares_input.text().strip()
        buy_price_str = self.buy_price_input.text().strip()

        if not all([ticker, shares_str, buy_price_str]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            shares = float(shares_str)
            buy_price = float(buy_price_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Shares and Buy Price must be numbers.")
            return

        self.db_manager.add_stock_to_portfolio(ticker, shares, buy_price)
        self.portfolio = self.db_manager.get_portfolio()
        self.ticker_input.clear()
        self.shares_input.clear()
        self.buy_price_input.clear()
        self.update_portfolio()

    def remove_stock(self):
        selected_rows = self.portfolio_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row_index = selected_rows[0].row()
        ticker_item = self.portfolio_table.item(row_index, 0)
        if ticker_item:
            ticker = ticker_item.text()
            if self.db_manager.remove_stock_from_portfolio(ticker):
                self.portfolio = self.db_manager.get_portfolio()
                self.update_portfolio()

    def update_portfolio(self):
        if not self.portfolio:
            self.portfolio_table.setRowCount(0)
            return

        self.portfolio_table.setRowCount(len(self.portfolio))

        for i, stock in enumerate(self.portfolio):
            ticker = stock["ticker"]
            shares = stock["shares"]
            buy_price = stock["buy_price"]

            self.portfolio_table.setItem(i, 0, QTableWidgetItem(ticker))
            self.portfolio_table.setItem(i, 1, QTableWidgetItem(f"{shares}"))
            self.portfolio_table.setItem(i, 2, QTableWidgetItem(f"{buy_price:.2f}"))

            try:
                historical_data = self.data_manager.get_historical_data(ticker)
                if historical_data.empty:
                    raise ValueError("No data returned")

                current_price = historical_data.iloc[-1]['Close']
                cost_basis = shares * buy_price
                current_value = shares * current_price
                gain_loss = current_value - cost_basis

                self.portfolio_table.setItem(i, 3, QTableWidgetItem(f"{current_price:.2f}"))
                self.portfolio_table.setItem(i, 4, QTableWidgetItem(f"{cost_basis:.2f}"))
                self.portfolio_table.setItem(i, 5, QTableWidgetItem(f"{current_value:.2f}"))
                self.portfolio_table.setItem(i, 6, QTableWidgetItem(f"{gain_loss:+.2f}"))

            except Exception as e:
                for j in range(3, 7):
                    self.portfolio_table.setItem(i, j, QTableWidgetItem("N/A"))

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.refresh_label.setText(f"Last updated at: {timestamp}. Auto-refreshes every 60 seconds.")
