import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings, User, Database, Shield, CheckCircle2 } from 'lucide-react';

const SettingsPage = () => {
  const { user } = useAuth();

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <Settings className="w-6 h-6 text-cyan-400" /> Settings & System Environment
        </h1>
        <p className="text-xs text-slate-400">Manage user configuration, active model parameters, and database connection profiles.</p>
      </div>

      {/* Profile Info */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <User className="w-4 h-4 text-cyan-400" /> Active Security Analyst Profile
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-slate-400 block font-mono text-[10px] uppercase">Analyst Name</span>
            <span className="font-bold text-slate-200">{user?.name || 'Administrator'}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-slate-400 block font-mono text-[10px] uppercase">Email Address</span>
            <span className="font-bold text-slate-200">{user?.email || 'admin@example.com'}</span>
          </div>
        </div>
      </div>

      {/* Database & Environment Info */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <Database className="w-4 h-4 text-teal-400" /> Database & Storage Configuration
        </h2>
        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono">
            <span className="text-slate-400">Database Engine:</span>
            <span className="text-emerald-400 font-bold">SQLite 3 (OR SQLAlchemy MySQL Ready)</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono">
            <span className="text-slate-400">Backend Server:</span>
            <span className="text-cyan-400 font-bold">FastAPI 0.116+ (Uvicorn Async ASGI)</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono">
            <span className="text-slate-400">ML Model Status:</span>
            <span className="text-emerald-400 font-bold">Loaded (`phishing_model.pkl` & `risk_model.pkl`)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
