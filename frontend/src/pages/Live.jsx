import React from 'react';
import { useViolations } from '../hooks/useViolations';
import { useStats } from '../hooks/useAnalytics';
import RiskBadge from '../components/RiskBadge';
import ViolationTag from '../components/ViolationTag';
import { formatDate } from '../utils/formatters';
import { Link } from 'react-router-dom';

export default function Live() {
  const { data: violationsData, isLoading: viLoading } = useViolations();
  const { data: statsData, isLoading: statsLoading } = useStats();

  if (viLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
          <span className="text-slate-400 font-mono text-sm">LOADING REALTIME SENSORS...</span>
        </div>
      </div>
    );
  }

  const violations = violationsData?.data?.violations || [];
  const stats = statsData?.data || {};

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-100 flex items-center gap-2">
            <span className="pulse-glow text-cyan-400 text-2xl">●</span> Live Telemetry Feed
          </h1>
          <p className="text-slate-400 text-sm mt-1">Real-time highway camera inference stream and active violator logging.</p>
        </div>
      </div>

      {/* KPI Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-6 border-slate-800">
          <div className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mt-2">
            {stats.today_violations || 0}
          </div>
        </div>
        <div className="card p-6 border-slate-800">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-mono">High Risk Events</div>
          <div className="text-4xl font-extrabold text-amber-500 mt-2">
            {stats.high_risk_count || 0}
          </div>
        </div>
        <div className="card p-6 border-slate-800">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-mono">Critical Queue</div>
          <div className="text-4xl font-extrabold text-red-500 mt-2">
            {stats.pending_count || 0}
          </div>
        </div>
        <div className="card p-6 border-slate-800">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-mono">Avg System Risk</div>
          <div className="text-4xl font-extrabold text-emerald-400 mt-2">
            {stats.avg_risk_score || 0}
          </div>
        </div>
      </div>

      {/* Violations List */}
      <div className="space-y-4">
        {violations.length === 0 ? (
          <div className="card p-12 text-center text-slate-500 border-dashed border-slate-800">
            <div className="text-3xl mb-2">📡</div>
            <div className="font-mono text-sm">NO TELEMETRY EVENTS DETECTED YET</div>
          </div>
        ) : (
          violations.map((violation) => (
            <div 
              key={violation.violation_id} 
              className="card p-5 hover:border-slate-700/80 transition-all group"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <Link 
                      to={`/evidence/${violation.violation_id}`}
                      className="font-mono font-bold text-lg text-slate-200 hover:text-cyan-400 hover:underline tracking-wider"
                    >
                      {violation.vehicle_plate || 'UNKNOWN'}
                    </Link>
                    <RiskBadge score={violation.risk_score} />
                  </div>
                  
                  <div className="flex gap-2 mb-3 flex-wrap">
                    {violation.violations?.map((type) => (
                      <ViolationTag key={type} type={type} />
                    ))}
                  </div>
                  
                  <div className="text-xs text-slate-400 font-mono">
                    {formatDate(violation.timestamp)} • Sensor ID: {violation.camera_id}
                  </div>
                </div>

                <div className="flex gap-2 self-end sm:self-center">
                  <Link 
                    to={`/evidence/${violation.violation_id}`}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:text-white rounded-lg font-medium text-xs transition duration-300"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
