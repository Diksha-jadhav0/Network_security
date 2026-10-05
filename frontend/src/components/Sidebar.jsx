import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  History,
  BarChart3,
  TrendingUp,
  Settings,
  ShieldAlert,
  Info
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload & Analyze', icon: Upload },
    { path: '/history', label: 'Email History', icon: History },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/prediction', label: 'Future Risk', icon: TrendingUp },
    { path: '/about', label: 'About Project', icon: Info },
    { path: '/settings', label: 'Settings & Profile', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between hidden md:flex min-h-screen">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="font-extrabold text-lg tracking-wider text-slate-100 flex items-center gap-1">
              Phish<span className="text-cyan-400">Shield</span>
            </h1>
            <p className="text-[10px] uppercase font-mono tracking-widest text-slate-400">AI Threat Intelligence</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 font-semibold shadow-sm shadow-cyan-500/5'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Network Security Footer */}
      <div className="p-4 border-t border-slate-800 m-4 rounded-xl bg-slate-950/60 border text-xs text-slate-400 space-y-1">
        <div className="flex items-center justify-between text-[11px] font-mono text-cyan-400">
          <span>STATUS: ONLINE</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
        </div>
        <p className="text-[11px]">TF-IDF + Random Forest Classifier v1.0</p>
        <p className="text-[10px] text-slate-400">Final-Year Engineering Project</p>
      </div>
    </aside>
  );
};

export default Sidebar;
