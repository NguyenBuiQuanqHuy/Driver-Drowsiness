import json
import os

FILE_PATH = "settings.json"


def load_settings():

    default = {
        "theme": "Dark",
        "voice_language": "English",
        "volume": 100
    }

    if not os.path.exists(FILE_PATH):
        return default

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return default


def save_settings(data):

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)