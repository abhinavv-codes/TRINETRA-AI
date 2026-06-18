import React, { useState } from 'react';
import { useViolations } from '../hooks/useViolations';

export default function Search() {
  const [plate, setPlate] = useState('');
  const [type, setType] = useState('');
  const { data: violationsData, isLoading } = useViolations();

  const violations = violationsData?.data?.violations || [];
  const filtered = violations.filter((v) => {
    if (plate && !v.vehicle_plate.includes(plate)) return false;
    if (type && !v.violations.includes(type)) return false;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🔍 Search Violations</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            placeholder="Filter by plate..."
            value={plate}
            onChange={(e) => setPlate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">All violation types</option>
            <option value="NO_HELMET">No Helmet</option>
            <option value="TRIPLE_RIDING">Triple Riding</option>
            <option value="RED_LIGHT">Red Light</option>
          </select>
        </div>

        <div className="text-sm text-gray-600">
          Found {filtered.length} violation{filtered.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="space-y-2">
        {filtered.map((v) => (
          <div key={v.violation_id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <span className="font-mono">{v.vehicle_plate}</span> - {v.violations.join(', ')}
          </div>
        ))}
      </div>
    </div>
  );
}
