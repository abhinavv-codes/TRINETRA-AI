import { format } from 'date-fns';

export const formatDate = (date) => {
  return format(new Date(date), 'dd MMM yyyy HH:mm');
};

export const formatTime = (date) => {
  return format(new Date(date), 'HH:mm:ss');
};

export const getRiskBand = (score) => {
  if (score >= 80) return 'CRITICAL';
  if (score >= 60) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
};

export const getRiskColor = (score) => {
  if (score >= 80) return '#dc2626';  // Dark red
  if (score >= 60) return '#ef4444';  // Red
  if (score >= 40) return '#f59e0b';  // Amber
  return '#10b981';  // Green
};
