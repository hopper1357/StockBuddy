import json
import os

class SettingsManager:
    def __init__(self, filename="settings.json"):
        # Use a platform-independent path for application data
        home_dir = os.path.expanduser("~")
        app_dir = os.path.join(home_dir, ".stockbuddy")

        # Create the directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)

        self.filepath = os.path.join(app_dir, filename)
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file."""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default settings if file doesn't exist or is empty/corrupt
            return self.get_default_settings()

    def save_settings(self):
        """Saves the current settings to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get_setting(self, key, default=None):
        """Gets a specific setting by key."""
        # Use the provided default if the key is not in settings
        default_value = default if default is not None else self.get_default_settings().get(key)
        return self.settings.get(key, default_value)

    def set_setting(self, key, value):
        """Sets a specific setting and immediately saves it."""
        self.settings[key] = value
        self.save_settings()

    def get_default_settings(self):
        """Returns a dictionary of default settings."""
        return {
            "font_size": "Medium"  # Options: "Small", "Medium", "Large"
        }
