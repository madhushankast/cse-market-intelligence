import React, { useEffect, useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
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
  Menu,
  X,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const location = useLocation();

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

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
    `flex items-center gap-2 px-3.5 py-2 md:py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
      isActive
        ? 'bg-subsurface text-brand border border-borderline shadow-sm'
        : 'text-muted hover:text-gray-200 hover:bg-subsurface/50'
    }`;

  return (
    <header className="border-b border-borderline bg-surface/95 backdrop-blur sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-2">
        {/* Brand identity */}
        <Link to="/" className="flex items-center gap-2.5 sm:gap-3 group min-w-0">
          <div className="w-8 h-8 sm:w-9 sm:h-9 shrink-0 rounded-lg bg-subsurface border border-borderline flex items-center justify-center">
            <BarChart2 className="w-4 h-4 sm:w-5 sm:h-5 text-brand" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="font-bold text-sm sm:text-base tracking-tight text-gray-100 group-hover:text-brand transition-colors truncate">
                CSE Market Intelligence
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-subsurface text-muted border border-borderline shrink-0">
                v2.0
              </span>
            </div>
            <p className="text-[11px] text-muted hidden sm:block font-sans truncate">
              Colombo Stock Exchange • Multi-Quantile LightGBM Terminal
            </p>
          </div>
        </Link>

        {/* Desktop Global Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 lg:gap-2">
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono text-muted hover:text-gray-200 hover:bg-subsurface/50 border border-transparent hover:border-borderline transition-all"
            title={`FastAPI Swagger Documentation (${API_BASE_URL}/docs)`}
          >
            <span>API Docs</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </nav>

        {/* Right Status Indicator & Mobile Menu Toggle */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs font-mono shrink-0">
          {health ? (
            <div
              className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
              title={`Connected to live backend at ${API_BASE_URL} (${health.models_count} trained models online)`}
            >
              <Wifi className="w-3.5 h-3.5 text-emerald-400 animate-pulse shrink-0" />
              <span className="hidden sm:inline">Live API ({health.models_count || 26} Models)</span>
              <span className="sm:hidden text-[10px]">Live</span>
            </div>
          ) : (
            <div
              className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400"
              title={`Backend offline at ${API_BASE_URL}. Showing cached models & preview data.`}
            >
              <WifiOff className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span className="hidden sm:inline">Offline / Demo Mode</span>
              <span className="sm:hidden text-[10px]">Demo</span>
            </div>
          )}

          <div className="hidden xl:flex items-center gap-1 text-[11px] text-muted">
            <Zap className="w-3 h-3 text-brand" />
            <span>{health ? `${health.available_equities_count || 26} Equities` : '26 Equities'}</span>
          </div>

          {/* Mobile Hamburger Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-2 rounded-lg bg-subsurface border border-borderline text-gray-200 hover:text-brand focus:outline-none transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-borderline bg-surface px-4 pt-3 pb-4 space-y-2 shadow-2xl">
          <div className="grid grid-cols-1 gap-1.5">
            <NavLink to="/" end className={navLinkClass}>
              <BookOpen className="w-4 h-4" />
              <span>Platform Overview</span>
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
              className="flex items-center justify-between px-3.5 py-2 rounded-lg text-xs font-mono text-muted hover:text-gray-200 hover:bg-subsurface/50 border border-transparent hover:border-borderline transition-all"
            >
              <span className="flex items-center gap-2">
                <ExternalLink className="w-4 h-4" />
                <span>FastAPI Swagger Docs</span>
              </span>
              <span className="text-[10px] text-brand">Open</span>
            </a>
          </div>

          <div className="pt-2 border-t border-borderline/60 flex items-center justify-between text-[11px] font-mono text-muted px-1">
            <span className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-brand" />
              <span>{health ? `${health.available_equities_count || 26} CSE Equities Active` : '26 CSE Equities'}</span>
            </span>
            <span>Multi-Quantile LightGBM</span>
          </div>
        </div>
      )}
    </header>
  );
};
