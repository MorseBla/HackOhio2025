import { useState } from "react";

function App() {
  const [building, setBuilding] = useState("Dreese Laboratories");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchTaken = async () => {
    setLoading(true);
    setResults(null);
    try {
      const url = `http://127.0.0.1:8000/taken?building=${encodeURIComponent(
        building
      )}&term=1258`; // change term if needed
      const res = await fetch(url);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      setResults({ error: "Failed to fetch" });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2>OSU Room Usage Finder</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label>Building: </label>
        <input
          value={building}
          onChange={(e) => setBuilding(e.target.value)}
          style={{ marginRight: "1rem" }}
        />
        <button onClick={fetchTaken}>Search</button>
      </div>

      {loading && <p>Loading...</p>}
      {results?.error && <p style={{ color: "red" }}>{results.error}</p>}

      {results && results.taken_slots && results.taken_slots.length > 0 && (
        <div>
          <h3>
            Results for {results.building} — Term {results.term}
          </h3>
          <table
            border="1"
            cellPadding="5"
            style={{ borderCollapse: "collapse", width: "100%" }}
          >
            <thead style={{ backgroundColor: "#f0f0f0" }}>
              <tr>
                <th>Room</th>
                <th>Course</th>
                <th>Subject</th>
                <th>Catalog</th>
                <th>Section</th>
                <th>Time</th>
                <th>Days</th>
                <th>Instructor(s)</th>
                <th>Capacity</th>
                <th>Dates</th>
              </tr>
            </thead>
            <tbody>
              {results.taken_slots.map((slot, idx) => (
                <tr key={idx}>
                  <td>{slot.room}</td>
                  <td>{slot.courseTitle}</td>
                  <td>{slot.subject}</td>
                  <td>{slot.catalogNumber}</td>
                  <td>{slot.section}</td>
                  <td>
                    {slot.startTime} – {slot.endTime}
                  </td>
                  <td>
                    {Object.entries(slot.days)
                      .filter(([_, val]) => val)
                      .map(([day]) => day[0].toUpperCase())
                      .join(", ")}
                  </td>
                  <td>{slot.instructors.join(", ")}</td>
                  <td>{slot.capacity}</td>
                  <td>
                    {slot.startDate} → {slot.endDate}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {results && results.taken_slots && results.taken_slots.length === 0 && (
        <p>No scheduled classes found for that building/term.</p>
      )}
    </div>
  );
}

export default App;

