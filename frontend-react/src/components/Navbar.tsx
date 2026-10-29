import React, { useEffect, useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { checkHealth, type HealthStatus } from '../api';
import {
  BarChart2,
  TrendingUp,
  Award,
  BookOpen,
  ExternalLink,
  Zap,
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
    }, 30000);
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
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono text-muted hover:text-gray-200 hover:bg-subsurface/50 border border-transparent hover:border-borderline transition-all"
            title="FastAPI Interactive Swagger Documentation"
          >
            <span>API Docs</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </nav>

        {/* Right Status Indicator */}
        <div className="hidden lg:flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>{health ? 'API Connected' : 'Online'}</span>
          </div>

          <div className="flex items-center gap-1 text-[11px] text-muted">
            <Zap className="w-3 h-3 text-brand" />
            <span>26 Equities</span>
          </div>
        </div>
      </div>
    </header>
  );
};
