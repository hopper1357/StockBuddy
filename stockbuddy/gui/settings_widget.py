from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Settings View")
        layout.addWidget(label)
        self.setLayout(layout)
