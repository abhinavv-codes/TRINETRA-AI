import React from 'react';
import { VIOLATION_LABELS, VIOLATION_COLORS } from '../utils/constants';

export default function ViolationTag({ type }) {
  const label = VIOLATION_LABELS[type] || type;
  
  let colorClasses = "bg-cyan-950/40 text-cyan-400 border border-cyan-800/30";
  if (type === 'NO_HELMET') {
    colorClasses = "bg-amber-950/40 text-amber-400 border border-amber-800/30";
  } else if (type === 'TRIPLE_RIDING' || type === 'RED_LIGHT' || type === 'WRONG_SIDE') {
    colorClasses = "bg-red-950/40 text-red-400 border border-red-800/30";
  } else if (type === 'NONE') {
    colorClasses = "bg-emerald-950/40 text-emerald-400 border border-emerald-800/30";
  }

  return (
    <span className={`px-2.5 py-1 rounded text-[10px] uppercase font-mono tracking-wider font-semibold inline-block ${colorClasses}`}>
      {label}
    </span>
  );
}
