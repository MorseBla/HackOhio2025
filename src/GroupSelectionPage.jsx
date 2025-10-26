import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function GroupSelectionPage() {
  const [group, setGroup] = useState("");
  const [user, setUser] = useState("");
  const [error, setError] = useState("");
    //const BACKEND = import.meta.env.VITE_API_BASE;
    const BACKEND = "http://127.0.0.1:5001"; 
  const navigate = useNavigate();

  const handleGroupAction = async (action) => {
    if (!group || !user) {
      setError("Both group and name required");
      return;
    }
    try {
      const res = await fetch(`${BACKEND}/api/${action}_group`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ group, user }),
      });
      if (!res.ok) {
        throw new Error("Failed to join/create group");
      }
      setError("");
      navigate("/group", { state: { group, user } }); // go to GroupPage
    } catch (err) {
      setError("Error: " + err.message);
    }
  };

  return (
      <div  className="mt-3">
      <h1 className="text-center text-decoration-underline fw-bold text-xl font-bold mb-4">Join or Create a Group</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div className="d-flex justify-content-center">    
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
          </div>
          
          <div  className="my-4 d-flex justify-content-center">
        <button onClick={() => handleGroupAction("create")} style={{ marginRight: "10px" }}>
          Create Group
        </button>
        <button onClick={() => handleGroupAction("join")}>Join Group</button>
      </div>
    </div>
  );
}

export default GroupSelectionPage;

