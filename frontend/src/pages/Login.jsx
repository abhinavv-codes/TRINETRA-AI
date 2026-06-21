import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/violations';
import toast from 'react-hot-toast';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('demo');
  const [password, setPassword] = useState('demo123');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authAPI.login(username, password);
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('role', response.data.role);
      toast.success(`Welcome, ${username}!`);
      onLogin();
      navigate('/');
    } catch (error) {
      toast.error('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050b18] text-slate-150 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Glow Elements */}
      <div className="absolute right-0 top-0 w-80 h-80 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="absolute left-0 bottom-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>

      <div className="card p-8 max-w-md w-full border-slate-800/80 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-500/20">
            <span className="text-white text-2xl">👁️</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">TRINETRA <span className="text-cyan-400 font-black">AI</span></h1>
          <p className="text-[10px] text-slate-400 font-mono uppercase tracking-widest mt-2">Traffic Violation Detection</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-[10px] font-mono text-slate-400 uppercase mb-2 tracking-wider">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-650 focus:ring-2 focus:ring-cyan-500 focus:border-transparent font-mono text-sm"
              placeholder="demo"
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono text-slate-400 uppercase mb-2 tracking-wider">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-650 focus:ring-2 focus:ring-cyan-500 focus:border-transparent font-mono text-sm"
              placeholder="••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-2.5 mt-2 text-sm font-bold uppercase tracking-wider"
          >
            {loading ? 'Authenticating...' : 'Establish Connection'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-800/60 text-center font-mono text-xs">
          <p className="text-slate-500 mb-3">System Node Access Credentials</p>
          <div className="space-y-1.5 text-slate-400">
            <p>Officer: <span className="text-cyan-400">demo</span> / <span className="text-slate-500">demo123</span></p>
            <p>Administrator: <span className="text-cyan-400">admin</span> / <span className="text-slate-500">admin123</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
