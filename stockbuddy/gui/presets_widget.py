import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QTextEdit, QPushButton, QInputDialog, QMessageBox,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox)
from PyQt5.QtGui import QFont

from stockbuddy.core.preset_manager import PresetManager
from stockbuddy.core.settings_manager import SettingsManager


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
    def __init__(self, settings_manager: SettingsManager, preset_manager: PresetManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.preset_manager = preset_manager

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

        button_layout.addStretch()

        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)

        self.set_active_button = QPushButton("Set as Active")
        self.set_active_button.clicked.connect(self.set_active_preset)


        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(help_button)
        left_layout.addLayout(button_layout)
        left_layout.addWidget(self.set_active_button)

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
        active_preset_name = self.settings_manager.get_active_preset()

        for name in presets.keys():
            item = QListWidgetItem(name)
            if name == active_preset_name:
                font = QFont()
                font.setBold(True)
                item.setFont(font)
            self.preset_list_widget.addItem(item)

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

    def set_active_preset(self):
        selected_items = self.preset_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a preset to set as active.")
            return

        preset_name = selected_items[0].text()
        self.settings_manager.set_active_preset(preset_name)
        self.load_presets_into_list() # Reload to update the bolded item

    def show_help(self):
        help_title = "Preset Creation Help"
        help_text = """
        <p><b>How to Create Your Own Preset:</b></p>
        <ol>
            <li>Click the "Add" button.</li>
            <li>In the dialog, provide a unique name for your preset.</li>
            <li>Edit the JSON rules in the text box. Each preset is a collection of rules.</li>
        </ol>
        <p><b>Understanding the Rule Terms:</b></p>
        <ul>
            <li><b>indicator:</b> The technical indicator to use (e.g., "SMA", "RSI", "MACD").</li>
            <li><b>period:</b> The time period for the indicator (e.g., 14 for a 14-day RSI). Some indicators like "Golden Cross" have `short_period` and `long_period`.</li>
            <li><b>condition:</b> The comparison operator (e.g., ">" for greater than, "<" for less than, "crosses_above").</li>
            <li><b>value:</b> The threshold to check against. This can be a number (e.g., 70 for RSI) or a string like "Price".</li>
            <li><b>action:</b> The signal to generate if the condition is met (e.g., "Buy" or "Sell").</li>
        </ul>
        <p><b>Example Rule:</b></p>
        <pre>
{
    "indicator": "RSI",
    "period": 14,
    "condition": ">",
    "value": 70,
    "action": "Sell"
}
        </pre>
        <p>This rule means: "If the 14-day RSI is greater than 70, generate a 'Sell' signal."</p>
        """
        QMessageBox.information(self, help_title, help_text)
