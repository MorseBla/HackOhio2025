import { useState } from "react";
import usableBuildings from "../../buildings/usable_buildings2.json";

function App() {
  const [selected, setSelected] = useState("");
  const [buildingData, setBuildingData] = useState(null);

  const handleSelect = (building) => {
    setSelected(building);
    if (!building) {
      setBuildingData(null);
      return;
    }

    console.log("Fetching data for:", building);

    fetch(`http://127.0.0.1:5000/api/buildings/${encodeURIComponent(building)}`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch building data");
        return res.json();
      })
      .then(data => {
        console.log("Data received:", data);
        setBuildingData(data);
      })
      .catch(err => console.error("Error fetching building:", err));
  };

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>OSU Room Finder</h1>

      <select value={selected} onChange={(e) => handleSelect(e.target.value)}>
        <option value="">-- Select a Building --</option>
        {usableBuildings.map(b => (
          <option key={b} value={b}>{b}</option>
        ))}
      </select>

      {buildingData && (
        <div style={{ marginTop: "20px" }}>
          <h2>{selected}</h2>
          <h3>Rooms: {buildingData.rooms.join(", ")}</h3>

          <h3>Classes</h3>
          <ul>
            {buildingData.classes.map((c, idx) => (
              <li key={idx}>
                Room {c.room} — {c.startTime} to {c.endTime} (
                  {Object.keys(c.days).filter(d => c.days[d]).join(", ")}
                )
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;

