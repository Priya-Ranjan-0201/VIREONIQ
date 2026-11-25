import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import api from '@/lib/axios';
import { extractApiErrorMessage, isNetworkError as isApiNetworkError } from '@/lib/errors';
import { isMockAuthEnabled, mockLogin } from '@/lib/mockAuth';
import { useAuthStore } from '@/store/authStore';
import { Sparkles } from 'lucide-react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

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
    } catch (backendError: unknown) {
      const isNetworkError = isApiNetworkError(backendError);

      if (isNetworkError && isMockAuthEnabled()) {
        // Explicit dev-only fallback when backend is unreachable
        const result = mockLogin(email, password);
        if (result.success && result.token && result.user) {
          setAuth(result.user, result.token);
          toast.success('Access Granted (Dev Mock Mode). Welcome back!');
          navigate('/app/dashboard');
        } else {
          toast.error(result.error || 'Invalid credentials.');
        }
      } else if (isNetworkError) {
        toast.error('Authentication server is unreachable. Please try again later.');
      } else {
        const message = extractApiErrorMessage(backendError, 'Authentication failed.');
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050714] p-6 relative overflow-hidden">
      {/* Dynamic Cosmic Aurora Background Lighting Orbs */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute -top-[20%] left-[25%] h-[650px] w-[650px] rounded-full bg-gradient-to-tr from-indigo-600/30 to-purple-600/20 blur-[150px] animate-aurora-1" />
        <div className="absolute top-[30%] -right-[10%] h-[600px] w-[600px] rounded-full bg-gradient-to-bl from-cyan-500/20 via-blue-600/15 to-transparent blur-[160px] animate-aurora-2" />
        <div className="absolute -bottom-[20%] left-[20%] h-[600px] w-[600px] rounded-full bg-gradient-to-r from-fuchsia-600/15 via-purple-600/20 to-indigo-700/15 blur-[160px] animate-aurora-3" />
      </div>

      <div className="w-full max-w-md space-y-8 relative z-10">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-semibold backdrop-blur-md mb-2 shadow-[0_0_16px_rgba(99,102,241,0.25)]">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI Career & Workforce Intelligence</span>
          </div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-white via-indigo-200 to-cyan-300 bg-clip-text text-transparent tracking-tight">
            VIREONIQ
          </h1>
          <p className="text-slate-400 text-sm font-medium">Log in to your career intelligence dashboard</p>
        </div>

        <div className="bg-[#0A0F24]/80 backdrop-blur-2xl p-8 rounded-[2rem] border border-white/[0.12] shadow-[0_16px_48px_rgba(0,0,0,0.6),inset_0_1px_1px_rgba(255,255,255,0.15)]">
          {isMockAuthEnabled() && (
            <div className="mb-6 p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-xs text-slate-300 space-y-1">
              <p className="font-bold text-indigo-400 uppercase tracking-widest text-[10px] mb-1">Dev Mock Mode Active</p>
              <p>Email: <span className="font-mono text-cyan-300">demo@vireoniq.com</span></p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-300 ml-1 text-xs font-semibold">Work Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 bg-white/[0.04] border-white/10 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/30 rounded-xl text-white placeholder:text-slate-500 transition-all"
                required
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between ml-1">
                <Label htmlFor="password" className="text-slate-300 text-xs font-semibold">Password</Label>
                <Link to="#" className="text-[10px] font-bold uppercase tracking-widest text-indigo-400 hover:text-cyan-300 transition-colors">Forgot?</Link>
              </div>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-12 bg-white/[0.04] border-white/10 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/30 rounded-xl text-white transition-all"
                required
              />
            </div>
            <Button 
              type="submit" 
              className="w-full h-13 text-base font-bold rounded-xl glow-button" 
              disabled={isLoading}
            >
              {isLoading ? 'Authenticating...' : 'Sign In'}
            </Button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/[0.08] text-center text-sm text-slate-400">
            New to VIREONIQ?{' '}
            <Link to="/register" className="text-indigo-400 font-bold hover:text-cyan-300 transition-colors underline-offset-4 hover:underline">
              Create account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
