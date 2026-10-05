import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import { BarChart3, TrendingUp, Clock, Key, Globe, RefreshCw } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const AnalyticsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await analyticsAPI.getDashboard();
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-sm font-mono text-slate-400">Loading Deep Threat Analytics...</p>
      </div>
    );
  }

  const { daily_trend, weekly_risk, top_suspicious_domains, hourly_distribution, common_keywords, category_distribution } = data;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-cyan-400" /> Deep Threat Analytics
        </h1>
        <p className="text-xs text-slate-400">Statistical metrics on email threat vectors, time distribution, and suspicious domain patterns.</p>
      </div>

      {/* 14-Day Daily Trend */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-cyan-400" /> 14-Day Historical Phishing Volume
        </h3>
        <p className="text-xs text-slate-400 mb-4">Volume of legitimate vs phishing email attacks detected per day</p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={daily_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="phishGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Area type="monotone" dataKey="phishing" name="Phishing Emails" stroke="#ef4444" fillOpacity={1} fill="url(#phishGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category-wise Attack Trends Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-purple-400" /> Category-wise Attack Trends
        </h3>
        <p className="text-xs text-slate-400 mb-4">Frequency and distribution of phishing threats across AI fraud categories</p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={(category_distribution || []).map(item => ({
                name: item.category.replace(/_/g, ' '),
                count: item.count
              }))}
              margin={{ top: 10, right: 10, left: -20, bottom: 35 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} angle={-20} textAnchor="end" interval={0} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
              <Bar dataKey="count" name="Threat Frequency" fill="#a855f7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
            <Clock className="w-4 h-4 text-teal-400" /> Hourly Attack Traffic (00:00 - 23:00)
          </h3>
          <p className="text-xs text-slate-400 mb-4">Frequency of email reception across 24 hours</p>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourly_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={10} tickFormatter={(h) => `${h}h`} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="count" name="Emails Received" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weekly Risk Probability */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <h3 className="text-sm font-bold text-slate-100 mb-1 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-amber-400" /> Weekly Risk Exposure Trend
          </h3>
          <p className="text-xs text-slate-400 mb-4">7-Day historical behavior risk probability score</p>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weekly_risk} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="risk_probability" name="Risk Score" stroke="#f59e0b" fillOpacity={1} fill="url(#riskGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
