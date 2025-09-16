from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Dashboard View")
        layout.addWidget(label)
        self.setLayout(layout)
