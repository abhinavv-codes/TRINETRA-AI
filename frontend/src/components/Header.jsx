import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Header({ onLogout }) {
  const navigate = useNavigate();
  const role = localStorage.getItem('role');

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">🎯</span>
          </div>
          <div>
            <div className="font-bold text-lg">TRINETRA AI</div>
            <div className="text-xs text-gray-500">Traffic Enforcement</div>
          </div>
        </Link>

        <nav className="flex items-center gap-6">
          <Link to="/" className="text-gray-600 hover:text-primary font-medium">Live</Link>
          <Link to="/heatmap" className="text-gray-600 hover:text-primary font-medium">Heatmap</Link>
          <Link to="/trends" className="text-gray-600 hover:text-primary font-medium">Trends</Link>
          <Link to="/risk-queue" className="text-gray-600 hover:text-primary font-medium">Queue</Link>
        </nav>

        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{role} Role</span>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
