import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget,
                             QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem, QScrollArea)
from PyQt5.QtCore import QTimer, Qt
from stockbuddy.data.data_manager import DataManager
from stockbuddy.data.database_manager import DatabaseManager
from stockbuddy.gui.dashboard_widget import DashboardWidget
from stockbuddy.gui.watchlist_widget import WatchlistWidget
from stockbuddy.gui.portfolio_widget import PortfolioWidget
from stockbuddy.gui.presets_widget import PresetsWidget
from stockbuddy.gui.settings_widget import SettingsWidget
from stockbuddy.core.settings_manager import SettingsManager
from stockbuddy.core.preset_manager import PresetManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockBuddy")
        self.setGeometry(100, 100, 1200, 800)

        self.settings_manager = SettingsManager()
        self.preset_manager = PresetManager()
        self.db_manager = DatabaseManager()
        self.font_sizes = {"Small": "10pt", "Medium": "12pt", "Large": "15pt"}

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

        # Apply initial font size
        initial_font_size = self.settings_manager.get_setting("font_size")
        self.apply_font_size(initial_font_size)

    def setup_ui(self):
        # Add items to sidebar and widgets to stacked_widget
        # Pass managers to widgets that need them
        self.views = {
            "Dashboard": DashboardWidget(self.db_manager),
            "Watchlist": WatchlistWidget(self.settings_manager, self.preset_manager, self.db_manager),
            "Portfolio": PortfolioWidget(self.db_manager),
            "Presets": PresetsWidget(self.settings_manager, self.preset_manager),
            "Settings": SettingsWidget(self.settings_manager)
        }

        for name, widget in self.views.items():
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)

            # Wrap each widget in a scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(widget)
            # Set scrollbar policies
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            self.stacked_widget.addWidget(scroll_area)

            # Connect the signal from the settings widget
            if isinstance(widget, SettingsWidget):
                widget.font_size_changed.connect(self.apply_font_size)

        # Connect preset changes to watchlist updates
        self.views["Presets"].active_preset_changed.connect(self.views["Watchlist"].update_watchlist)

    def apply_font_size(self, size_str):
        """Applies the selected font size globally."""
        font_size = self.font_sizes.get(size_str, "12pt") # Default to Medium
        # Use the universal selector '*' to apply the font size to all widgets
        stylesheet = f"* {{ font-size: {font_size}; }}"
        QApplication.instance().setStyleSheet(stylesheet)

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
