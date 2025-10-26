import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GROUPS_FILE = os.path.join(BASE_DIR, "groups.json")

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(GROUPS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_groups(groups):
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=2)

