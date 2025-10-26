import { useState, useEffect } from "react";

function App() {
  const [buildings, setBuildings] = useState([]);
  const [filteredBuildings, setFilteredBuildings] = useState([]);
  const [selectedBuildings, setSelectedBuildings] = useState([]);
  const [search, setSearch] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [day, setDay] = useState("mon");
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5001/api/buildings")
      .then((res) => res.json())
      .then((data) => {
        setBuildings(data.buildings || []);
        setFilteredBuildings(data.buildings || []);
      })
      .catch((err) => console.error("Error loading buildings:", err));
  }, []);

  const toggleBuilding = (b) => {
    if (selectedBuildings.includes(b)) {
      setSelectedBuildings(selectedBuildings.filter((x) => x !== b));
    } else {
      setSelectedBuildings([...selectedBuildings, b]);
    }
  };

  const handleSearch = (e) => {
    const value = e.target.value.toLowerCase();
    setSearch(value);
    setFilteredBuildings(
      buildings.filter((b) => b.toLowerCase().includes(value))
    );
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5001/api/meeting-spot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          buildings: selectedBuildings,
          start,
          end,
          day,
        }),
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Error submitting request:", err);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>OSU Meeting Spot Finder</h1>

      {/* 🔎 Search bar */}
      <input
        type="text"
        placeholder="Search buildings..."
        value={search}
        onChange={handleSearch}
        style={{ marginBottom: "10px", width: "300px", padding: "5px" }}
      />

      {/* ✅ Scrollable checkbox menu */}
      <div
        style={{
          border: "1px solid #ccc",
          height: "200px",
          width: "320px",
          overflowY: "scroll",
          padding: "10px",
          marginBottom: "15px",
        }}
      >
        {filteredBuildings.map((b, idx) => (
          <div key={idx}>
            <label>
              <input
                type="checkbox"
                checked={selectedBuildings.includes(b)}
                onChange={() => toggleBuilding(b)}
              />
              {b}
            </label>
          </div>
        ))}
      </div>

      {/* Time range */}
      <label>
        Start Time:
        <input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
      </label>
      <label>
        End Time:
        <input type="time" value={end} onChange={(e) => setEnd(e.target.value)} />
      </label>

      <br /><br />

      {/* Day of week */}
      <label>
        Day of Week:
        <select value={day} onChange={(e) => setDay(e.target.value)}>
          <option value="mon">Monday</option>
          <option value="tue">Tuesday</option>
          <option value="wed">Wednesday</option>
          <option value="thu">Thursday</option>
          <option value="fri">Friday</option>
        </select>
      </label>

      <br /><br />

      <button onClick={handleSubmit}>Find Meeting Spot</button>

      {/* Results */}
      {result && (
        <div style={{ border: "1px solid #ccc", marginTop: "20px", padding: "10px" }}>
          <h2>Results</h2>
          <p><strong>Closest Building:</strong> {result.closest_building}</p>
          <p><strong>Average Location:</strong> {result.average_location.join(", ")}</p>
          <p>
            <strong>Free Rooms:</strong>{" "}
            {Array.isArray(result.free_rooms) && result.free_rooms.length > 0
              ? result.free_rooms.join(", ")
              : "None"}
          </p>
          <p>
            <strong>Occupied Rooms:</strong>{" "}
            {Array.isArray(result.occupied_rooms) && result.occupied_rooms.length > 0
              ? result.occupied_rooms.join(", ")
              : "None"}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;

