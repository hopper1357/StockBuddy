import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QTextEdit, QPushButton, QInputDialog, QMessageBox,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox)

from stockbuddy.core.preset_manager import PresetManager


class PresetEditDialog(QDialog):
    def __init__(self, preset_name="", preset_rules=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Preset")

        self.layout = QFormLayout(self)

        self.name_edit = QLineEdit(preset_name)
        self.rules_edit = QTextEdit(json.dumps(preset_rules, indent=4) if preset_rules else "")

        self.layout.addRow("Preset Name:", self.name_edit)
        self.layout.addRow("Rules (JSON):", self.rules_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

    def get_data(self):
        try:
            rules = json.loads(self.rules_edit.toPlainText())
            return self.name_edit.text(), rules
        except json.JSONDecodeError:
            return None, None


class PresetsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.preset_manager = PresetManager()

        # Main layout
        layout = QHBoxLayout(self)

        # Left side: List of presets
        left_layout = QVBoxLayout()
        self.preset_list_widget = QListWidget()
        self.preset_list_widget.itemSelectionChanged.connect(self.display_preset_details)
        left_layout.addWidget(self.preset_list_widget)

        # Buttons for preset management
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_preset)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_preset)

        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        left_layout.addLayout(button_layout)

        # Right side: Preset details
        right_layout = QVBoxLayout()
        self.preset_details_display = QTextEdit()
        self.preset_details_display.setReadOnly(True)
        right_layout.addWidget(self.preset_details_display)

        # Add left and right layouts to main layout
        layout.addLayout(left_layout, 1)  # 1/3 of the space
        layout.addLayout(right_layout, 2) # 2/3 of the space

        self.setLayout(layout)
        self.load_presets_into_list()

    def load_presets_into_list(self):
        self.preset_list_widget.clear()
        presets = self.preset_manager.get_all_presets()
        for name in presets.keys():
            self.preset_list_widget.addItem(name)

    def display_preset_details(self):
        selected_items = self.preset_list_widget.selectedItems()
        if not selected_items:
            self.preset_details_display.clear()
            return

        preset_name = selected_items[0].text()
        preset = self.preset_manager.get_preset(preset_name)
        if preset:
            # Pretty print the JSON rules
            details_text = json.dumps(preset.get("rules", {}), indent=4)
            self.preset_details_display.setText(details_text)

    def add_preset(self):
        dialog = PresetEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            name, rules = dialog.get_data()
            if name and rules is not None:
                self.preset_manager.add_preset(name, rules)
                self.load_presets_into_list()
            else:
                QMessageBox.warning(self, "Error", "Invalid JSON in rules or empty name.")

    def delete_preset(self):
        selected_items = self.preset_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a preset to delete.")
            return

        preset_name = selected_items[0].text()
        reply = QMessageBox.question(self, 'Delete Preset',
                                     f"Are you sure you want to delete '{preset_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.preset_manager.delete_preset(preset_name)
            self.load_presets_into_list()
            self.preset_details_display.clear()
