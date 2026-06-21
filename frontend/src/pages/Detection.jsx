import React, { useState } from 'react';
import { violationsAPI } from '../api/violations';
import RiskBadge from '../components/RiskBadge';
import ViolationTag from '../components/ViolationTag';
import { formatDate } from '../utils/formatters';
import { Upload, Camera, CheckCircle, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Detection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const handleFileChange = (e) => {
    if (loading) return;
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null); // Clear previous results
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select an image first");
      return;
    }

    setLoading(true);
    setActiveStep(0);
    const toastId = toast.loading("Initializing pipeline...");

    // Cycle through steps every 7-8 seconds to show dynamic user feedback
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < 3) return prev + 1;
        return prev;
      });
    }, 7500);

    try {
      const response = await violationsAPI.detect(selectedFile);
      setResult(response.data);
      toast.success("Analysis complete!", { id: toastId });
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Detection failed", { id: toastId });
    } finally {
      setLoading(false);
      clearInterval(interval);
    }
  };

  const getBackendUrl = (uri) => {
    if (!uri) return '';
    return `http://localhost:8000/${uri}`;
  };

  const stepsList = [
    { title: "Stage 1/4", desc: "Vehicle Detection" },
    { title: "Stage 2/4", desc: "Helmet Detection" },
    { title: "Stage 3/4", desc: "License Plate OCR" },
    { title: "Stage 4/4", desc: "Evidence Generation" }
  ];

  const getPlateDisplay = (plateText, ocrConf, status) => {
    const confidencePercent = Math.round(ocrConf * 100);
    let barColorClass = "bg-red-500";
    let textColorClass = "text-red-400";
    
    if (ocrConf >= 0.85) {
      barColorClass = "bg-emerald-500";
      textColorClass = "text-emerald-400";
    } else if (ocrConf >= 0.50) {
      barColorClass = "bg-amber-500";
      textColorClass = "text-amber-400";
    }

    let displayPlate = "";
    if (status === "VERIFIED") {
      displayPlate = `Plate: ${plateText || ''}`;
    } else if (status === "LOW_CONFIDENCE") {
      const text = plateText || '';
      displayPlate = `Plate: ${text.length > 2 ? text.slice(0, -2) + '**' : text + '**'}`;
    } else {
      displayPlate = "Plate Not Readable";
    }

    return {
      displayPlate,
      confidencePercent,
      barColorClass,
      textColorClass
    };
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 relative">
      
      {/* Full-Screen Processing Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl max-w-md w-full text-center space-y-6 shadow-2xl">
            {/* Animated Spinner & Progress ring */}
            <div className="relative w-16 h-16 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-transparent border-t-cyan-500 rounded-full animate-spin"></div>
            </div>
            
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-100 font-mono tracking-wider flex items-center justify-center gap-1.5">
                🔍 AI Analysis In Progress
              </h3>
              <p className="text-xs text-slate-400 font-mono">Running neural inference engines...</p>
            </div>

            {/* Stages List */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-950 text-left font-mono text-xs space-y-4">
              {stepsList.map((step, idx) => {
                const isDone = activeStep > idx;
                const isActive = activeStep === idx;
                return (
                  <div key={idx} className="flex items-center justify-between border-b border-slate-900/40 pb-2 last:border-b-0 last:pb-0">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-slate-500 font-bold uppercase">{step.title}</span>
                      <span className={isDone ? "text-slate-500 line-through" : isActive ? "text-cyan-400 font-bold" : "text-slate-400"}>
                        {step.desc}
                      </span>
                    </div>
                    <span className="font-bold text-[10px] uppercase">
                      {isDone ? (
                        <span className="text-emerald-500">✓ Completed</span>
                      ) : isActive ? (
                        <span className="text-cyan-400 animate-pulse">● Processing</span>
                      ) : (
                        <span className="text-slate-650 text-slate-600">Awaiting</span>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Progress Bar inside overlay */}
            <div className="w-full bg-slate-950/60 rounded-full h-1.5 overflow-hidden border border-slate-800">
              <div 
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-1000" 
                style={{ width: `${(activeStep + 1) * 25}%` }}
              ></div>
            </div>

            <p className="text-[10px] text-slate-500 font-mono border-t border-slate-850 pt-4">
              Processing may take 30–120 seconds on CPU. Please do not refresh.
            </p>
          </div>
        </div>
      )}

      <div>
        <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2">
          <Camera className="w-8 h-8 text-cyan-400" /> Image Enforcement Portal
        </h1>
        <p className="text-slate-400 text-sm mt-1">Upload a snapshot to run the multi-stage YOLO + PaddleOCR pipeline.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Upload & Image Viewer */}
        <div className="lg:col-span-7 space-y-4">
          <div className="card p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">Traffic Image Feed</h2>
            
            {!previewUrl && !result ? (
              <label className={`flex flex-col items-center justify-center h-80 rounded-xl border-2 border-dashed bg-slate-950/40 transition-all duration-300 ${
                loading 
                  ? 'border-slate-850 cursor-not-allowed opacity-50 pointer-events-none' 
                  : 'border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900/20 cursor-pointer group'
              }`}>
                <Upload className="w-12 h-12 text-slate-500 group-hover:text-cyan-400 transition mb-3" />
                <span className="text-slate-300 font-medium">Select traffic image or drag & drop</span>
                <span className="text-xs text-slate-500 mt-1 font-mono">PNG, JPG up to 10MB</span>
                <input 
                  type="file" 
                  accept="image/*" 
                  disabled={loading}
                  onChange={handleFileChange} 
                  className="hidden" 
                />
              </label>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-xl border border-slate-800 bg-slate-950 overflow-hidden min-h-[300px] flex items-center justify-center">
                  <img 
                    src={result ? getBackendUrl(result.evidence_image) : previewUrl} 
                    alt="Surveillance snapshot" 
                    className="max-h-[450px] w-full object-contain"
                  />
                </div>

                {!result && (
                  <div className="flex gap-2">
                    <button 
                      onClick={handleUpload}
                      disabled={loading}
                      className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      🚀 Process Image
                    </button>
                    <button 
                      onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                      disabled={loading}
                      className="btn-secondary"
                    >
                      Clear
                    </button>
                  </div>
                )}

                {result && (
                  <button 
                    onClick={() => { setSelectedFile(null); setPreviewUrl(null); setResult(null); }}
                    disabled={loading}
                    className="btn-secondary w-full"
                  >
                    Upload Another Image
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Analysis panel */}
        <div className="lg:col-span-5 space-y-4">
          <div className="card p-6 h-full flex flex-col">
            <h2 className="text-lg font-bold text-slate-200 mb-4">Pipeline Analysis</h2>

            {!result ? (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 py-12 border border-slate-800 border-dashed rounded-lg bg-slate-950/10">
                <FileText className="w-12 h-12 mb-3 opacity-30" />
                <span className="font-mono text-xs">AWAITING IMAGE DATA</span>
              </div>
            ) : (
              <div className="space-y-6">
                
                {/* Event Summary Card */}
                <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-850 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400 text-xs font-mono">Camera Node</span>
                    <span className="text-slate-200 font-bold font-mono">{result.camera_id}</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400 text-xs font-mono">Telemetry Timestamp</span>
                    <span className="text-slate-300 text-xs font-mono">{formatDate(result.timestamp)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-cyan-400 text-xs font-mono font-semibold">Surveillance Risk Index</span>
                    <RiskBadge score={result.risk_score} />
                  </div>
                </div>

                {/* Detections List */}
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-slate-300 font-mono uppercase tracking-wider">Detected Entities</h3>
                  <div className="space-y-3.5 max-h-[380px] overflow-y-auto pr-1">
                    {result.results?.map((vehicle, idx) => {
                      const hasViolation = vehicle.violation && vehicle.violation !== 'NONE';
                      const { displayPlate, confidencePercent, barColorClass, textColorClass } = getPlateDisplay(
                        vehicle.plate_text,
                        vehicle.ocr_confidence,
                        vehicle.plate_status
                      );
                      
                      return (
                        <div 
                          key={idx}
                          className={`p-4 rounded-xl border bg-slate-900/40 space-y-3.5 transition duration-300 ${
                            hasViolation ? 'border-red-950/40 hover:border-red-900/30' : 'border-slate-850 hover:border-slate-800'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <span className="text-[10px] uppercase font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                                  {vehicle.vehicle_type}
                                </span>
                                <span className={`text-[9px] font-bold font-mono px-2 py-0.5 rounded border ${
                                  vehicle.plate_status === 'VERIFIED'
                                    ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/30'
                                    : vehicle.plate_status === 'LOW_CONFIDENCE'
                                    ? 'bg-amber-950/30 text-amber-400 border-amber-900/30'
                                    : 'bg-red-950/30 text-red-400 border-red-900/30'
                                }`}>
                                  {vehicle.plate_status}
                                </span>
                              </div>
                              
                              <div className="font-mono font-bold tracking-wider text-sm text-slate-200">
                                {displayPlate}
                              </div>
                            </div>
                            
                            <div className="text-right flex flex-col items-end">
                              <span className="text-[10px] font-mono text-slate-500 uppercase">Risk Rating</span>
                              <span className={`text-sm font-mono font-bold mt-1 ${
                                vehicle.risk_score >= 80 ? 'text-red-500' : vehicle.risk_score >= 60 ? 'text-orange-500' : vehicle.risk_score >= 30 ? 'text-amber-500' : 'text-emerald-400'
                              }`}>
                                {vehicle.risk_score} pt
                              </span>
                            </div>
                          </div>

                          {/* Violations tags list */}
                          <div className="flex gap-1.5 flex-wrap">
                            {hasViolation ? (
                              <ViolationTag type={vehicle.violation} />
                            ) : (
                              <span className="flex items-center gap-1 text-[10px] uppercase font-mono tracking-wider font-semibold text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/20 border border-emerald-900/20">
                                <CheckCircle className="w-3.5 h-3.5" /> System Cleared
                              </span>
                            )}
                          </div>

                          {/* Confidence Indicator */}
                          <div className="space-y-1.5 pt-2 border-t border-slate-900">
                            <div className="flex justify-between text-[10px] font-mono text-slate-400">
                              <span>OCR Confidence</span>
                              <span className="font-bold text-slate-350">{confidencePercent}%</span>
                            </div>
                            <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-900">
                              <div className={`h-full ${barColorClass}`} style={{ width: `${confidencePercent}%` }}></div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
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
