import api from './client';

export const violationsAPI = {
  detect: (file, cameraId = 'J17-N') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('camera_id', cameraId);
    return api.post('/violations/detect', formData);
  },
  
  list: (skip = 0, limit = 50, filters = {}) => {
    return api.get('/violations/list', {
      params: { skip, limit, ...filters }
    });
  },
  
  get: (violationId) => {
    return api.get(`/violations/${violationId}`);
  },
  
  verify: (violationId, action, note = '') => {
    return api.post(`/violations/${violationId}/verify`, {
      action,
      note
    });
  },
};

export const analyticsAPI = {
  heatmap: (filters = {}) => {
    return api.get('/analytics/heatmap', { params: filters });
  },
  
  corridors: (limit = 10) => {
    return api.get('/analytics/corridors', { params: { limit } });
  },
  
  trends: (filters = {}) => {
    return api.get('/analytics/trends', { params: filters });
  },
  
  predict: (location, horizon = '7d') => {
    return api.get('/analytics/predict', { params: { location, horizon } });
  },
  
  stats: () => {
    return api.get('/analytics/statistics');
  },
};

export const authAPI = {
  login: (username, password) => {
    return api.post('/auth/login', { username, password });
  },
  
  me: () => {
    return api.get('/auth/me');
  },
};
