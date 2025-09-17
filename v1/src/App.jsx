import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import Home from "./pages/Home";
import Memory from "./pages/Memory";
import Profile from "./pages/Profile";
import SOS from "./pages/SOS";
import Community from "./pages/Community";
import Recommendation from "./pages/Recommendation";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="memory" element={<Memory />} />
          <Route path="recommendation" element={<Recommendation />} />
          <Route path="sos" element={<SOS />} />
          <Route path="profile" element={<Profile />} />
          <Route path="community" element={<Community />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
