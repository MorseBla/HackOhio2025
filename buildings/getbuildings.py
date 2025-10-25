import csv
import json
import requests
import time

API = "https://content.osu.edu/v2/classes/search"
TERM = "1258"   # Autumn 2024 (change if needed)

usable_buildings = set()

with open("buildings.csv", "r") as f:
    reader = csv.reader(f)
    all_buildings = [row[0].strip() for row in reader if row]

for building in all_buildings:
    print(f"Checking {building}...")
    try:
        resp = requests.get(API, params={"q": building, "term": TERM, "p": 1}, timeout=10)
    except Exception as e:
        print(f"  ❌ Error querying {building}: {e}")
        continue

    if resp.status_code != 200:
        print(f"  ❌ Skipped {building} (HTTP {resp.status_code})")
        continue

    data = resp.json().get("data", {})
    courses = data.get("courses", [])

    found = False
    for course in courses:
        for sec in course.get("sections", []):
            for m in sec.get("meetings", []):
                facility = m.get("facilityDescription")
                if facility and building.lower() in facility.lower():
                    usable_buildings.add(facility)  # save API's canonical name
                    print(f"  ✅ Found: {facility}")
                    found = True
                    break
            if found:
                break
        if found:
            break

    # be nice to the API
    time.sleep(0.2)

# Save usable list
with open("usable_buildings2.json", "w") as f:
    json.dump(sorted(usable_buildings), f, indent=2)

print(f"\n✅ Found {len(usable_buildings)} usable buildings")

