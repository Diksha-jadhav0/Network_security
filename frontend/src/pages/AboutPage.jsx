import React from 'react';
import { ShieldAlert, BookOpen, CheckCircle2, Lock, Cpu, Server, FileText } from 'lucide-react';

const AboutPage = () => {
  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-cyan-400" /> Academic Project Specification
        </h1>
        <p className="text-xs text-slate-400">Network Security Final-Year Capstone Architecture & Implementation Overview.</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
        <div>
          <h2 className="text-lg font-bold text-slate-100 text-cyan-400">Problem Statement</h2>
          <p className="text-xs text-slate-300 leading-relaxed mt-2">
            Phishing attacks account for over 80% of reported cybersecurity breaches worldwide. Conventional email gateways evaluate incoming messages in isolation, failing to consider historical user behavioral patterns. This project addresses the gap by integrating NLP machine learning text classification with historical behavioral risk scoring to predict future exposure.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" /> Phishing Classifier Pipeline
            </h3>
            <p className="text-xs text-slate-400">
              Combines TF-IDF vectorization with a 200-estimator Random Forest Classifier trained on email text & engineered features (URL count, raw IP URL, urgent keywords, domain mismatch, uppercase ratio).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Server className="w-4 h-4 text-teal-400" /> Future Risk Prediction Engine
            </h3>
            <p className="text-xs text-slate-400">
              Logistic Regression model trained on 7 user behavioral features (phishing history over 24h & 7d, unknown sender ratio, average URLs, off-hours ratio, suspicious domain frequency).
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Lock className="w-4 h-4 text-amber-400" /> Header Authentication Awareness (SPF / DKIM / DMARC)
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Parses raw email MIME headers (`From`, `Reply-To`, `Received`, `Authentication-Results`) to detect domain spoofing, mismatched reply addresses, missing SPF records, or missing DKIM cryptographic signatures.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
