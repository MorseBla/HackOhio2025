import { useState } from "react";
import usableBuildings from "../../buildings/usable_buildings2.json";

function App() {
  const [selected, setSelected] = useState("");
  const [day, setDay] = useState("mon");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [availability, setAvailability] = useState(null);

  const checkAvailability = () => {
    if (!selected || !start || !end) return;

    fetch(`http://127.0.0.1:5000/api/availability/${encodeURIComponent(selected)}?start=${start}&end=${end}&day=${day}`)
      .then(res => res.json())
      .then(setAvailability)
      .catch(err => console.error(err));
  };

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>OSU Room Finder</h1>

      {/* Building dropdown */}
      <select value={selected} onChange={(e) => setSelected(e.target.value)}>
        <option value="">-- Select a Building --</option>
        {usableBuildings.map(b => (
          <option key={b} value={b}>{b}</option>
        ))}
      </select>

      {/* Day dropdown */}
      <select value={day} onChange={(e) => setDay(e.target.value)} style={{ marginLeft: "10px" }}>
        <option value="mon">Monday</option>
        <option value="tue">Tuesday</option>
        <option value="wed">Wednesday</option>
        <option value="thu">Thursday</option>
        <option value="fri">Friday</option>
        <option value="sat">Saturday</option>
        <option value="sun">Sunday</option>
      </select>

      {/* Time inputs */}
      <input type="time" value={start} onChange={(e) => setStart(e.target.value)} style={{ marginLeft: "10px" }} />
      <input type="time" value={end} onChange={(e) => setEnd(e.target.value)} style={{ marginLeft: "10px" }} />

      <button onClick={checkAvailability} style={{ marginLeft: "10px" }}>
        Check Availability
      </button>

      {availability && (
        <div style={{ marginTop: "20px" }}>
          <h2>{availability.building}</h2>
          <p>Day: {availability.day}, Time Range: {availability.requested_range}</p>
          <p><b>Free Rooms:</b> {availability.free_rooms.join(", ") || "None"}</p>
          <p><b>Occupied Rooms:</b> {availability.occupied_rooms.join(", ") || "None"}</p>
        </div>
      )}
    </div>
  );
}

export default App;

