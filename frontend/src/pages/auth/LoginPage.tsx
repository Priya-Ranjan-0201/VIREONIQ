import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import api from '@/lib/axios';
import { mockLogin } from '@/lib/mockAuth';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Try real backend first
      const response = await api.post('/auth/login', { email, password });
      const { access_token } = response.data;
      const userResponse = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      setAuth(userResponse.data, access_token);
      toast.success('Access Granted. Welcome back.');
      navigate('/app/dashboard');
    } catch (backendError: any) {
      const isNetworkError = !backendError.response;

      if (isNetworkError) {
        // Backend unreachable — fall back to mock auth
        const result = mockLogin(email, password);
        if (result.success && result.token && result.user) {
          setAuth(result.user as any, result.token);
          toast.success('Access Granted (Offline Mode). Welcome back!');
          navigate('/app/dashboard');
        } else {
          toast.error(result.error || 'Invalid credentials.');
        }
      } else {
        const message = backendError.response?.data?.detail || 'Authentication failed.';
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px]" />
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-secondary/10 rounded-full blur-[120px]" />
      </div>

      <div className="w-full max-w-md space-y-8 relative z-10">
        <div className="text-center">
          <h1 className="text-4xl font-black bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent tracking-tighter">
            VIREONIQ
          </h1>
          <p className="text-slate-500 mt-2 font-medium">Log in to your intelligence dashboard</p>
        </div>

        <div className="bg-card/40 backdrop-blur-2xl p-8 rounded-[2rem] border border-white/10 shadow-2xl">
          {/* Demo Credentials Banner */}
          <div className="mb-6 p-3 rounded-xl bg-primary/10 border border-primary/20 text-xs text-slate-300 space-y-1">
            <p className="font-bold text-primary uppercase tracking-widest text-[10px] mb-1">Demo Credentials</p>
            <p>📧 <span className="font-mono">demo@vireoniq.com</span></p>
            <p>🔑 <span className="font-mono">Demo@1234</span></p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-400 ml-1">Work Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 bg-white/5 border-white/10 focus:border-primary rounded-xl"
                required
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between ml-1">
                <Label htmlFor="password" className="text-slate-400">Password</Label>
                <Link to="#" className="text-[10px] font-bold uppercase tracking-widest text-primary hover:text-accent transition-colors">Forgot?</Link>
              </div>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-12 bg-white/5 border-white/10 focus:border-primary rounded-xl"
                required
              />
            </div>
            <Button type="submit" className="w-full h-14 text-lg font-bold rounded-2xl shadow-lg shadow-primary/20" disabled={isLoading}>
              {isLoading ? 'Authenticating...' : 'Sign In'}
            </Button>
          </form>

          <div className="mt-8 pt-8 border-t border-white/5 text-center text-sm text-slate-500">
            New to VIREONIQ?{' '}
            <Link to="/register" className="text-primary font-bold hover:underline">Create account</Link>
          </div>
        </div>
      </div>
    </div>
  );
};
