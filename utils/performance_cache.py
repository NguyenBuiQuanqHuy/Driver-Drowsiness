import json
import os

FILE = "data\performance_cache.json"


def save_metrics(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_metrics():
    if not os.path.exists(FILE):
        return None

    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)