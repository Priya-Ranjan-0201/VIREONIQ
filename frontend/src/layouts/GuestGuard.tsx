import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

export const GuestGuard = () => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <Navigate to="/app/dashboard" replace /> : <Outlet />;
};
