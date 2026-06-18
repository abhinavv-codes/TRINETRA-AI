import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../api/violations';

export const useHeatmap = (filters = {}) => {
  return useQuery({
    queryKey: ['heatmap', filters],
    queryFn: () => analyticsAPI.heatmap(filters),
    refetchInterval: 10000,  // Refresh every 10s
  });
};

export const useCorridors = (limit = 10) => {
  return useQuery({
    queryKey: ['corridors', limit],
    queryFn: () => analyticsAPI.corridors(limit),
    refetchInterval: 30000,  // Refresh every 30s
  });
};

export const useTrends = (filters = {}) => {
  return useQuery({
    queryKey: ['trends', filters],
    queryFn: () => analyticsAPI.trends(filters),
    refetchInterval: 60000,  // Refresh every 60s
  });
};

export const useStats = () => {
  return useQuery({
    queryKey: ['statistics'],
    queryFn: () => analyticsAPI.stats(),
    refetchInterval: 5000,  // Refresh every 5s
  });
};
