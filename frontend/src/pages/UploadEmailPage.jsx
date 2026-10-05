import React, { useState } from 'react';
import { emailAPI } from '../services/api';
import ThreatBadge from '../components/ThreatBadge';
import {
  Upload, FileText, Send, ShieldAlert, CheckCircle2,
  AlertTriangle, Link as LinkIcon, Shield, Globe, Lock, Cpu
} from 'lucide-react';

const UploadEmailPage = () => {
  const [activeTab, setActiveTab] = useState('text'); // 'text' or 'file'
  const [sender, setSender] = useState('security-update@paypa1-alert.com');
  const [subject, setSubject] = useState('Verify your PayPal account immediately');
  const [body, setBody] = useState('Dear customer, We detected unauthorized login attempts on your PayPal account. Click http://paypa1-security.com/login-verify to restore full access. Failure to verify within 24 hours will result in permanent account termination.');
  
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await emailAPI.analyze(sender, subject, body);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Email analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a .txt or .eml file');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await emailAPI.upload(formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'File processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <Upload className="w-6 h-6 text-cyan-400" /> Email Threat Analysis Portal
        </h1>
        <p className="text-xs text-slate-400">Analyze email content or upload raw MIME (.eml) files for instant machine learning threat detection.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-4">
        <button
          onClick={() => { setActiveTab('text'); setError(''); }}
          className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'text'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" /> Manual Text Entry
        </button>
        <button
          onClick={() => { setActiveTab('file'); setError(''); }}
          className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'file'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Upload className="w-4 h-4" /> File Upload (.eml / .txt)
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form Column */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          {activeTab === 'text' ? (
            <form onSubmit={handleTextSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1.5">Sender Email Address</label>
                <input
                  type="text"
                  required
                  value={sender}
                  onChange={(e) => setSender(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500/50"
                  placeholder="sender@domain.com"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1.5">Subject Line</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500/50"
                  placeholder="Urgent account verification needed"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1.5">Email Body Content</label>
                <textarea
                  required
                  rows={7}
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500/50"
                  placeholder="Paste email body text here..."
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-slate-950 font-extrabold text-sm tracking-wide shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
              >
                {loading ? 'Analyzing Threat Vector...' : (
                  <>
                    <Cpu className="w-4 h-4" /> Run Phishing Classification
                  </>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleFileUpload} className="space-y-6">
              <div className="border-2 border-dashed border-slate-700 hover:border-cyan-500/50 rounded-xl p-8 text-center bg-slate-950/50 transition-all">
                <Upload className="w-10 h-10 text-cyan-400 mx-auto mb-3" />
                <p className="text-sm font-semibold text-slate-200">Select or Drag Email File</p>
                <p className="text-xs text-slate-400 mt-1">Supports raw email files (.eml) or text exports (.txt)</p>
                <input
                  type="file"
                  accept=".eml,.txt"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="mt-4 text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-500/10 file:text-cyan-400 hover:file:bg-cyan-500/20 cursor-pointer"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !file}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-slate-950 font-extrabold text-sm tracking-wide shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
              >
                {loading ? 'Parsing EML Headers...' : 'Analyze Uploaded File'}
              </button>
            </form>
          )}
        </div>

        {/* Threat Analysis Output Column */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between">
          {result ? (
            <div className="space-y-5">
              {/* Header Status Banner */}
              <div className={`p-4 rounded-xl border flex items-center justify-between ${
                result.is_phishing
                  ? 'bg-red-500/10 border-red-500/30 text-red-400'
                  : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              }`}>
                <div className="flex items-center gap-3">
                  {result.is_phishing ? (
                    <ShieldAlert className="w-8 h-8 text-red-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0" />
                  )}
                  <div>
                    <h3 className="font-extrabold text-base">
                      {result.is_phishing ? 'PHISHING THREAT DETECTED' : 'LEGITIMATE EMAIL'}
                    </h3>
                    <p className="text-xs opacity-90">
                      Model Confidence: {(result.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                <ThreatBadge level={result.risk_level} size="lg" />
              </div>

              {/* Security Metrics Breakdown */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                  <p className="text-[10px] uppercase font-mono text-slate-400">URLs Found</p>
                  <p className="text-lg font-bold text-slate-200 flex items-center gap-1.5 mt-0.5">
                    <LinkIcon className="w-4 h-4 text-cyan-400" /> {result.url_count} URLs
                  </p>
                </div>
                <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                  <p className="text-[10px] uppercase font-mono text-slate-400">Sender Domain</p>
                  <p className="text-xs font-mono font-bold text-slate-200 truncate mt-1">
                    {result.sender_domain_analysis?.domain || 'N/A'}
                  </p>
                </div>
              </div>

              {/* DistilBERT Phishing Category Classification */}
              {result.phishing_category && (
                <div className="p-4 rounded-xl bg-slate-950 border border-purple-900/40 space-y-1.5 shadow-inner">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                      <Cpu className="w-4 h-4 text-purple-400" /> Phishing Category Classification
                    </p>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                      DistilBERT AI Model
                    </span>
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-sm font-extrabold tracking-wide text-cyan-300">
                      {result.phishing_category.replace(/_/g, ' ')}
                    </span>
                    {result.category_confidence !== undefined && result.category_confidence !== null && (
                      <span className="text-xs font-mono font-bold text-purple-300">
                        {(result.category_confidence * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                </div>
              )}


              {/* SPF / DKIM / DMARC Header Authentication Awareness */}
              {result.header_analysis && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <p className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <Shield className="w-4 h-4 text-cyan-400" /> Header Security Authentication (SPF / DKIM / DMARC)
                  </p>
                  <div className="flex gap-4 text-xs font-mono">
                    <span className={result.header_analysis.has_spf ? 'text-emerald-400' : 'text-red-400'}>
                      SPF: {result.header_analysis.has_spf ? 'PASS' : 'MISSING'}
                    </span>
                    <span className={result.header_analysis.has_dkim ? 'text-emerald-400' : 'text-red-400'}>
                      DKIM: {result.header_analysis.has_dkim ? 'PASS' : 'MISSING'}
                    </span>
                    <span className={result.header_analysis.has_dmarc ? 'text-emerald-400' : 'text-amber-400'}>
                      DMARC: {result.header_analysis.has_dmarc ? 'PASS' : 'NONE'}
                    </span>
                  </div>
                  {result.header_analysis.auth_warning && (
                    <p className="text-[11px] text-amber-400">{result.header_analysis.auth_warning}</p>
                  )}
                </div>
              )}

              {/* Suspicious Keywords */}
              <div>
                <p className="text-xs font-semibold text-slate-400 mb-2">Urgent / Phishing Keywords Detected:</p>
                <div className="flex flex-wrap gap-1.5">
                  {result.suspicious_keywords && result.suspicious_keywords.length > 0 ? (
                    result.suspicious_keywords.map((kw, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-mono">
                        {kw}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">None detected</span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-slate-800 rounded-xl">
              <Shield className="w-12 h-12 text-slate-700 mb-3" />
              <h4 className="text-sm font-bold text-slate-400">Awaiting Email Analysis Input</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-xs">
                Fill in the email fields on the left or upload a raw file to run real-time Random Forest classification.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadEmailPage;
