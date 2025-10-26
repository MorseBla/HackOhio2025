import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

function GroupPage() {
    const { state } = useLocation();
    const { group, user } = state || {};
    const [results, setResults] = useState(null);
    const [error, setError] = useState("");

    const [start, setStart] = useState("");
    const [end, setEnd] = useState("");
    const [day, setDay] = useState("mon");

    const BACKEND = import.meta.env.VITE_API_BASE;
    //const BACKEND = "http://127.0.0.1:5001";

    // GPS + update loop
    useEffect(() => {
        if (!group || !user || !start || !end || !day) return;

        const sendLocation = () => {
            if (!navigator.geolocation) {
                setError("Geolocation not supported");
                return;
            }
            navigator.geolocation.getCurrentPosition(
                async (pos) => {
                    try {
                        const res = await fetch(
                            `${BACKEND}/api/update_location`,
                            {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    group,
                                    user,
                                    lat: pos.coords.latitude,
                                    lon: pos.coords.longitude,
                                    start,
                                    end,
                                    day,
                                }),
                            }
                        );
                        if (!res.ok) {
                            const txt = await res.text();
                            setError(`Update error: ${txt}`);
                            return;
                        }
                        const data = await res.json();
                        setResults(data);
                    } catch (err) {
                        setError("Failed to update location");
                    }
                },
                (err) => setError("GPS error: " + err.message),
                { enableHighAccuracy: true }
            );
        };

        sendLocation();
        const interval = setInterval(sendLocation, 15000);
        return () => clearInterval(interval);
    }, [group, user, start, end, day]);

    return (
        <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
            <h1 className="text-center fw-bold text-xl font-bold mb-5">
                Group: {group}
            </h1>
            <div className="">
                <p className="text-center">
                    Sharing as <strong>{user}</strong>
                </p>
                {error && <p style={{ color: "red" }}>{error}</p>}

                {/* Time + Day controls */}
                <div className="my-2 text-center">
                    <label className="me-2">Start Time: </label>
                    <input
                        type="time"
                        value={start}
                        onChange={(e) => setStart(e.target.value)}
                    />
                </div>
                <div className="my-2 text-center">
                    <label className="me-2">End Time: </label>
                    <input
                        type="time"
                        value={end}
                        onChange={(e) => setEnd(e.target.value)}
                    />
                </div>
                <div className="my-2 text-center">
                    <label className="me-2">Day: </label>
                    <select
                        value={day}
                        onChange={(e) => setDay(e.target.value)}
                    >
                        <option value="mon">Monday</option>
                        <option value="tue">Tuesday</option>
                        <option value="wed">Wednesday</option>
                        <option value="thu">Thursday</option>
                        <option value="fri">Friday</option>
                    </select>
                </div>

                {results && results.top_buildings ? (
                    <>
                        <div className="mt-6">
                            <h2 className="text-center mt-5 text-lg font-semibold">
                                Top 3 Closest
                            </h2>
                            {results.top_buildings.map((tb, i) => (
                                <div
                                    key={i}
                                    className="border p-2 my-4 rounded"
                                >
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
                    </>
                ) : (
                    <p className="text-center mt-5">Waiting for updates...</p>
                )}
            </div>
        </div>
    );
}

export default GroupPage;
