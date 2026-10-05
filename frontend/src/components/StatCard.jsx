import React from 'react';

const StatCard = ({ title, value, icon: Icon, change, changeType = 'neutral', color = 'cyan' }) => {
  const colorStyles = {
    cyan: 'from-cyan-500/10 to-slate-900/50 border-cyan-500/20 text-cyan-400',
    teal: 'from-teal-500/10 to-slate-900/50 border-teal-500/20 text-teal-400',
    red: 'from-red-500/10 to-slate-900/50 border-red-500/20 text-red-400',
    amber: 'from-amber-500/10 to-slate-900/50 border-amber-500/20 text-amber-400',
    emerald: 'from-emerald-500/10 to-slate-900/50 border-emerald-500/20 text-emerald-400',
  };

  return (
    <div className={`relative overflow-hidden rounded-xl border bg-gradient-to-br p-5 shadow-lg backdrop-blur-md transition-all hover:border-slate-700 ${colorStyles[color] || colorStyles.cyan}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="mt-2 text-3xl font-extrabold text-slate-100">{value}</h3>
          {change && (
            <p className={`mt-1.5 text-xs font-semibold flex items-center gap-1 ${
              changeType === 'increase-danger' ? 'text-red-400' :
              changeType === 'increase-good' ? 'text-emerald-400' : 'text-slate-400'
            }`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-slate-800/80 border border-slate-700/50 text-2xl shadow-inner`}>
          {Icon && <Icon className="w-6 h-6" />}
        </div>
      </div>
      <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-current opacity-5 rounded-full blur-xl pointer-events-none" />
    </div>
  );
};

export default StatCard;
