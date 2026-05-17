import json
import os


SETTINGS_FILE = "settings.json"


DEFAULT_SETTINGS = {

    "theme": "Dark",

    "voice_language": "English"
}


# =========================================
# LOAD SETTINGS
# =========================================
def load_settings():

    if not os.path.exists(SETTINGS_FILE):

        save_settings(DEFAULT_SETTINGS)

    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# =========================================
# SAVE SETTINGS
# =========================================
def save_settings(data):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )