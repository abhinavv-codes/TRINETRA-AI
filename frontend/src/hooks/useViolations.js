import { useQuery } from '@tanstack/react-query';
import { violationsAPI } from '../api/violations';

export const useViolations = (skip = 0, limit = 50, filters = {}) => {
  return useQuery({
    queryKey: ['violations', skip, limit, filters],
    queryFn: () => violationsAPI.list(skip, limit, filters),
    refetchInterval: 3000,  // Poll every 3s
  });
};

export const useViolation = (violationId) => {
  return useQuery({
    queryKey: ['violation', violationId],
    queryFn: () => violationsAPI.get(violationId),
    enabled: !!violationId,
  });
};
