import React, { useState, useEffect } from "react";


function ManualPage() {
  const [buildings, setBuildings] = useState([]);
  const [selected, setSelected] = useState([]);
  const [results, setResults] = useState(null);
    //const BACKEND = "http://127.0.0.1:5001"; 
  const BACKEND = import.meta.env.VITE_API_BASE;

  useEffect(() => {
    fetch(`${BACKEND}/api/buildings`)
    .then(res => res.json())
    .then(data => {
      console.log("Buildings API response:", data); // 👀 debug
      // If it's already an array, use it directly
      if (Array.isArray(data)) {
        setBuildings(data);
      } else if (data.buildings) {
        // if backend returns { "buildings": [...] }
        setBuildings(data.buildings);
      } else {
        setBuildings([]); // fallback
      }
    })
    .catch(err => {
      console.error("Error loading buildings:", err);
      setBuildings([]);
    });


  }, []);

  const toggleBuilding = (b) => {
    setSelected(prev =>
      prev.includes(b) ? prev.filter(x => x !== b) : [...prev, b]
    );
  };

  const calculate = () => {
    fetch(`${BACKEND}/api/manual_average`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ buildings: selected })
    })
      .then(r => r.json())
      .then(setResults);
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Manual Mode</h1>
      <div className="h-64 overflow-y-scroll border p-2 mb-4">
        {buildings.map((b, i) => (
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
      <button onClick={calculate} className="px-4 py-2 bg-blue-600 text-white rounded">
        Find Closest
      </button>

      {results && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold">Top 3 Closest</h2>
          {results.top_buildings.map((tb, i) => (
            <div key={i} className="border p-2 my-2 rounded">
              <p><strong>{tb.building}</strong></p>
              <p>Free Rooms: {tb.free_rooms.join(", ")}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ManualPage;

