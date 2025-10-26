import os
import json
import math
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import load_groups, save_groups

# -----------------------------
# App + CORS
# -----------------------------
app = Flask(__name__)

# In dev: allow Vite (localhost:5173). Add your Netlify URL when deployed.
CORS(app)

# accept both /path and /path/ without 404
app.url_map.strict_slashes = False

# -----------------------------
# Data loading helpers
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(filename, default):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

# Expected files (you already generated these earlier)
# - usable_buildings.json: ["Dreese Laboratories", "Bolz Hall", ...]
# - building_coords.json: {"Dreese Laboratories":[40.00,-83.01], ...}
# - building_classes.json:
#   {
#     "Dreese Laboratories": {
#        "rooms": ["100","201",...],
#        "classes": [
#           {"room":"201","startTime":"9:10 AM","endTime":"10:05 AM","days":{"mon":true,"tue":true,"wed":false,"thu":true,"fri":true}}
#        ]
#     }, ...
#   }
usable_buildings = load_json("buildings/usable_buildings.json", [])
building_coords   = load_json("buildings/building_coords.json", {})          # name -> [lat, lon]
building_data     = load_json("buildings/building_classes.json", {})         # name -> { rooms, classes }

# -----------------------------
# In-memory groups structure
# -----------------------------
# groups = { "groupName": { "members": { "userId": (lat, lon), ... } } }

groups = load_groups()

# -----------------------------
# Utility functions
# -----------------------------
def average_gps(*coords):
    """Spherical average of lat/lon pairs."""
    if not coords:
        raise ValueError("No coordinates to average.")
    x_total = y_total = z_total = 0.0
    for lat, lon in coords:
        lat_r = math.radians(lat)
        lon_r = math.radians(lon)
        x_total += math.cos(lat_r) * math.cos(lon_r)
        y_total += math.cos(lat_r) * math.sin(lon_r)
        z_total += math.sin(lat_r)
    n = len(coords)
    x, y, z = x_total/n, y_total/n, z_total/n
    lon_avg = math.atan2(y, x)
    hyp = math.sqrt(x*x + y*y)
    lat_avg = math.atan2(z, hyp)
    return math.degrees(lat_avg), math.degrees(lon_avg)

def haversine(a, b):
    R = 6371.0
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    s = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(s))

def parse_time_12h(s):
    """'9:10 AM' -> datetime.time; returns None if bad."""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%I:%M %p").time()
    except Exception:
        return None

def rooms_free_now(building_name, when=None, day_key=None):
    """
    Return list of free rooms for building at 'when' (datetime.time) on 'day_key' (mon,tue,...).
    Defaults: now + today's weekday.
    """
    if building_name not in building_data:
        return []

    bd = building_data[building_name]
    all_rooms = bd.get("rooms", [])
    classes = bd.get("classes", [])

    if when is None:
        when = datetime.now().time()

    if day_key is None:
        day_key = datetime.today().strftime("%a").lower()[:3]  # mon,tue,...

    occupied = set()
    for c in classes:
        room = c.get("room")
        if not room:
            continue
        days = (c.get("days") or {})
        if not days.get(day_key, False):
            continue
        st = parse_time_12h(c.get("startTime"))
        et = parse_time_12h(c.get("endTime"))
        if not st or not et:
            continue
        # overlap if st <= when < et
        if st <= when < et:
            occupied.add(room)

    return [r for r in all_rooms if r not in occupied]

# -----------------------------
# API Routes
# -----------------------------

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/api/buildings", methods=["GET"])
def get_buildings():
    return jsonify({"buildings": usable_buildings})

@app.route("/api/create_group", methods=["POST"])
def create_group():
    data = request.get_json(silent=True) or {}
    group = str(data.get("group") or "").strip()
    if not group:
        return jsonify({"error": "Group is required"}), 400
    if group in groups:
        # idempotent create
        return jsonify({"message": "Group already exists", "group": group}), 200
    groups[group] = {"members": {}}
    save_groups(groups)
    return jsonify({"message": "Group created", "group": group}), 200

