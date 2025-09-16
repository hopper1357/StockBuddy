from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView)
from PyQt5.QtCore import QTimer
from stockbuddy.data.data_manager import DataManager
from stockbuddy.data.database_manager import DatabaseManager

class DashboardWidget(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.data_manager = DataManager()

        layout = QVBoxLayout(self)

        # --- Portfolio Summary ---
        self.total_value_label = QLabel("Total Portfolio Value: N/A")
        self.total_value_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.total_gain_loss_label = QLabel("Total Gain/Loss: N/A")
        self.total_gain_loss_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.total_value_label)
        layout.addWidget(self.total_gain_loss_label)

        # --- Holdings Table ---
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(4)
        self.holdings_table.setHorizontalHeaderLabels(["Symbol", "Shares", "Current Value", "Gain/Loss"])
        self.holdings_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.holdings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.holdings_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.holdings_table)

        # --- Refresh Message ---
        self.refresh_label = QLabel("Updating...")
        self.refresh_label.setStyleSheet("font-style: italic; color: grey;")
        layout.addWidget(self.refresh_label)

        self.setLayout(layout)

        # --- Timer for Updates ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(60000)  # Update every 60 seconds

        # Initial load
        self.update_dashboard()

    def update_dashboard(self):
        portfolio = self.db_manager.get_portfolio()
        if not portfolio:
            self.holdings_table.setRowCount(0)
            self.total_value_label.setText("Total Portfolio Value: $0.00")
            self.total_gain_loss_label.setText("Total Gain/Loss: $0.00")
            return

        self.holdings_table.setRowCount(len(portfolio))
        total_value = 0
        total_cost_basis = 0

        for i, stock in enumerate(portfolio):
            ticker = stock["ticker"]
            shares = stock["shares"]
            buy_price = stock["buy_price"]

            self.holdings_table.setItem(i, 0, QTableWidgetItem(ticker))
            self.holdings_table.setItem(i, 1, QTableWidgetItem(f"{shares}"))

            try:
                historical_data = self.data_manager.get_historical_data(ticker)
                if historical_data.empty:
                    raise ValueError("No data returned")

                current_price = historical_data.iloc[-1]['Close']
                current_value = shares * current_price
                cost_basis = shares * buy_price
                gain_loss = current_value - cost_basis

                total_value += current_value
                total_cost_basis += cost_basis

                self.holdings_table.setItem(i, 2, QTableWidgetItem(f"${current_value:,.2f}"))
                self.holdings_table.setItem(i, 3, QTableWidgetItem(f"${gain_loss:+,_ .2f}"))

            except Exception as e:
                self.holdings_table.setItem(i, 2, QTableWidgetItem("N/A"))
                self.holdings_table.setItem(i, 3, QTableWidgetItem("N/A"))

        total_gain_loss = total_value - total_cost_basis
        self.total_value_label.setText(f"Total Portfolio Value: ${total_value:,.2f}")
        self.total_gain_loss_label.setText(f"Total Gain/Loss: ${total_gain_loss:+,_ .2f}")

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.refresh_label.setText(f"Last updated at: {timestamp}. Auto-refreshes every 60 seconds.")

    def showEvent(self, event):
        """Override showEvent to update dashboard when it becomes visible."""
        super().showEvent(event)
        self.update_dashboard()
