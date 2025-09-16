from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class PresetsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Presets View")
        layout.addWidget(label)
        self.setLayout(layout)
