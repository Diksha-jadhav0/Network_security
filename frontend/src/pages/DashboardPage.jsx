import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import StatCard from '../components/StatCard';
import ThreatBadge from '../components/ThreatBadge';
import {
  Mail, ShieldAlert, CheckCircle2, TrendingUp, AlertTriangle,
  Globe, Key, Clock, ShieldCheck, RefreshCw
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await analyticsAPI.getDashboard();
      setData(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-sm font-mono text-slate-400">Loading Security Intelligence Dashboard...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
        <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
        <p>{error || 'No data available'}</p>
        <button onClick={fetchDashboard} className="mt-4 px-4 py-2 bg-slate-800 rounded-lg text-xs text-slate-200">Retry</button>
      </div>
    );
  }

  const {
    stats,
    daily_trend,
    weekly_risk,
    top_suspicious_domains,
    phishing_vs_legit,
    hourly_distribution,
    recent_suspicious,
    common_keywords,
    category_distribution
  } = data;

  const pieData = [
    { name: 'Phishing', value: phishing_vs_legit.phishing, color: '#ef4444' },
    { name: 'Legitimate', value: phishing_vs_legit.legitimate, color: '#10b981' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
            Threat Intelligence Overview
          </h1>
          <p className="text-xs text-slate-400">Real-time ML Phishing Detection & Behavioral Risk Analytics</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboard}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-cyan-400 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <ThreatBadge level={stats.current_risk_level} size="lg" />
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Emails Analyzed"
          value={stats.total_emails}
          icon={Mail}
          change="+12% from last week"
          changeType="increase-good"
          color="cyan"
        />
        <StatCard
          title="Phishing Threats Detected"
          value={stats.phishing_count}
          icon={ShieldAlert}
          change={`${((stats.phishing_count / (stats.total_emails || 1)) * 100).toFixed(1)}% threat ratio`}
          changeType="increase-danger"
          color="red"
        />
        <StatCard
          title="Legitimate Emails"
          value={stats.legitimate_count}
          icon={CheckCircle2}
          change="Clean communications"
          changeType="increase-good"
          color="emerald"
        />
        <StatCard
          title="Future 24h Risk Score"
          value={`${(stats.current_risk_score * 100).toFixed(0)}%`}
          icon={TrendingUp}
          change={`Risk Level: ${stats.current_risk_level}`}
          changeType={stats.current_risk_score > 0.5 ? 'increase-danger' : 'increase-good'}
          color={stats.current_risk_score > 0.5 ? 'amber' : 'teal'}
        />
      </div>

      {/* Main Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Phishing Trend Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" /> Daily Email Analysis Trend
              </h3>
              <p className="text-xs text-slate-400">14-Day volume of legitimate vs phishing emails</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={daily_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPhish" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorLegit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="phishing" name="Phishing" stroke="#ef4444" fillOpacity={1} fill="url(#colorPhish)" />
                <Area type="monotone" dataKey="legitimate" name="Legitimate" stroke="#10b981" fillOpacity={1} fill="url(#colorLegit)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Phishing vs Legitimate Distribution Pie */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-teal-400" /> Phishing vs Legitimate Distribution
            </h3>
            <p className="text-xs text-slate-400">Total email classification proportions</p>
          </div>
          <div className="h-52 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
            Total Analyzed: <span className="font-bold text-slate-200">{stats.total_emails} Emails</span>
          </div>
        </div>
      </div>

      {/* Fraud Category Distribution Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-purple-400" /> Fraud Category Distribution
        </h3>
        <p className="text-xs text-slate-400 mb-4">DistilBERT AI Multi-class Fraud Categorization Breakdown</p>
        <div className="h-60">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={(category_distribution || []).map(item => ({
                name: item.category.replace(/_/g, ' '),
                count: item.count
              }))}
              margin={{ top: 10, right: 10, left: -20, bottom: 40 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} angle={-25} textAnchor="end" interval={0} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
              <Bar dataKey="count" name="Fraud Incidents" fill="#c084fc" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>


      {/* Main Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Attack Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" /> Hourly Attack Distribution (00:00 - 23:00)
          </h3>
          <p className="text-xs text-slate-400 mb-4">Peak hours of incoming suspicious email traffic</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourly_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={10} tickFormatter={(h) => `${h}h`} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="count" name="Emails" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Suspicious Domains */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
            <Globe className="w-4 h-4 text-red-400" /> Top Suspicious Domains Detected
          </h3>
          <p className="text-xs text-slate-400 mb-4">Highest volume offending sender domains</p>
          <div className="space-y-3">
            {top_suspicious_domains.length > 0 ? (
              top_suspicious_domains.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <div className="flex items-center gap-2.5">
                    <span className="w-6 h-6 rounded-md bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-mono font-bold flex items-center justify-center">
                      #{idx + 1}
                    </span>
                    <span className="text-xs font-mono font-semibold text-slate-200">{item.domain}</span>
                  </div>
                  <span className="px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 text-xs font-bold font-mono">
                    {item.count} threats
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 py-8 text-center">No suspicious domains recorded.</p>
            )}
          </div>
        </div>
      </div>

      {/* Widgets Row 3 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Suspicious Emails */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" /> Recent High-Risk Suspicious Emails
          </h3>
          <div className="space-y-2.5">
            {recent_suspicious.length > 0 ? (
              recent_suspicious.map((email) => (
                <div key={email.id} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between gap-4">
                  <div className="overflow-hidden">
                    <p className="text-xs font-bold text-slate-200 truncate">{email.subject}</p>
                    <p className="text-[11px] font-mono text-slate-400 truncate">From: {email.sender}</p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs font-mono font-bold text-red-400">{(email.confidence * 100).toFixed(0)}% Conf</span>
                    <ThreatBadge level={email.risk_level} size="sm" />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 py-6 text-center">No recent phishing emails detected.</p>
            )}
          </div>
        </div>

        {/* Most Common Phishing Keywords */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 mb-3 flex items-center gap-2">
            <Key className="w-4 h-4 text-cyan-400" /> Frequently Detected Keywords
          </h3>
          <div className="flex flex-wrap gap-2">
            {common_keywords.map((kw, idx) => (
              <span key={idx} className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 flex items-center gap-1.5">
                <span>{kw.keyword}</span>
                <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-[10px] text-cyan-400 font-bold">{kw.count}</span>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
