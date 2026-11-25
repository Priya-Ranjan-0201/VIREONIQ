import { useAuthStore } from '@/store/authStore';
import { Navigate, Outlet } from 'react-router-dom';

export const GuestGuard = () => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <Navigate to="/app/dashboard" replace /> : <Outlet />;
};
