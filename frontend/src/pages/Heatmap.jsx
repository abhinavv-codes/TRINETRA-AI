import React from 'react';
import { useHeatmap, useCorridors } from '../hooks/useAnalytics';

export default function Heatmap() {
  const { data: heatmapData, isLoading: hmLoading } = useHeatmap();
  const { data: corridorsData, isLoading: corrLoading } = useCorridors();

  if (hmLoading || corrLoading) return <div className="p-8">Loading heatmap...</div>;

  const corridors = corridorsData?.data || [];

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🗺️ Violation Hotspots</h1>

      <div className="grid grid-cols-3 gap-6">
        {/* Map */}
        <div className="col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-4 h-96">
          <div className="w-full h-full bg-gray-100 rounded flex items-center justify-center text-gray-500">
            Map visualization (Leaflet)
          </div>
        </div>

        {/* Top Corridors */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="font-bold mb-4">Top Corridors</h2>
          <div className="space-y-2">
            {corridors.length === 0 ? (
              <p className="text-gray-500 text-sm">No data</p>
            ) : (
              corridors.map((corridor, idx) => (
                <div key={idx} className="p-3 bg-gray-50 rounded">
                  <div className="font-medium text-sm">{corridor.corridor}</div>
                  <div className="text-xs text-gray-600">
                    {corridor.violation_count} violations
                  </div>
                  <div className="w-full bg-gray-200 rounded h-2 mt-1">
                    <div
                      className="bg-primary h-full rounded"
                      style={{ width: `${(corridor.risk_weighted / corridors[0]?.risk_weighted) * 100}%` }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
