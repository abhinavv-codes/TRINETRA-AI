import React from 'react';
import { useParams } from 'react-router-dom';
import { useViolation } from '../hooks/useViolations';
import RiskBadge from '../components/RiskBadge';
import ViolationTag from '../components/ViolationTag';

export default function Evidence() {
  const { id } = useParams();
  const { data: violationData, isLoading } = useViolation(id);

  if (isLoading) return <div className="p-8">Loading evidence...</div>;

  const violation = violationData?.data;

  if (!violation) return <div className="p-8">Violation not found</div>;

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">📷 Evidence</h1>

      <div className="grid grid-cols-2 gap-6">
        {/* Image */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gray-200 h-96 flex items-center justify-center">
            <span className="text-gray-500">Image: {violation.evidence_uri}</span>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-bold mb-4">Details</h2>
            <div className="space-y-3">
              <div>
                <span className="text-gray-600 text-sm">Plate:</span>
                <div className="font-mono font-bold">{violation.vehicle_plate}</div>
              </div>
              <div>
                <span className="text-gray-600 text-sm">Violations:</span>
                <div className="flex gap-2 mt-1 flex-wrap">
                  {violation.violations?.map((v) => (
                    <ViolationTag key={v} type={v} />
                  ))}
                </div>
              </div>
              <div>
                <span className="text-gray-600 text-sm">Risk Score:</span>
                <div className="mt-1">
                  <RiskBadge score={violation.risk_score} />
                </div>
              </div>
            </div>
          </div>

          {/* Report */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-bold mb-4">Report</h2>
            <p className="text-gray-700">{violation.report || 'No report'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
