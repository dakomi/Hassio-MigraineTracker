import json
import os

SETTINGS_FILE = "/data/settings.json"

DEFAULT_SETTINGS = {
    "tomorrow_io_api_key": "",
    "google_weather_api_key": "",
    "indoor_temp_sensor": None,
    "indoor_humidity_sensor": None,
    "fetch_frequency": "1h",
    "fetch_range_before": 3,
    "fetch_range_after": 1,
}

def get_settings():
    """
    Loads the settings from the settings file, applying defaults for any
    missing values.
    """
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
            # Apply defaults for any missing settings
            for key, value in DEFAULT_SETTINGS.items():
                if key not in settings:
                    settings[key] = value
            return settings
    else:
        return DEFAULT_SETTINGS

def save_settings(settings: dict):
    """
    Saves the settings to the settings file.
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
