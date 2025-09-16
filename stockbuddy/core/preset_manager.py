import json
import os

class PresetManager:
    def __init__(self, filename="presets.json"):
        home_dir = os.path.expanduser("~")
        app_dir = os.path.join(home_dir, ".stockbuddy")
        os.makedirs(app_dir, exist_ok=True)
        self.filepath = os.path.join(app_dir, filename)
        self.presets = self.load_presets()

    def load_presets(self):
        """Loads presets from the JSON file."""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_presets()

    def save_presets(self):
        """Saves the current presets to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.presets, f, indent=4)

    def get_preset(self, name):
        """Gets a specific preset by name."""
        return self.presets.get(name)

    def add_preset(self, name, rules):
        """Adds a new preset and saves it."""
        self.presets[name] = {"rules": rules}
        self.save_presets()

    def delete_preset(self, name):
        """Deletes a preset and saves the changes."""
        if name in self.presets:
            del self.presets[name]
            self.save_presets()

    def get_all_presets(self):
        """Returns a dictionary of all presets."""
        return self.presets

    def get_default_presets(self):
        """Returns a dictionary of default presets."""
        return {
            "Conservative Growth": {
                "rules": [
                    {"indicator": "SMA", "period": 200, "condition": ">", "value": "Price", "action": "Buy"},
                    {"indicator": "RSI", "period": 14, "condition": "<", "value": 30, "action": "Buy"},
                ]
            },
            "Aggressive Momentum": {
                "rules": [
                    {"indicator": "Golden Cross", "short_period": 50, "long_period": 200, "condition": "crosses_above", "value": "Price", "action": "Buy"},
                    {"indicator": "MACD", "fast_period": 12, "slow_period": 26, "signal_period": 9, "condition": "crosses_above_signal", "action": "Buy"},
                ]
            },
            "Sell High": {
                "rules": [
                    {"indicator": "RSI", "period": 14, "condition": ">", "value": 70, "action": "Sell"}
                ]
            },
            "Bollinger Bands Buy": {
                "rules": [
                    {"indicator": "Bollinger Bands", "period": 20, "std_dev": 2, "condition": "price_crosses_below_lower_band", "action": "Buy"}
                ]
            },
            "Stochastic Oscillator Buy": {
                "rules": [
                    {"indicator": "Stochastic Oscillator", "k_period": 14, "d_period": 3, "condition": "<", "value": 20, "action": "Buy"}
                ]
            },
            "Death Cross Sell": {
                "rules": [
                    {"indicator": "Death Cross", "short_period": 50, "long_period": 200, "condition": "crosses_below", "value": "Price", "action": "Sell"}
                ]
            }
        }
