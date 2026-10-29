import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { TerminalPage } from './pages/TerminalPage';
import { BenchmarksPage } from './pages/BenchmarksPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-canvas text-gray-200 flex flex-col font-sans selection:bg-brand/20 selection:text-brand">
        {/* Persistent Global Header */}
        <Navbar />

        {/* Dynamic Route Viewport */}
        <main className="flex-1 flex flex-col">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/terminal" element={<TerminalPage />} />
            <Route path="/benchmarks" element={<BenchmarksPage />} />
            {/* Fallback redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Persistent Terminal Footer */}
        <footer className="border-t border-borderline py-5 px-6 bg-surface/50 text-xs font-mono text-muted flex flex-col sm:flex-row items-center justify-between gap-3 mt-12">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-brand" />
            <span className="text-gray-300 font-semibold">
              CSE Market Intelligence Platform
            </span>
            <span>&bull;</span>
            <span>Colombo Stock Exchange</span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span>Purged Walk-Forward Cross-Validation (30d Embargo)</span>
            <span>&bull;</span>
            <span>Multi-Quantile LightGBM</span>
            <span>&bull;</span>
            <span>Dual-Layer Explainability (TreeSHAP)</span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
