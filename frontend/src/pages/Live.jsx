import React from 'react';
import { useViolations, useStats } from '../hooks/useViolations';
import RiskBadge from '../components/RiskBadge';
import ViolationTag from '../components/ViolationTag';
import { formatDate } from '../utils/formatters';

export default function Live() {
  const { data: violationsData, isLoading: viLoading } = useViolations();
  const { data: statsData, isLoading: statsLoading } = useStats();

  if (viLoading || statsLoading) return <div className="p-8">Loading violations...</div>;

  const violations = violationsData?.data?.violations || [];
  const stats = statsData?.data || {};

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🚨 Live Violations Feed</h1>

      {/* KPI Bar */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-600 text-sm">Today</div>
          <div className="text-3xl font-bold text-primary mt-1">{stats.total_violations || 0}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-600 text-sm">HIGH Risk</div>
          <div className="text-3xl font-bold text-warning mt-1">{stats.high_risk_count || 0}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-600 text-sm">CRITICAL</div>
          <div className="text-3xl font-bold text-danger mt-1">{stats.pending_count || 0}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-gray-600 text-sm">Avg Risk</div>
          <div className="text-3xl font-bold text-success mt-1">{stats.avg_risk_score || 0}</div>
        </div>
      </div>

      {/* Violations List */}
      <div className="space-y-4">
        {violations.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center text-gray-600">
            No violations detected yet
          </div>
        ) : (
          violations.map((violation) => (
            <div key={violation.violation_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-mono font-bold text-lg">{violation.vehicle_plate || 'UNKNOWN'}</span>
                    <RiskBadge score={violation.risk_score} />
                  </div>
                  
                  <div className="flex gap-2 mb-2 flex-wrap">
                    {violation.violations?.map((type) => (
                      <ViolationTag key={type} type={type} />
                    ))}
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    {formatDate(violation.timestamp)} • Camera {violation.camera_id}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-success text-white rounded text-sm hover:opacity-90">
                    ✓ Verify
                  </button>
                  <button className="px-3 py-1 bg-danger text-white rounded text-sm hover:opacity-90">
                    ✗ Reject
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
