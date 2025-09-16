import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget,
                             QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem)
from PyQt5.QtCore import QTimer, Qt
from stockbuddy.data.data_manager import DataManager
from stockbuddy.gui.dashboard_widget import DashboardWidget
from stockbuddy.gui.watchlist_widget import WatchlistWidget
from stockbuddy.gui.presets_widget import PresetsWidget
from stockbuddy.gui.settings_widget import SettingsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockBuddy")
        self.setGeometry(100, 100, 1200, 800)

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(150)
        layout.addWidget(self.sidebar)

        # Stacked Widget for content
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        self.setup_ui()
        self.sidebar.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)

        # Top bar for indexes
        self.index_bar = self.statusBar()
        self.index_label = QLabel("Indexes: Loading...")
        self.index_bar.addPermanentWidget(self.index_label)

        self.data_manager = DataManager()
        self.update_index_data()

        # Update every 60 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_index_data)
        self.timer.start(60000)

    def setup_ui(self):
        # Add items to sidebar and widgets to stacked_widget
        views = {
            "Dashboard": DashboardWidget(),
            "Watchlist": WatchlistWidget(),
            "Presets": PresetsWidget(),
            "Settings": SettingsWidget()
        }

        for name, widget in views.items():
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)
            self.stacked_widget.addWidget(widget)

    def update_index_data(self):
        tickers = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow",
            "^IXIC": "Nasdaq",
            "^RUT": "Russell 2000"
        }
        try:
            data = self.data_manager.get_index_data(list(tickers.keys()))

            if not data.empty and 'Close' in data:
                latest_prices = data['Close'].iloc[-1]
                display_text = " | ".join(
                    f"{name}: {latest_prices[ticker]:.2f}"
                    for ticker, name in tickers.items() if ticker in latest_prices
                )
                self.index_label.setText(display_text)
            else:
                self.index_label.setText("Failed to retrieve index data.")
        except Exception as e:
            self.index_label.setText(f"Error fetching index data.")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
