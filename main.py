import os
import json
import math
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import load_groups, save_groups
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app) 
app.url_map.strict_slashes = False

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

usable_buildings = load_json("buildings/usable_buildings.json", [])
building_coords   = load_json("buildings/building_coords.json", {})
building_data     = load_json("buildings/building_classes.json", {})

groups = load_groups()




def rooms_free_now(building_name, when=None, day_key=None, start=None, end=None):
    if building_name not in building_data:
        return []

    bd = building_data[building_name]
    all_rooms = bd.get("rooms", [])
    classes = bd.get("classes", [])

    if day_key is None:
        day_key = datetime.today().strftime("%a").lower()[:3]  # mon, tue, etc.

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

        if start and end:
            # Overlap check for range
            if not (et <= start or st >= end):
                occupied.add(room)
        elif when:
            # Point-in-time check
            if st <= when < et:
                occupied.add(room)

    return [r for r in all_rooms if r not in occupied]







def parse_time_12h(s):
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%I:%M %p").time()
    except Exception:
        return None


def average_gps(*coords):
    if not coords:
        raise ValueError("No coordinates to average.")
    x_total = y_total = z_total = 0.0
    for lat, lon in coords:
        lat_r, lon_r = math.radians(lat), math.radians(lon)
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
    dlat, dlon = lat2 - lat1, lon2 - lon1
    s = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(s))

def parse_time_24h(s):
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%H:%M").time()
    except:
        return None

def rooms_free_in_range(building_name, start, end, day_key):
    if building_name not in building_data:
        return []
    bd = building_data[building_name]
    all_rooms, classes = bd.get("rooms", []), bd.get("classes", [])

    occupied = set()
    for c in classes:
        room = c.get("room")
        if not room: 
            continue
        if not (c.get("days") or {}).get(day_key, False):
            continue
        st = datetime.strptime(c["startTime"], "%I:%M %p").time() if c.get("startTime") else None
        et = datetime.strptime(c["endTime"], "%I:%M %p").time() if c.get("endTime") else None
        if not st or not et:
            continue
        if st < end and et > start:
            occupied.add(room)
    return [r for r in all_rooms if r not in occupied]

def get_buildings():
    return jsonify({"buildings": usable_buildings})

@app.route("/api/create_group", methods=["POST"])
def create_group():
    data = request.get_json(silent=True) or {}
    group = str(data.get("group") or "").strip()
    user  = str(data.get("user") or "").strip()
    start = str(data.get("start") or "").strip()
    end   = str(data.get("end") or "").strip()
    day   = str(data.get("day") or "").strip()

    if not group:
        return jsonify({"error": "Group is required"}), 400
    if group in groups:
        return jsonify({"message": "Group already exists", "group": group}), 200

    groups[group] = {"members": {}, "start": start, "end": end, "day": day}
    save_groups(groups)
    return jsonify({"message": "Group created", "group": group}), 200

@app.route("/api/join_group", methods=["POST"])
def join_group():
    data = request.get_json(silent=True) or {}
    group, user = str(data.get("group") or "").strip(), str(data.get("user") or "").strip()
    if not group or not user:
        return jsonify({"error": "Group and user are required"}), 400
    if group not in groups:
        return jsonify({"error": "Group not found"}), 404

    groups[group]["members"].setdefault(user, None)
    save_groups(groups)
    return jsonify({
        "message": f"{user} joined {group}",
        "time_range": [groups[group].get("start"), groups[group].get("end")],
        "day": groups[group].get("day")
    }), 200

@app.route("/api/manual_average", methods=["POST"])
def manual_average():
    data = request.json or {}
    buildings = data.get("buildings", [])
    start_str, end_str, day_key = data.get("start",""), data.get("end",""), data.get("day","").lower()

    if not buildings:
        return jsonify({"error": "No buildings provided"}), 400

    coords = [tuple(building_coords[b]) for b in buildings if b in building_coords]
    if not coords:
        return jsonify({"error": "No valid building coordinates"}), 400
    avg_lat, avg_lon = average_gps(*coords)

    start, end = parse_time_24h(start_str), parse_time_24h(end_str)
    if not start or not end:
        return jsonify({"error": "Invalid time range"}), 400
    if not day_key:
        day_key = datetime.today().strftime("%a").lower()[:3]

    candidates = []
    for b, coord in building_coords.items():
        if b not in building_data:
            continue
        dist = haversine((avg_lat, avg_lon), tuple(coord))
        free = rooms_free_in_range(b, start, end, day_key)
        if free:
            candidates.append((dist, b, free))

    candidates.sort(key=lambda x: x[0])
    top3 = [{"building": b, "free_rooms": rooms} for _, b, rooms in candidates[:3]]

    return jsonify({
        "average_location": [avg_lat, avg_lon],
        "top_buildings": top3,
        "selected_buildings": buildings,
        "time_range": [start_str, end_str],
        "day": day_key
    })

    

@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.get_json(silent=True) or {}
    group = str(data.get("group") or "").strip()
    user  = str(data.get("user") or "").strip()
    lat   = data.get("lat", None)
    lon   = data.get("lon", None)
 
    start_time = data.get("startTime")
    end_time   = data.get("endTime")
    day_key    = data.get("day")
    
    if not group or not user or lat is None or lon is None:
        return jsonify({"error": "group, user, lat, lon required"}), 400
    
    if user not in groups[group]["members"]:
        groups[group]["members"][user] = None


    if group not in groups:
        return jsonify({"error": f"Group '{group}' not found. Please create or join first."}), 404

    if group not in groups:
        groups[group] = {"members": {}}



    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return jsonify({"error": "lat/lon must be numbers"}), 400

    groups[group]["members"][user] = (lat, lon)
    save_groups(groups)

    coords = [c for c in groups[group]["members"].values() if c]
    if not coords:
        return jsonify({"error": "No coordinates yet"}), 400

    avg_lat, avg_lon = average_gps(*coords)

    if start_time and end_time:
        try:
            start = parse_time_12h(start_time)
            end   = parse_time_12h(end_time)
        except:
            start, end = None, None
    else:
        now = datetime.now().time()
        start, end = now, now


    if not day_key:
        day_key = datetime.today().strftime("%a").lower()[:3]
    
    candidates = []
    for bname, coord in building_coords.items():
        if bname not in building_data:
            continue
        try:
            dist = haversine((avg_lat, avg_lon), (coord[0], coord[1]))
        except Exception:
            continue
        free = rooms_free_now(bname, when=start, day_key=day)
        if free:
            candidates.append((dist, bname, free))
        
        candidates.sort(key=lambda t: t[0]) 

        top3 = [{"building": b, "free_rooms": rooms} for _, b, rooms in candidates[:3]]



    return jsonify({
        "average_location": [avg_lat, avg_lon],
        "top_buildings": top3,
        "members": list(groups[group]["members"].keys()),
    }), 200





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

