from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # allow all origins (frontend can be on any port)

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "../buildings/usable_buildings.json"), "r") as f:
    usable_buildings = json.load(f)

with open(os.path.join(base_dir, "../buildings/building_classes.json"), "r") as f:
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)

