from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox)
from PyQt5.QtCore import pyqtSignal
from stockbuddy.core.settings_manager import SettingsManager

class SettingsWidget(QWidget):
    # Signal to notify the main window that the font size has changed
    font_size_changed = pyqtSignal(str)

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # --- Font Size Setting ---
        font_layout = QHBoxLayout()

        font_label = QLabel("Application Font Size:")
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Small", "Medium", "Large"])

        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        font_layout.addStretch()

        # Load the saved font size and set the combo box
        current_font_size = self.settings_manager.get_setting("font_size")
        self.font_combo.setCurrentText(current_font_size)

        # Connect the signal after setting the initial value to avoid premature emission
        self.font_combo.currentTextChanged.connect(self._on_font_size_changed)

        # Add the font settings layout to the main layout
        layout.addLayout(font_layout)
        layout.addStretch() # Pushes the UI to the top

        self.setLayout(layout)

    def _on_font_size_changed(self, size_str):
        """
        Called when the user selects a new font size.
        Saves the setting and emits a signal.
        """
        self.settings_manager.set_setting("font_size", size_str)
        self.font_size_changed.emit(size_str)
