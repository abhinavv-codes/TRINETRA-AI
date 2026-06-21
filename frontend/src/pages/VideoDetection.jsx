import React, { useState } from 'react';
import { violationsAPI } from '../api/violations';
import RiskBadge from '../components/RiskBadge';
import ViolationTag from '../components/ViolationTag';
import { formatDate } from '../utils/formatters';
import { Upload, Play, FileVideo, Shield, Link as LinkIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function VideoDetection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const handleFileChange = (e) => {
    if (loading) return;
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a video file first");
      return;
    }

    setLoading(true);
    setActiveStep(0);
    const toastId = toast.loading("Processing traffic recording...");

    // Start timer interval to cycle through active steps
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < 3) return prev + 1;
        return prev;
      });
    }, 9000);

    try {
      const response = await violationsAPI.detectVideo(selectedFile);
      setResult(response.data);
      toast.success("Video processing complete!", { id: toastId });
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Video processing failed", { id: toastId });
    } finally {
      setLoading(false);
      clearInterval(interval);
    }
  };

  const stepsList = [
    "Running Vehicle Detection...",
    "Running Helmet Detection...",
    "Running OCR...",
    "Generating Evidence..."
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6 relative">
      
      {/* Full-Screen Processing Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl max-w-md w-full text-center space-y-6 shadow-2xl">
            {/* Animated Spinner */}
            <div className="relative w-16 h-16 mx-auto">
              <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-transparent border-t-cyan-500 rounded-full animate-spin"></div>
            </div>
            
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-slate-100 font-mono tracking-wider">COMPUTING CCTV VIDEO ANALYTICS</h3>
              <p className="text-[11px] text-cyan-400 font-mono animate-pulse">Processing may take 1–2 minutes on CPU.</p>
            </div>

            {/* Steps List */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-950 text-left font-mono text-xs space-y-3">
              {stepsList.map((step, idx) => {
                const isDone = activeStep > idx;
                const isActive = activeStep === idx;
                return (
                  <div key={idx} className="flex items-center justify-between">
                    <span className={isDone ? "text-slate-500 line-through" : isActive ? "text-cyan-400 font-bold" : "text-slate-400"}>
                      {step}
                    </span>
                    <span className="font-bold">
                      {isDone ? (
                        <span className="text-emerald-500">✓ DONE</span>
                      ) : isActive ? (
                        <span className="text-cyan-400 animate-pulse">● ACTIVE</span>
                      ) : (
                        <span className="text-slate-600">AWAITING</span>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <div>
        <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2">
          <Play className="w-8 h-8 text-cyan-400 fill-cyan-400/20" /> Video Enforcement Hub
        </h1>
        <p className="text-slate-400 text-sm mt-1">Submit DVR or camera footage recordings to run batched frame analysis.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Pane: Upload Video File */}
        <div className="lg:col-span-5 space-y-4">
          <div className="card p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">Select Footage</h2>
            
            {!selectedFile ? (
              <label className={`flex flex-col items-center justify-center h-72 rounded-xl border-2 border-dashed bg-slate-950/40 transition-all duration-300 ${
                loading 
                  ? 'border-slate-800 cursor-not-allowed opacity-50 pointer-events-none' 
                  : 'border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900/20 cursor-pointer group'
              }`}>
                <FileVideo className="w-12 h-12 text-slate-500 group-hover:text-cyan-400 transition mb-3" />
                <span className="text-slate-300 font-medium">Select video recording</span>
                <span className="text-xs text-slate-500 mt-1 font-mono">MP4, AVI, MOV up to 50MB</span>
                <input 
                  type="file" 
                  accept="video/*" 
                  disabled={loading}
                  onChange={handleFileChange} 
                  className="hidden" 
                />
              </label>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center gap-3">
                  <div className="p-3 bg-cyan-950/30 text-cyan-400 rounded-lg">
                    <FileVideo className="w-6 h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-slate-200 truncate">{selectedFile.name}</div>
                    <div className="text-xs font-mono text-slate-500 mt-0.5">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </div>
                  </div>
                </div>

                {!result && (
                  <div className="flex gap-2">
                    <button 
                      onClick={handleUpload}
                      disabled={loading}
                      className="btn-primary flex-1"
                    >
                      Process Footage
                    </button>
                    <button 
                      onClick={() => setSelectedFile(null)}
                      disabled={loading}
                      className="btn-secondary"
                    >
                      Clear
                    </button>
                  </div>
                )}

                {result && (
                  <button 
                    onClick={() => { setSelectedFile(null); setResult(null); }}
                    disabled={loading}
                    className="btn-secondary w-full"
                  >
                    Select Another Video
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: Surviellance Results */}
        <div className="lg:col-span-7 space-y-4">
          <div className="card p-6 h-full flex flex-col">
            <h2 className="text-lg font-bold text-slate-200 mb-4">Surveillance Logging</h2>

            {!result ? (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 py-16 border border-slate-800 border-dashed rounded-lg bg-slate-950/10">
                <Shield className="w-12 h-12 mb-3 opacity-30" />
                <span className="font-mono text-xs">AWAITING CCTV TELEMETRY PASS</span>
              </div>
            ) : (
              <div className="space-y-6">
                
                {/* Stats Cards */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-850">
                    <span className="text-slate-500 text-[10px] uppercase font-mono tracking-wider block">Frames Processed</span>
                    <span className="text-2xl font-bold text-slate-200 mt-1 block">
                      {result.frames_processed}
                    </span>
                  </div>
                  <div className="p-4 bg-slate-950/60 rounded-xl border-cyan-950/30 border">
                    <span className="text-cyan-400 text-[10px] uppercase font-mono tracking-wider block">Violations Flagged</span>
                    <span className="text-2xl font-bold text-cyan-400 mt-1 block">
                      {result.violations_detected}
                    </span>
                  </div>
                </div>

                {/* Table list */}
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-slate-300 font-mono uppercase tracking-wider">Flagged Incidents</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider">
                          <th className="py-2.5 font-medium">Plate</th>
                          <th className="py-2.5 font-medium">Vehicle</th>
                          <th className="py-2.5 font-medium">Violation</th>
                          <th className="py-2.5 font-medium text-right">Risk</th>
                          <th className="py-2.5 font-medium text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-850/60 text-slate-300">
                        {result.results?.filter(v => v.violation !== 'NONE').map((item, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/30 transition-colors">
                            <td className="py-3 font-semibold text-slate-200 tracking-wider">
                              {item.plate_number || 'UNKNOWN'}
                            </td>
                            <td className="py-3 capitalize text-slate-400">
                              {item.vehicle_type}
                            </td>
                            <td className="py-3">
                              <ViolationTag type={item.violation} size="small" />
                            </td>
                            <td className="py-3 text-right">
                              <span className={`font-bold ${item.risk_score >= 80 ? 'text-red-500' : item.risk_score >= 60 ? 'text-orange-500' : 'text-amber-500'}`}>
                                {item.risk_score}
                              </span>
                            </td>
                            <td className="py-3 text-right">
                              {item.violation_id ? (
                                <Link 
                                  to={`/evidence/${item.violation_id}`}
                                  className="text-cyan-400 hover:text-cyan-300 hover:underline inline-flex items-center gap-1"
                                >
                                  View <LinkIcon className="w-3.5 h-3.5" />
                                </Link>
                              ) : (
                                <span className="text-slate-600">-</span>
                              )}
                            </td>
                          </tr>
                        ))}
                        {result.results?.filter(v => v.violation !== 'NONE').length === 0 && (
                          <tr>
                            <td colSpan="5" className="py-8 text-center text-slate-500">
                              No violations detected in processed frames.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
