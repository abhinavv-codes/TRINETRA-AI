import React from 'react';
import { useViolations } from '../hooks/useViolations';
import RiskBadge from '../components/RiskBadge';
import { formatDate } from '../utils/formatters';

export default function RiskQueue() {
  const { data: violationsData, isLoading } = useViolations();

  if (isLoading) return <div className="p-8">Loading queue...</div>;

  const violations = violationsData?.data?.violations || [];
  const sorted = [...violations].sort((a, b) => b.risk_score - a.risk_score);

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">⚡ Officer Worklist (Risk Sorted)</h1>

      <div className="space-y-2">
        {sorted.map((violation, idx) => (
          <div
            key={violation.violation_id}
            className="bg-white p-4 rounded-lg shadow-sm border-l-4 hover:shadow-md transition"
            style={{
              borderLeftColor: violation.risk_score >= 80 ? '#dc2626' : violation.risk_score >= 60 ? '#ef4444' : '#f59e0b'
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1">
                <div className="text-lg font-bold text-gray-400">#{idx + 1}</div>
                <div>
                  <div className="font-mono font-bold">{violation.vehicle_plate}</div>
                  <div className="text-sm text-gray-500">{formatDate(violation.timestamp)}</div>
                </div>
              </div>
              <RiskBadge score={violation.risk_score} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
