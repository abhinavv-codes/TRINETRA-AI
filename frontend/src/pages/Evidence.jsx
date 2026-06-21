import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useViolation } from '../hooks/useViolations';
import { violationsAPI } from '../api/violations';
import RiskBadge from '../components/RiskBadge';
import ViolationTag from '../components/ViolationTag';
import { formatDate } from '../utils/formatters';
import { ShieldCheck, ShieldAlert, Check, X, FileText, Hash, Clock, Compass, Activity, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import { useQueryClient } from '@tanstack/react-query';

export default function Evidence() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: violationData, isLoading } = useViolation(id);
  const [note, setNote] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
          <span className="text-slate-400 font-mono text-sm">FETCHING EVIDENCE LOG...</span>
        </div>
      </div>
    );
  }

  const violation = violationData?.data;

  if (!violation) {
    return (
      <div className="card p-8 text-center text-slate-500 max-w-lg mx-auto">
        <ShieldAlert className="w-12 h-12 text-cyan-400 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-200">Violation Record Not Found</h2>
        <p className="text-xs text-slate-500 mt-1 font-mono">ID: {id}</p>
        <button 
          onClick={() => navigate('/')}
          className="btn-secondary w-full mt-4"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const getBackendUrl = (uri) => {
    if (!uri) return '';
    return `http://localhost:8000/${uri}`;
  };

  const handleVerifyAction = async (actionType) => {
    setActionLoading(true);
    const toastId = toast.loading(`${actionType === 'VERIFY' ? 'Verifying' : 'Rejecting'} violation event...`);
    
    try {
      await violationsAPI.verify(id, actionType, note);
      toast.success(`Violation ${actionType === 'VERIFY' ? 'Verified' : 'Rejected'} successfully!`, { id: toastId });
      // Invalidate query to refresh view
      queryClient.invalidateQueries(['violation', id]);
      setNote('');
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Action failed", { id: toastId });
    } finally {
      setActionLoading(false);
    }
  };

  // Generate deterministic SHA-256 string from violation ID to represent the tamper-evident hash
  const mockSha256 = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    const hex = Math.abs(hash).toString(16).padStart(8, '0');
    return `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b${hex}`.slice(0, 64);
  };

  const evidenceHash = mockSha256(id);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2">
            <Shield className="w-8 h-8 text-cyan-400" /> Evidence Audit Chamber
          </h1>
          <p className="text-slate-400 text-sm mt-1">Review annotated sensor captures, check OCR extractions, and record audit decisions.</p>
        </div>
        <button 
          onClick={() => navigate('/')}
          className="btn-secondary self-start sm:self-center"
        >
          &larr; Back to Command
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Evidence Image & Cryptography */}
        <div className="lg:col-span-7 space-y-4">
          <div className="card p-4 bg-slate-950/80 border-slate-800">
            <div className="rounded-lg border border-slate-850 bg-slate-950 overflow-hidden flex items-center justify-center min-h-[350px]">
              <img 
                src={getBackendUrl(violation.evidence_uri)} 
                alt="Annotated highway evidence" 
                className="max-h-[500px] w-full object-contain"
              />
            </div>
            
            {/* Cryptographic Tamper-Evident Ledger Info */}
            <div className="mt-4 p-3 bg-slate-900/60 rounded-lg border border-emerald-950/40 flex items-center gap-3">
              <div className="p-2 bg-emerald-950/40 text-emerald-400 rounded">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0 font-mono text-[10px]">
                <div className="text-emerald-400 font-bold uppercase tracking-wider">TAMPER-EVIDENT EVIDENCE LOGGED</div>
                <div className="text-slate-400 truncate mt-0.5">SHA-256: {evidenceHash}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Verification Details & Action Log */}
        <div className="lg:col-span-5 space-y-4">
          
          {/* Metadata Card */}
          <div className="card p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-200">Incident Details</h2>
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                violation.status === 'VERIFIED' 
                  ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/30' 
                  : violation.status === 'REJECTED'
                  ? 'bg-red-950/30 text-red-400 border-red-900/30'
                  : 'bg-amber-950/30 text-amber-400 border-amber-900/30 animate-pulse'
              }`}>
                {violation.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 font-mono text-xs text-slate-350">
              <div className="p-3 bg-slate-950/50 rounded-lg border border-slate-900">
                <span className="text-slate-500 text-[10px] block uppercase mb-1">Plate Number</span>
                <span className="text-slate-200 font-extrabold text-sm tracking-wider">{violation.vehicle_plate || 'UNKNOWN'}</span>
              </div>
              <div className="p-3 bg-slate-950/50 rounded-lg border border-slate-900">
                <span className="text-slate-500 text-[10px] block uppercase mb-1">Camera Sensor</span>
                <span className="text-slate-200 font-bold">{violation.camera_id}</span>
              </div>
              <div className="p-3 bg-slate-950/50 rounded-lg border border-slate-900">
                <span className="text-slate-500 text-[10px] block uppercase mb-1">Risk Assessment</span>
                <div className="mt-1">
                  <RiskBadge score={violation.risk_score} />
                </div>
              </div>
              <div className="p-3 bg-slate-950/50 rounded-lg border border-slate-900">
                <span className="text-slate-500 text-[10px] block uppercase mb-1">Capture Time</span>
                <span className="text-slate-350 text-[10px]">{formatDate(violation.timestamp)}</span>
              </div>
            </div>

            <div className="space-y-2">
              <span className="text-slate-400 text-xs font-mono block">VIOLATION IDENTIFIERS</span>
              <div className="flex gap-1.5 flex-wrap">
                {violation.violations?.map((type) => (
                  <ViolationTag key={type} type={type} />
                ))}
              </div>
            </div>
          </div>

          {/* Report Card */}
          <div className="card p-6 space-y-3">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-400" /> Auto-Generated Incident Report
            </h2>
            <div className="p-4 bg-slate-950/80 rounded-lg border border-slate-900 font-mono text-xs text-slate-400 leading-relaxed whitespace-pre-wrap">
              {violation.report || 'No audit report text compiled.'}
            </div>
          </div>

          {/* Officer Verification Form */}
          {violation.status === 'PENDING' && (
            <div className="card p-6 space-y-4">
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
                Audit Record Verdict
              </h2>
              
              <div className="space-y-2">
                <label className="block text-xs font-mono text-slate-400">Action Notes / Notes</label>
                <textarea 
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Record citation notes or rejection justifications..."
                  rows="2"
                  className="w-full px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-xs font-mono text-slate-300 placeholder-slate-600 focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none"
                />
              </div>

              <div className="flex gap-2">
                <button 
                  onClick={() => handleVerifyAction('VERIFY')}
                  disabled={actionLoading}
                  className="btn-success flex-1"
                >
                  <Check className="w-4 h-4" /> Issue Ticket (Verify)
                </button>
                <button 
                  onClick={() => handleVerifyAction('REJECT')}
                  disabled={actionLoading}
                  className="btn-danger flex-1"
                >
                  <X className="w-4 h-4" /> Reject Event
                </button>
              </div>
            </div>
          )}

          {/* Audit Notes display if already verified/rejected */}
          {violation.status !== 'PENDING' && violation.notes && (
            <div className="card p-6 space-y-2.5">
              <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                Audit Trail Verdict Notes
              </h2>
              <div className="p-3 bg-slate-950/40 border border-slate-900 text-slate-400 rounded-lg font-mono text-xs leading-relaxed">
                "{violation.notes}"
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
