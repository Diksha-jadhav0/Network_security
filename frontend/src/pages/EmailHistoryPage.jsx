import React, { useEffect, useState } from 'react';
import { emailAPI } from '../services/api';
import ThreatBadge from '../components/ThreatBadge';
import { History, Search, Trash2, Eye, X, Filter, Mail } from 'lucide-react';

const EmailHistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [selectedEmail, setSelectedEmail] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await emailAPI.getHistory();
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this email record?")) return;
    try {
      await emailAPI.deleteEmail(id);
      setHistory(history.filter(item => item.id !== id));
      if (selectedEmail?.id === id) setSelectedEmail(null);
    } catch (err) {
      console.error("Failed to delete email:", err);
    }
  };

  const filteredHistory = history.filter(item => {
    const matchesSearch = item.subject.toLowerCase().includes(search.toLowerCase()) ||
                          item.sender.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = filterRisk === 'ALL' || item.risk_level === filterRisk;
    const matchesCategory = filterCategory === 'ALL' || item.phishing_category === filterCategory;
    return matchesSearch && matchesRisk && matchesCategory;
  });

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <History className="w-6 h-6 text-cyan-400" /> Historical Email Security Logs
        </h1>
        <p className="text-xs text-slate-400">Searchable log of all previously analyzed emails and machine learning risk evaluations.</p>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-4 rounded-xl">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by sender or subject..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">LOW Risk</option>
            <option value="MEDIUM">MEDIUM Risk</option>
            <option value="HIGH">HIGH Risk</option>
            <option value="CRITICAL">CRITICAL Risk</option>
          </select>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Fraud Categories</option>
            <option value="BANKING_FRAUD">Banking Fraud</option>
            <option value="TRANSACTION_FRAUD">Transaction Fraud</option>
            <option value="LOTTERY_SCAM">Lottery Scam</option>
            <option value="JOB_FRAUD">Job Fraud</option>
            <option value="ENTERTAINMENT_SCAM">Entertainment Scam</option>
            <option value="CRYPTO_INVESTMENT_SCAM">Crypto Scam</option>
            <option value="ACCOUNT_VERIFICATION_SCAM">Account Verification Scam</option>
            <option value="LEGITIMATE">Legitimate Email</option>
            <option value="UNKNOWN">Unknown</option>
          </select>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        {loading ? (
          <p className="p-8 text-center text-xs text-slate-400">Loading history logs...</p>
        ) : filteredHistory.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Sender</th>
                  <th className="px-4 py-3">Subject</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Phishing Score</th>
                  <th className="px-4 py-3">Risk Level</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredHistory.map((email) => (
                  <tr
                    key={email.id}
                    onClick={() => setSelectedEmail(email)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-slate-400">
                      {new Date(email.received_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-200 font-medium">
                      {email.sender}
                    </td>
                    <td className="px-4 py-3 text-slate-200 font-semibold max-w-xs truncate">
                      {email.subject}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">
                      <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-semibold">
                        {(email.phishing_category || 'N/A').replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono font-bold">
                      <span className={email.is_phishing ? 'text-red-400' : 'text-emerald-400'}>
                        {(email.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <ThreatBadge level={email.risk_level} size="sm" />
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={(e) => { e.stopPropagation(); setSelectedEmail(email); }}
                          className="p-1.5 rounded bg-slate-800 text-slate-300 hover:text-cyan-400"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(email.id, e)}
                          className="p-1.5 rounded bg-slate-800 text-slate-300 hover:text-red-400"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-12 text-center text-xs text-slate-400">No matching email records found.</p>
        )}
      </div>

      {/* Detail Modal */}
      {selectedEmail && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6 space-y-4 shadow-2xl relative">
            <button
              onClick={() => setSelectedEmail(null)}
              className="absolute top-4 right-4 p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-3">
              <ThreatBadge level={selectedEmail.risk_level} size="lg" />
              {selectedEmail.phishing_category && (
                <span className="px-2.5 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono text-xs font-bold">
                  {selectedEmail.phishing_category.replace(/_/g, ' ')}
                </span>
              )}
              <span className="text-xs font-mono text-slate-400">ID #{selectedEmail.id}</span>
            </div>

            <div>
              <h2 className="text-lg font-bold text-slate-100">{selectedEmail.subject}</h2>
              <p className="text-xs font-mono text-cyan-400 mt-0.5">From: {selectedEmail.sender}</p>
              <p className="text-[11px] text-slate-400 font-mono">
                Received: {new Date(selectedEmail.received_at).toLocaleString()}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
              {selectedEmail.body}
            </div>

            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Phishing Score</span>
                <span className="font-bold text-slate-200 font-mono">{(selectedEmail.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Fraud Category Confidence</span>
                <span className="font-bold text-purple-300 font-mono">
                  {selectedEmail.category_confidence !== undefined && selectedEmail.category_confidence !== null
                    ? `${(selectedEmail.category_confidence * 100).toFixed(1)}%`
                    : 'N/A'}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">URLs Extracted</span>
                <span className="font-bold text-slate-200 font-mono">{selectedEmail.url_count}</span>
              </div>
            </div>

            {selectedEmail.suspicious_keywords?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-400 mb-1.5">Detected Phishing Keywords:</p>
                <div className="flex flex-wrap gap-1.5">
                  {selectedEmail.suspicious_keywords.map((kw, i) => (
                    <span key={i} className="px-2.5 py-1 rounded bg-red-500/10 border border-red-500/20 text-red-400 font-mono text-xs">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default EmailHistoryPage;
