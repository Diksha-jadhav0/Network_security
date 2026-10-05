import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, ShieldCheck, Bell } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Navbar = ({ title = "Dashboard" }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-slate-900/80 border-b border-slate-800 backdrop-blur-md sticky top-0 z-30 px-6 flex items-center justify-between">
      <div>
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          {title}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate('/upload')}
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-semibold hover:bg-cyan-500/20 transition-all"
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Quick Analyze</span>
        </button>

        {user && (
          <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 flex items-center justify-center font-bold text-xs">
                {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-slate-200 leading-tight">{user.name}</p>
                <p className="text-[10px] text-slate-400 leading-tight">{user.email}</p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              title="Logout"
              className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-all"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
