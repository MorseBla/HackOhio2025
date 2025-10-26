import React, { useState, useEffect } from "react";

function App() {
  const [step, setStep] = useState("start"); // "start" | "group" | "results"
  const [group, setGroup] = useState("");
  const [user, setUser] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

    //const BACKEND = "http://127.0.0.1:5001"; 
  const BACKEND = import.meta.env.VITE_API_BASE;

    // Create group
  const createGroup = async () => {
    if (!group || !user) return;
    try {
      const res = await fetch(`${BACKEND}/api/create_group`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ group, user }),
      });
      if (!res.ok) throw new Error("Failed to create group");
      setStep("group");
      setError("");
    } catch (err) {
      setError("Error creating group");
    }
  };

  // Join group
  const joinGroup = async () => {
    if (!group || !user) return;
    try {
      const res = await fetch(`${BACKEND}/api/join_group`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ group, user }),
      });
      if (!res.ok) throw new Error("Failed to join group");
      setStep("group");
      setError("");
    } catch (err) {
      setError("Error joining group");
    }
  };

  // GPS loop
  useEffect(() => {
    if (step !== "group" || !group || !user) return;

    const sendLocation = () => {
      if (!navigator.geolocation) {
        setError("Geolocation not supported");
        return;
      }
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          try {
            const res = await fetch(`${BACKEND}/api/update_location`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                group,
                user,
                lat: pos.coords.latitude,
                lon: pos.coords.longitude,
              }),
            });
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

    sendLocation(); // initial
    const interval = setInterval(sendLocation, 15000); // update every 15s
    return () => clearInterval(interval);
  }, [step, group, user]);

  // UI
  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <h1>OSU Meeting Spot Finder</h1>

      {step === "start" && (
        <div>
          <input
            type="text"
            placeholder="Your Name"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            style={{ marginRight: "10px" }}
          />
          <input
            type="text"
            placeholder="Group Name"
            value={group}
            onChange={(e) => setGroup(e.target.value)}
          />
          <div style={{ marginTop: "10px" }}>
            <button onClick={createGroup} style={{ marginRight: "10px" }}>
              Create Group
            </button>
            <button onClick={joinGroup}>Join Group</button>
          </div>
        </div>
      )}

      {step === "group" && (
        <div>
          <h2>Group: {group}</h2>
          <p>Sharing GPS as <strong>{user}</strong>...</p>
          {error && <p style={{ color: "red" }}>{error}</p>}

          {results && results.top_buildings ? (
            <>
              <p>
                <strong>Average Location:</strong>{" "}
                {results.average_location?.map((c) => c.toFixed(5)).join(", ")}
              </p>
              <h3>Closest Available Buildings</h3>
              <ul>
                {results.top_buildings.map((b, i) => (
                  <li key={i}>
                    <strong>{b.building}</strong> — Free rooms:{" "}
                    {Array.isArray(b.free_rooms) && b.free_rooms.length > 0
                      ? b.free_rooms.join(", ")
                      : "None"}
                  </li>
                ))}
              </ul>
              <h3>Members</h3>
              <ul>
                {results.members?.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </>
          ) : (
            <p>Waiting for updates...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

