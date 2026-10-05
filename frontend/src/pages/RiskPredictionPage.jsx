import React, { useEffect, useState } from 'react';
import { predictionAPI } from '../services/api';
import ThreatBadge from '../components/ThreatBadge';
import { TrendingUp, ShieldAlert, Cpu, CheckCircle2, AlertCircle, RefreshCw, Activity } from 'lucide-react';

const RiskPredictionPage = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const res = await predictionAPI.getFutureRisk();
      setPrediction(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-sm font-mono text-slate-400">Running Behavioral Logistic Regression Predictor...</p>
      </div>
    );
  }

  if (!prediction) {
    return <p className="p-8 text-center text-xs text-red-400">Failed to load risk prediction data.</p>;
  }

  const { future_risk_probability, predicted_risk, features_used, recommendation } = prediction;
  const riskPercent = (future_risk_probability * 100).toFixed(0);

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-cyan-400" /> Future 24-Hour Phishing Exposure Risk
        </h1>
        <p className="text-xs text-slate-400">Predictive behavioral modeling using Logistic Regression on historical user email patterns.</p>
      </div>

      {/* Main Risk Gauge Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">
          <div className="space-y-3 text-center md:text-left max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
              <Cpu className="w-3.5 h-3.5" /> Logistic Regression Model Inference
            </div>
            <h2 className="text-3xl font-extrabold text-slate-100">
              Predicted 24h Risk Score: <span className="text-cyan-400">{riskPercent}%</span>
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/80 p-4 rounded-xl border border-slate-800 font-mono">
              {recommendation}
            </p>
          </div>

          {/* Risk Score Circle Widget */}
          <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-950 border border-slate-800 min-w-[200px]">
            <div className="relative flex items-center justify-center">
              <span className="text-4xl font-extrabold font-mono text-slate-100">{riskPercent}%</span>
            </div>
            <p className="text-[11px] font-mono uppercase text-slate-400 mt-2">Predicted Risk Score</p>
            <div className="mt-3">
              <ThreatBadge level={predicted_risk} size="md" />
            </div>
          </div>
        </div>
      </div>

      {/* Feature Vector Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" /> Behavioral Feature Vector (Model Inputs)
        </h3>
        <p className="text-xs text-slate-400">The 7 quantitative historical behavioral statistics extracted from user email history:</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <p className="text-[10px] uppercase font-mono text-slate-400">Phishing Emails (Last 24h)</p>
            <p className="text-xl font-mono font-bold text-slate-200 mt-1">{features_used.phishing_last_24h}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <p className="text-[10px] uppercase font-mono text-slate-400">Phishing Emails (Last 7d)</p>
            <p className="text-xl font-mono font-bold text-slate-200 mt-1">{features_used.phishing_last_7d}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <p className="text-[10px] uppercase font-mono text-slate-400">Unknown Sender Ratio</p>
            <p className="text-xl font-mono font-bold text-slate-200 mt-1">{(features_used.unknown_sender_ratio * 100).toFixed(0)}%</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <p className="text-[10px] uppercase font-mono text-slate-400">Average URLs Per Email</p>
            <p className="text-xl font-mono font-bold text-slate-200 mt-1">{features_used.avg_url_count}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <p className="text-[10px] uppercase font-mono text-slate-400">Urgent Keywords Freq.</p>
            <p className="text-xl font-mono font-bold text-slate-200 mt-1">{features_used.urgent_keyword_frequency}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <p className="text-[10px] uppercase font-mono text-slate-400">Off-Hours Email Ratio</p>
            <p className="text-xl font-mono font-bold text-slate-200 mt-1">{(features_used.off_hours_email_ratio * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskPredictionPage;
