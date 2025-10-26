import React, { useState, useEffect } from "react";

function ManualPage() {
    const [buildings, setBuildings] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [selected, setSelected] = useState([]);
    const [search, setSearch] = useState("");
    const [results, setResults] = useState(null);

    const [start, setStart] = useState("");
    const [end, setEnd] = useState("");
    const [day, setDay] = useState("mon");

    const BACKEND = import.meta.env.VITE_API_BASE;
    //const BACKEND = "http://127.0.0.1:5001";

    // Load building list
    useEffect(() => {
        fetch(`${BACKEND}/api/buildings`)
            .then((res) => res.json())
            .then((data) => {
                const list = Array.isArray(data) ? data : data.buildings || [];
                setBuildings(list);
                setFiltered(list);
            })
            .catch((err) => {
                console.error("Error loading buildings:", err);
                setBuildings([]);
                setFiltered([]);
            });
    }, []);

    // Search filter
    useEffect(() => {
        const lower = search.toLowerCase();
        setFiltered(buildings.filter((b) => b.toLowerCase().includes(lower)));
    }, [search, buildings]);

    const toggleBuilding = (b) => {
        setSelected((prev) =>
            prev.includes(b) ? prev.filter((x) => x !== b) : [...prev, b]
        );
    };

    const calculate = () => {
        if (!start || !end || !day) {
            alert("Please select start time, end time, and day.");
            return;
        }
        fetch(`${BACKEND}/api/manual_average`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ buildings: selected, start, end, day }),
        })
            .then((r) => r.json())
            .then(setResults)
            .catch((err) =>
                console.error("Error fetching manual average:", err)
            );
    };

    return (
        <div className="p-6 container"  >
            <h1 className=" mt-3 text-center text-decoration-underline fw-bold text-xl font-bold mb-4">Manual Mode</h1>
            <div className="w-25 container px-5">
            {/* Search + scrollable checklist */}
            <input
                type="text"
                placeholder="Search buildings..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="border p-2 w-full mb-2"
            />
            <div
                style={{
                    maxHeight: "300px", // controls visible height
                    overflowY: "auto", // makes it scrollable
                    border: "1px solid #ccc",
                    padding: "8px",
                    marginBottom: "16px",
                }}
            >
                {filtered.map((b, i) => (
                    <div key={i}>
                        <label>
                            <input
                                type="checkbox"
                                checked={selected.includes(b)}
                                onChange={() => toggleBuilding(b)}
                            />
                            {b}
                        </label>
                    </div>
                ))}
            </div>
        </div>
        <div className="my-4 text-center">
            {/* Time + Day controls */}
            <span className="mx-2" > 
                <label className="me-2">Start Time: </label>
                <input
                    type="time"
                    value={start}
                    onChange={(e) => setStart(e.target.value)}
                />
            </span>
            <span className="mx-2">
                <label className="me-2">End Time: </label>
                <input
                    type="time"
                    value={end}
                    onChange={(e) => setEnd(e.target.value)}
                />
            </span>
            <span className="mx-2">
                <label className="me-2">Day: </label>
                <select value={day} onChange={(e) => setDay(e.target.value)}>
                    <option value="mon">Monday</option>
                    <option value="tue">Tuesday</option>
                    <option value="wed">Wednesday</option>
                    <option value="thu">Thursday</option>
                    <option value="fri">Friday</option>
                </select>
            </span >
            <div>
            <button
                onClick={calculate}
                className=" mt-4 px-4 py-2 bg-blue-600 text-white rounded"
            >
                Find Closest
            </button>
        </div>
    </div>
            {/* Results */}
            {results && results.top_buildings && (
                <div className="mt-6">
                    <h2 className="text-lg font-semibold">Top 3 Closest</h2>
                    {results.top_buildings.map((tb, i) => (
                        <div key={i} className="border p-2 my-4 rounded">
                            <p>
                                <strong>{tb.building}</strong>
                            </p>
                            <p>
                                Free Rooms:{" "}
                                {Array.isArray(tb.free_rooms) &&
                                tb.free_rooms.length > 0
                                    ? tb.free_rooms.join(", ")
                                    : "None"}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default ManualPage;
