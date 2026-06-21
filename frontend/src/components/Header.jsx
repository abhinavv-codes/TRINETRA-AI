import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Header({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const role = localStorage.getItem('role');

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Image Detect', path: '/detect' },
    { name: 'Video Detect', path: '/video-detection' },
    { name: 'Live Feed', path: '/live-feed' },
    { name: 'Analytics', path: '/analytics' },
  ];

  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <span className="text-white font-bold text-xl">👁️</span>
          </div>
          <div>
            <div className="font-extrabold text-xl tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-slate-100 to-slate-300">
              TRINETRA <span className="text-cyan-400 font-black">AI</span>
            </div>
            <div className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">Traffic Command Center</div>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? 'bg-cyan-950/40 text-cyan-400 border border-cyan-800/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end hidden sm:flex">
            <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 capitalize">
              {role?.toLowerCase() || 'officer'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 hover:text-white rounded-lg font-medium text-sm transition-all duration-300"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
