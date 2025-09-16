from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class WatchlistWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Watchlist View")
        layout.addWidget(label)
        self.setLayout(layout)
