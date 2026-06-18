import React from 'react';
import { VIOLATION_LABELS, VIOLATION_COLORS } from '../utils/constants';

export default function ViolationTag({ type }) {
  const label = VIOLATION_LABELS[type] || type;
  const bgColor = VIOLATION_COLORS[type] || '#e5e7eb';

  return (
    <span
      className="px-2 py-1 rounded text-xs font-medium text-gray-900 inline-block"
      style={{ backgroundColor: bgColor }}
    >
      {label}
    </span>
  );
}
