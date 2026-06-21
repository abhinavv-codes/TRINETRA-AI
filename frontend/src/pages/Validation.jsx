import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ShieldCheck, HardDrive, RefreshCw } from 'lucide-react';

export default function Validation() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchValidationStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/api/v1/analytics/validation-stats');
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch validation stats from backend API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchValidationStats();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-100 flex items-center gap-2">
            <HardDrive className="w-8 h-8 text-cyan-400" /> Ground Truth Validation Viewer
          </h1>
          <p className="text-slate-400 text-sm mt-1">Telemetry audit of benchmark validation image counts across standard classes.</p>
        </div>
        <button 
          onClick={fetchValidationStats} 
          disabled={loading}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Reload Stats
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-20 card">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
            <span className="text-slate-400 font-mono text-xs">SCANNING DIRECTORIES...</span>
          </div>
        </div>
      ) : error ? (
        <div className="card p-6 border-red-900/30 text-center space-y-3">
          <div className="text-red-400 font-bold uppercase tracking-wider font-mono">Telemetry Scan Interrupted</div>
          <p className="text-xs text-slate-400">{error}</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Stat */}
          <div className="card p-6 bg-gradient-to-r from-slate-900 to-slate-950 border border-slate-800 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">Validation Database</span>
              <span className="text-3xl font-black text-slate-100 font-mono">
                {data.total_images} <span className="text-xs text-cyan-400 font-normal">Files Cataloged</span>
              </span>
            </div>
            <div className="p-3 bg-cyan-950/30 text-cyan-400 rounded-xl border border-cyan-900/20">
              <ShieldCheck className="w-8 h-8" />
            </div>
          </div>

          {/* Breakdown cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(data.categories || {}).map(([key, count]) => {
              // Custom class mapping display name
              const displayNames = {
                helmet: "Helmet Clean",
                no_helmet: "No Helmet",
                triple: "Triple Riding",
                numberplate: "License Plate",
                normal: "Normal (No Violation)"
              };
              
              return (
                <div key={key} className="card p-4 flex flex-col justify-between border-slate-850 hover:border-slate-800 transition">
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wide truncate">
                    {displayNames[key] || key}
                  </span>
                  <div className="mt-4 flex items-baseline justify-between">
                    <span className="text-2xl font-bold font-mono text-slate-100">{count}</span>
                    <span className="text-[9px] text-slate-500 font-mono">images</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="card p-4 border-slate-850 bg-slate-950/20 font-mono text-[10px] text-slate-500 flex items-center justify-between">
            <span>Scan Location: data/validation/</span>
            <span>Target Benchmark Count: 91 images</span>
          </div>
        </div>
      )}
    </div>
  );
}
