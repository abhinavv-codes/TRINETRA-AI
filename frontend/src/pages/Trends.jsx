import React from 'react';
import { useTrends } from '../hooks/useAnalytics';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Trends() {
  const { data: trendsData, isLoading } = useTrends();

  if (isLoading) return <div className="p-8">Loading trends...</div>;

  const data = trendsData?.data?.data || [];

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">📊 Violation Trends</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold mb-4">Violations by Hour</h2>
        
        {data.length === 0 ? (
          <div className="text-center text-gray-500 py-8">No trend data</div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#ef4444" name="Violations" />
              <Line type="monotone" dataKey="risk_avg" stroke="#f59e0b" name="Avg Risk" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
