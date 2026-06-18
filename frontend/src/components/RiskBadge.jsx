import React from 'react';
import { RISK_COLORS } from '../utils/constants';

export default function RiskBadge({ score }) {
  let band, color;
  
  if (score >= 80) {
    band = 'CRITICAL';
    color = RISK_COLORS.CRITICAL;
  } else if (score >= 60) {
    band = 'HIGH';
    color = RISK_COLORS.HIGH;
  } else if (score >= 40) {
    band = 'MEDIUM';
    color = RISK_COLORS.MEDIUM;
  } else {
    band = 'LOW';
    color = RISK_COLORS.LOW;
  }

  return (
    <div
      className="px-3 py-1 rounded-full text-white font-bold text-sm"
      style={{ backgroundColor: color }}
    >
      {score}/100 {band}
    </div>
  );
}
