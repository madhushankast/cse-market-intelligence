import React, { useEffect, useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { checkHealth, API_BASE_URL, type HealthStatus } from '../api';
import {
  BarChart2,
  TrendingUp,
  Award,
  BookOpen,
  ExternalLink,
  Zap,
  Wifi,
  WifiOff,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
    const interval = setInterval(() => {
      checkHealth()
        .then(setHealth)
        .catch(() => setHealth(null));
    }, 20000);
    return () => clearInterval(interval);
  }, []);

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
      isActive
        ? 'bg-subsurface text-brand border border-borderline shadow-sm'
        : 'text-muted hover:text-gray-200 hover:bg-subsurface/50'
    }`;

  return (
    <header className="border-b border-borderline bg-surface/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand identity */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand to-sky-400 flex items-center justify-center font-bold text-canvas shadow-lg shadow-brand/20 group-hover:scale-105 transition-transform">
            <BarChart2 className="w-5 h-5 text-gray-950" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-gray-100 group-hover:text-brand transition-colors">
                CSE Market Intelligence
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-subsurface text-muted border border-borderline">
                v2.0
              </span>
            </div>
            <p className="text-[11px] text-muted hidden sm:block font-sans">
              Colombo Stock Exchange • Multi-Quantile LightGBM Terminal
            </p>
          </div>
        </Link>

        {/* Global Navigation Links */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <NavLink to="/" end className={navLinkClass}>
            <BookOpen className="w-4 h-4" />
            <span>Overview</span>
          </NavLink>

          <NavLink to="/terminal" className={navLinkClass}>
            <TrendingUp className="w-4 h-4" />
            <span>Trading Terminal</span>
          </NavLink>

          <NavLink to="/benchmarks" className={navLinkClass}>
            <Award className="w-4 h-4" />
            <span>Model Benchmarks</span>
          </NavLink>

          <a
            href={`${API_BASE_URL}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono text-muted hover:text-gray-200 hover:bg-subsurface/50 border border-transparent hover:border-borderline transition-all"
            title={`FastAPI Swagger Documentation (${API_BASE_URL}/docs)`}
          >
            <span>API Docs</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </nav>

        {/* Right Status Indicator */}
        <div className="hidden lg:flex items-center gap-3 text-xs font-mono">
          {health ? (
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
              title={`Connected to live backend at ${API_BASE_URL} (${health.models_count} trained models online)`}
            >
              <Wifi className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span>Live API ({health.models_count || 26} Models)</span>
            </div>
          ) : (
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400"
              title={`Backend offline at ${API_BASE_URL}. Showing cached models & preview data.`}
            >
              <WifiOff className="w-3.5 h-3.5 text-amber-400" />
              <span>Offline / Demo Mode</span>
            </div>
          )}

          <div className="flex items-center gap-1 text-[11px] text-muted">
            <Zap className="w-3 h-3 text-brand" />
            <span>{health ? `${health.available_equities_count || 26} Equities` : '26 Equities'}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
