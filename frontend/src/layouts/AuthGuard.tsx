import { useAuthStore } from '@/store/authStore';
import { Navigate, Outlet } from 'react-router-dom';

export const AuthGuard = () => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};
