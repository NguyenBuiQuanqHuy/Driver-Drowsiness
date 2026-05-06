from datetime import datetime
import json
import os

FILE_PATH = "history.json"

def clear_history():
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception as e:
        print("Clear error:", e)
        
def load_history():
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []  # tránh crash nếu file lỗi


def save_alert(alert_type, data=None):
    history = load_history()

    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": alert_type,
        "ear": data.get("ear") if data else None,
        "mar": data.get("mar") if data else None,
        "head": data.get("head") if data else None
    }

    history.append(record)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)