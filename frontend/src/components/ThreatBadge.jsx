import React from 'react';

const ThreatBadge = ({ level, size = 'md' }) => {
  const normalized = (level || 'LOW').toUpperCase();

  const styles = {
    LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10',
    MEDIUM: 'bg-amber-500/10 text-amber-400 border-amber-500/30 shadow-amber-500/10',
    HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/30 shadow-orange-500/10',
    CRITICAL: 'bg-red-500/15 text-red-400 border-red-500/40 shadow-red-500/20 animate-pulse',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs font-semibold',
    md: 'px-3 py-1 text-sm font-semibold',
    lg: 'px-4 py-1.5 text-base font-bold',
  };

  const currentStyle = styles[normalized] || styles.LOW;
  const currentSize = sizes[size] || sizes.md;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border shadow-sm ${currentStyle} ${currentSize}`}>
      <span className={`w-2 h-2 rounded-full ${
        normalized === 'CRITICAL' ? 'bg-red-500' :
        normalized === 'HIGH' ? 'bg-orange-500' :
        normalized === 'MEDIUM' ? 'bg-amber-500' : 'bg-emerald-500'
      }`} />
      {normalized} RISK
    </span>
  );
};

export default ThreatBadge;
