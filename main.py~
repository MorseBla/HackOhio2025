from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import math
from datetime import datetime

app = Flask(__name__)
CORS(app)  # allow requests from frontend

# --- Load data ---
base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "buildings/usable_buildings.json"), "r") as f:
    usable_buildings = json.load(f)

with open(os.path.join(base_dir, "buildings/building_classes.json"), "r") as f:
    building_data = json.load(f)

with open(os.path.join(base_dir, "buildings/building_coords.json"), "r") as f:
    building_coords = json.load(f)


# --- Utility functions ---
def average_gps(*coords):
    """Return spherical average of lat/lon coords."""
    if not coords:
        raise ValueError("At least one coordinate must be provided.")

    x_total = y_total = z_total = 0.0
    for lat, lon in coords:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        x_total += math.cos(lat_rad) * math.cos(lon_rad)
        y_total += math.cos(lat_rad) * math.sin(lon_rad)
        z_total += math.sin(lat_rad)

    num_points = len(coords)
    x_avg = x_total / num_points
    y_avg = y_total / num_points
    z_avg = z_total / num_points

    lon_avg = math.atan2(y_avg, x_avg)
    hyp = math.sqrt(x_avg**2 + y_avg**2)
    lat_avg = math.atan2(z_avg, hyp)

    return math.degrees(lat_avg), math.degrees(lon_avg)


def haversine(coord1, coord2):
    """Distance in km between two (lat, lon)."""
    R = 6371
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


# --- Routes ---
@app.route("/api/buildings", methods=["GET"])
def get_buildings():
    return jsonify({"buildings": usable_buildings})


@app.route("/api/buildings/<building_name>", methods=["GET"])
def get_building_classes(building_name):
    if building_name not in building_data:
        return jsonify({"error": "Building not found"}), 404
    return jsonify(building_data[building_name])


@app.route("/api/meeting-spot", methods=["POST"])
def meeting_spot():
    data = request.json
    building_list = data.get("buildings", [])
    start_str = data.get("start")
    end_str = data.get("end")
    day = data.get("day", "mon").lower()

    if not building_list:
        return jsonify({"error": "No buildings provided"}), 400

    coords = [tuple(building_coords[b]) for b in building_list if b in building_coords]
    if not coords:
        return jsonify({"error": "No valid buildings with coordinates"}), 400

    avg_lat, avg_lon = average_gps(*coords)

    try:
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
    except Exception:
        return jsonify({"error": "Invalid start/end time"}), 400

    # Sort buildings by distance to average location
    distances = []
    for b, coord in building_coords.items():
        dist = haversine((avg_lat, avg_lon), tuple(coord))
        distances.append((dist, b))
    distances.sort()

    # Try buildings in order until free rooms are found
    for _, candidate in distances:
        if candidate not in building_data:
            continue

        occupied_rooms = set()
        data_b = building_data[candidate]

        for c in data_b["classes"]:
            if not c["startTime"] or not c["endTime"]:
                continue
            if not c["days"].get(day, False):
                continue
            try:
                class_start = datetime.strptime(c["startTime"], "%I:%M %p").time()
                class_end = datetime.strptime(c["endTime"], "%I:%M %p").time()
            except ValueError:
                continue
            # overlap check
            if not (class_end <= start_time or class_start >= end_time):
                occupied_rooms.add(c["room"])

        free_rooms = [r for r in data_b["rooms"] if r not in occupied_rooms]

        if free_rooms:  # return first building with available rooms
            return jsonify({
                "closest_building": candidate,
                "average_location": [avg_lat, avg_lon],
                "free_rooms": free_rooms,
                "occupied_rooms": list(occupied_rooms)
            })

    # If no free rooms in any building
    return jsonify({
        "closest_building": None,
        "average_location": [avg_lat, avg_lon],
        "free_rooms": [],
        "occupied_rooms": []
    })


# --- Run ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

