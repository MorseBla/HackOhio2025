import json
import requests
import time

API = "https://content.osu.edu/v2/classes/search"
TERM = "1258"   # Autumn 2024

with open("usable_buildings.json", "r") as f:
    buildings = json.load(f)

building_data = {}

for building in buildings:
    print(f"Fetching classes for {building}...")
    page = 1
    classes = []
    rooms = set()

    while True:
        resp = requests.get(API, params={"q": building, "term": TERM, "p": page}, timeout=10)
        if resp.status_code != 200:
            print(f"  ❌ Error {resp.status_code} for {building}")
            break

        data = resp.json().get("data", {})
        courses = data.get("courses", [])

        for course in courses:
            for sec in course.get("sections", []):
                for m in sec.get("meetings", []):
                    facility = m.get("facilityDescription")
                    room = m.get("room")

                    if facility and building.lower() in facility.lower():
                        if room:
                            rooms.add(room)

                        classes.append({
                            "room": room,
                            "startTime": m.get("startTime"),
                            "endTime": m.get("endTime"),
                            "days": {
                                "mon": m.get("monday"),
                                "tue": m.get("tuesday"),
                                "wed": m.get("wednesday"),
                                "thu": m.get("thursday"),
                                "fri": m.get("friday"),
                                "sat": m.get("saturday"),
                                "sun": m.get("sunday")
                            }
                        })

        # pagination
        next_page = data.get("nextPageLink")
        if not next_page:
            break

        page += 1
        time.sleep(0.2)

    building_data[building] = {
        "rooms": sorted(list(rooms)),
        "classes": classes
    }
    print(f"  ✅ {len(classes)} classes, {len(rooms)} rooms for {building}")

# Save
with open("building_classes.json", "w") as f:
    json.dump(building_data, f, indent=2)

print("\nDone! Data saved to building_classes.json")

