import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Stock from "./pages/Stock";
import SystemStatus from "./pages/SystemStatus";
import Forecast from "./pages/Forecast";
import ModelComparison from "./pages/ModelComparison";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/stock" element={<Stock />} />
        <Route path="/system" element={<SystemStatus />} />
        <Route path="/forecast" element={<Forecast />} />
        <Route path="/compare" element={<ModelComparison />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
