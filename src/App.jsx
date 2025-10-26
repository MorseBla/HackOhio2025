import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import GroupPage from "./GroupPage";
import ManualPage from "./ManualPage";

function App() {
  return (
    <Router>
      <nav className="p-4 bg-gray-800 text-white flex gap-4">
        <Link to="/">Group Mode</Link>
        <Link to="/manual">Manual Mode</Link>
      </nav>
      <Routes>
        <Route path="/" element={<GroupPage />} />
        <Route path="/manual" element={<ManualPage />} />
      </Routes>
    </Router>
  );
}

export default App;

