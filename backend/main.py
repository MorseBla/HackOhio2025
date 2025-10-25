from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "../buildings/usable_buildings2.json"), "r") as f:
    usable_buildings = json.load(f)

with open(os.path.join(base_dir, "../buildings/building_classes2.json"), "r") as f:
    building_data = json.load(f)


@app.route("/api/buildings", methods=["GET"])
def get_buildings():
    return jsonify(usable_buildings)


@app.route("/api/buildings/<building_name>", methods=["GET"])
def get_building(building_name):
    building_name = building_name.replace("%20", " ")
    if building_name in building_data:
        return jsonify(building_data[building_name])
    else:
        return jsonify({"error": "Building not found"}), 404


@app.route("/api/availability/<building_name>", methods=["GET"])
def get_availability(building_name):
    building_name = building_name.replace("%20", " ")
    start_str = request.args.get("start")  # "13:00"
    end_str = request.args.get("end")      # "15:00"
    day = request.args.get("day", "mon").lower()

    if building_name not in building_data:
        return jsonify({"error": "Building not found"}), 404
    if not start_str or not end_str:
        return jsonify({"error": "Missing 'start' or 'end' parameter"}), 400

    # Parse input times
    try:
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Times must be in HH:MM format"}), 400

    data = building_data[building_name]
    occupied_rooms = set()

    for c in data["classes"]:
        if not c["startTime"] or not c["endTime"]:
            continue
        if not c["days"].get(day, False):
            continue

        try:
            class_start = datetime.strptime(c["startTime"], "%I:%M %p").time()
            class_end = datetime.strptime(c["endTime"], "%I:%M %p").time()
        except ValueError:
            continue

        # Check overlap
        if not (class_end <= start_time or class_start >= end_time):
            occupied_rooms.add(c["room"])

    free_rooms = [r for r in data["rooms"] if r not in occupied_rooms]

    return jsonify({
        "building": building_name,
        "day": day,
        "requested_range": f"{start_str}–{end_str}",
        "free_rooms": free_rooms,
        "occupied_rooms": list(occupied_rooms)
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

