from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_BASE = "https://content.osu.edu/v2/classes/search"

# Pick a known working term code (Autumn 2024 = 1248, Spring 2025 = 1252, Summer 2025 = 1254, Autumn 2025 = 1258)
DEFAULT_TERM = "1248"

@app.get("/taken")
def taken(
    building: str = Query(..., description="Building name, e.g. 'Dreese Laboratories'"),
    term: str = Query(DEFAULT_TERM, description="OSU term code, default Autumn 2024"),
    pages: int = Query(3, description="How many pages of results to fetch")
):
    """
    Example: /taken?building=Dreese%20Laboratories&term=1248
    """
    results = []

    for p in range(1, pages + 1):
        resp = requests.get(API_BASE, params={
            "q": building,
            "term": term,
            "p": p
        })
        if resp.status_code != 200:
            return {"error": f"API request failed with status {resp.status_code}"}
        data = resp.json()

        for course in data.get("data", {}).get("courses", []):
            for sec in course.get("sections", []):
                for m in sec.get("meetings", []):
                    facility = m.get("facilityDescription", "")
                    if facility and building.lower() in facility.lower():
                        results.append({
                            "courseTitle": sec.get("courseTitle"),
                            "subject": sec.get("subject"),
                            "catalogNumber": sec.get("catalogNumber"),
                            "section": sec.get("section"),
                            "room": m.get("room"),
                            "building": facility,
                            "startTime": m.get("startTime"),
                            "endTime": m.get("endTime"),
                            "days": {
                                "mon": m.get("monday"),
                                "tue": m.get("tuesday"),
                                "wed": m.get("wednesday"),
                                "thu": m.get("thursday"),
                                "fri": m.get("friday"),
                                "sat": m.get("saturday"),
                                "sun": m.get("sunday"),
                            },
                            "instructors": [i["displayName"] for i in m.get("instructors", [])],
                            "capacity": m.get("facilityCapacity"),
                            "startDate": m.get("startDate"),
                            "endDate": m.get("endDate")
                        })

    return {
        "building": building,
        "term": term,
        "taken_slots": results
    }

