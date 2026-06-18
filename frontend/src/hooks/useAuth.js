import { useQuery } from '@tanstack/react-query';
import { authAPI } from '../api/violations';

export const useAuth = () => {
  const token = localStorage.getItem('token');
  
  const { data: user, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: () => authAPI.me(),
    enabled: !!token,
    retry: false,
  });
  
  const login = async (username, password) => {
    const response = await authAPI.login(username, password);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', response.data.role);
    return response.data;
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
  };
  
  return {
    user: user?.data,
    isLoggedIn: !!token,
    isLoading,
    login,
    logout,
  };
};
