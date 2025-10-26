import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import ManualPage from "./ManualPage";
import GroupSelectionPage from "./GroupSelectionPage";
import GroupPage from "./GroupPage";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <BrowserRouter>
       <nav className=" navbar bg-black bg-opacity-25 navbar-dark">
      <div className="container-fluid d-flex justify-content-between">
        <h1 className="navbar-brand" href="#">
          OSU Group Meeting Finder
        </h1>
        <div className="d-flex flex-row-reverse">
            <Link to="/" className=" text-decoration-underline mx-3 nav-link d-inline text-white"  >
                Group Mode
          </Link>
          <Link to="/manual" className=" text-decoration-underline nav-link d-inline text-white" >
              Manual Mode
          </Link>
        </div>
      </div>
    </nav>  
      <Routes className="">
        <Route path="/" element={<GroupSelectionPage />} />
        <Route path="/group" element={<GroupPage />} />
        <Route path="/manual" element={<ManualPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

