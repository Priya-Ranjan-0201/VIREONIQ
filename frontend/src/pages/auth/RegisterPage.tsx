import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ThemeToggle } from '@/components/uiverse/ThemeToggle';
import { UiverseBackground } from '@/components/uiverse/UiverseBackground';
import { UiverseButton } from '@/components/uiverse/UiverseButton';
import api from '@/lib/axios';
import { extractApiErrorMessage, isNetworkError as isApiNetworkError } from '@/lib/errors';
import { isMockAuthEnabled, mockRegister } from '@/lib/mockAuth';
import { Sparkles, UserPlus } from 'lucide-react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const validatePassword = (pass: string) => {
    return (
      pass.length >= 8 &&
      /[A-Z]/.test(pass) &&
      /[a-z]/.test(pass) &&
      /\d/.test(pass) &&
      /[!@#$%^&*(),.?":{}|<>]/.test(pass)
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validatePassword(password)) {
      toast.error('Password must be 8+ chars with uppercase, lowercase, number & special character.');
      return;
    }

    setIsLoading(true);

    try {
      // Try real backend first
      await api.post('/auth/register', { email, password, role_name: 'User' });
      toast.success('Registration successful! Please log in.');
      navigate('/login');
    } catch (backendError: unknown) {
      const isNetworkError = isApiNetworkError(backendError);

      if (isNetworkError && isMockAuthEnabled()) {
        // Explicit dev-only fallback when backend is unreachable
        const result = mockRegister(email, password);
        if (result.success) {
          toast.success('Account created (Dev Mock Mode)! Please log in.');
          navigate('/login');
        } else {
          toast.error(result.error || 'Registration failed.');
        }
      } else if (isNetworkError) {
        toast.error('Registration server is unreachable. Please try again later.');
      } else {
        const message = extractApiErrorMessage(backendError, 'Registration failed.');
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f8fafc] dark:bg-[#080b18] text-slate-800 dark:text-slate-100 p-6 relative overflow-hidden transition-colors duration-400">
      {/* Dynamic Cosmic Aurora Background with Quad-Color Palette */}
      <UiverseBackground showGrid={true} />

      {/* Top Floating Theme Switcher */}
      <div className="absolute top-6 right-6 z-20 flex items-center gap-2">
        <ThemeToggle showLabel={true} />
      </div>

      <div className="w-full max-w-md space-y-8 relative z-10">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#fdbcb4]/20 border border-[#fdbcb4]/40 text-[#fca59b] dark:text-[#fdbcb4] text-xs font-semibold backdrop-blur-md mb-2 shadow-[0_0_16px_rgba(253,188,180,0.3)]">
            <Sparkles className="w-3.5 h-3.5 text-[#fdbcb4]" />
            <span>AI Career & Workforce Intelligence</span>
          </div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 dark:from-[#fdbcb4] dark:via-[#add8e6] dark:to-[#22c55e] bg-clip-text text-transparent tracking-tight font-heading">
            VIREONIQ
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Create your career intelligence account</p>
        </div>

        <div className="bg-white/85 dark:bg-[#0e1428]/80 backdrop-blur-2xl p-8 rounded-[2rem] border border-slate-200/90 dark:border-white/[0.12] shadow-xl dark:shadow-[0_16px_48px_rgba(0,0,0,0.6),inset_0_1px_1px_rgba(255,255,255,0.15)] transition-all">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-700 dark:text-slate-300 ml-1 text-xs font-semibold">Work Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 bg-slate-50 dark:bg-white/[0.04] border-slate-200 dark:border-white/10 focus:border-[#add8e6] dark:focus:border-[#add8e6] focus:ring-2 focus:ring-[#add8e6]/30 rounded-xl text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 transition-all font-medium"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700 dark:text-slate-300 ml-1 text-xs font-semibold">Secure Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Min 8 chars, uppercase, number, symbol"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-12 bg-slate-50 dark:bg-white/[0.04] border-slate-200 dark:border-white/10 focus:border-[#add8e6] dark:focus:border-[#add8e6] focus:ring-2 focus:ring-[#add8e6]/30 rounded-xl text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 transition-all font-medium"
                required
              />
            </div>
            <UiverseButton
              type="submit"
              variant="cosmic"
              size="lg"
              className="w-full h-13 shadow-[0_0_24px_rgba(253,188,180,0.4)]"
              disabled={isLoading}
              icon={!isLoading && <UserPlus className="w-4 h-4 ml-1" />}
            >
              {isLoading ? 'Creating Account...' : 'Register Securely'}
            </UiverseButton>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-200/80 dark:border-white/10 text-center">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Already have an account?{' '}
              <Link to="/login" className="font-bold text-sky-600 dark:text-[#add8e6] hover:text-[#fdbcb4] transition-colors">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
