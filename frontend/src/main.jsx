import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Stock from "./pages/Stock";
import SystemStatus from "./pages/SystemStatus";
import Forecast from "./pages/Forecast";
import ModelComparison from "./pages/ModelComparison";
import Analytics from "./pages/Analytics";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/stock" element={<Stock />} />
        <Route path="/system" element={<SystemStatus />} />
        <Route path="/forecast" element={<Forecast />} />
        <Route path="/compare" element={<ModelComparison />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