@app.route("/api/join_group", methods=["POST"])
def join_group():
    data = request.get_json(silent=True) or {}
    group = str(data.get("group") or "").strip()
    user  = str(data.get("user") or "").strip()
    if not group or not user:
        return jsonify({"error": "Group and user are required"}), 400
    if group not in groups:
        return jsonify({"error": "Group not found"}), 404
    groups[group]["members"].setdefault(user, None)
    save_groups(groups)
    return jsonify({"message": f"{user} joined {group}"}), 200

@app.route("/api/manual_average", methods=["POST"])
def manual_average():
    data = request.json
    buildings = data.get("buildings", [])
    if not buildings:
        return jsonify({"error": "No buildings provided"}), 400

    coords = []
    for b in buildings:
        if b in building_coords:
            coords.append(tuple(building_coords[b]))
    if not coords:
        return jsonify({"error": "No valid building coordinates"}), 400

    avg_lat, avg_lon = average_gps(*coords)

    # Find top 3 closest buildings with available rooms
    today = datetime.today().strftime("%a").lower()[:3]
    now = datetime.now().time()
    candidates = []
    for b, coord in building_coords.items():
        if b not in building_data:
            continue
        dist = haversine((avg_lat, avg_lon), tuple(coord))
        occupied = set()
        for c in building_data[b]["classes"]:
            if not c["startTime"] or not c["endTime"]:
                continue
            if not c["days"].get(today, False):
                continue
            try:
                st = datetime.strptime(c["startTime"], "%I:%M %p").time()
                et = datetime.strptime(c["endTime"], "%I:%M %p").time()
            except:
                continue
            if not (et <= now or st >= now):
                occupied.add(c["room"])
        free_rooms = [r for r in building_data[b]["rooms"] if r not in occupied]
        if free_rooms:
            candidates.append((dist, b, free_rooms))

    candidates.sort(key=lambda x: x[0])
    top3 = [{"building": b, "free_rooms": rooms} for _, b, rooms in candidates[:3]]

    return jsonify({
        "average_location": [avg_lat, avg_lon],
        "top_buildings": top3,
        "selected_buildings": buildings
    })




@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.get_json(silent=True) or {}
    group = str(data.get("group") or "").strip()
    user  = str(data.get("user") or "").strip()
    lat   = data.get("lat", None)
    lon   = data.get("lon", None)

    if not group or not user or lat is None or lon is None:
        return jsonify({"error": "group, user, lat, lon required"}), 400
    if group not in groups:
        return jsonify({"error": "Group not found"}), 404

    # Auto-add user to group if not present (nice UX for hackathon)
    if user not in groups[group]["members"]:
        groups[group]["members"][user] = None

    # Update location
    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return jsonify({"error": "lat/lon must be numbers"}), 400

    groups[group]["members"][user] = (lat, lon)
    save_groups(groups)

    # Gather current known coords
    coords = [c for c in groups[group]["members"].values() if c]
    if not coords:
        return jsonify({"error": "No coordinates yet"}), 400

    # Average GPS
    avg_lat, avg_lon = average_gps(*coords)

    # Find top 3 closest buildings that have free rooms now
    now = datetime.now().time()
    today_key = datetime.today().strftime("%a").lower()[:3]

    candidates = []
    for bname, coord in building_coords.items():
        if bname not in building_data:
            continue
        try:
            dist = haversine((avg_lat, avg_lon), (coord[0], coord[1]))
        except Exception:
            continue
        free = rooms_free_now(bname, when=now, day_key=today_key)
        if free:
            candidates.append((dist, bname, free))

    candidates.sort(key=lambda t: t[0])
    top3 = [{"building": b, "free_rooms": rooms} for _, b, rooms in candidates[:3]]

    return jsonify({
        "average_location": [avg_lat, avg_lon],
        "top_buildings": top3,
        "members": list(groups[group]["members"].keys())
    }), 200

# -----------------------------
# Dev runner
# -----------------------------
def print_routes():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods))
        print(f"{rule.endpoint:20s} {methods:20s} {rule}")

if __name__ == "__main__":
    print_routes()
    app.run(host="0.0.0.0", port=5001, debug=True)

