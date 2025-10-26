import json
import os

FILE = "groups.json"

def load_groups():
    # If the file doesn't exist, create it with an empty dict
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({}, f)
        return {}

    # Otherwise, load and return its contents
    with open(FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If file is empty or corrupted, reset it
            return {}

def save_groups(groups):
    with open(FILE, "w") as f:
        json.dump(groups, f, indent=2)

