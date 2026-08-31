import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import api from '@/lib/axios';
import { mockRegister } from '@/lib/mockAuth';

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
    } catch (backendError: any) {
      const isNetworkError = !backendError.response;

      if (isNetworkError) {
        // Backend unreachable — fall back to mock offline registration
        const result = mockRegister(email, password);
        if (result.success) {
          toast.success('Account created (Offline Mode)! Please log in.');
          navigate('/login');
        } else {
          toast.error(result.error || 'Registration failed.');
        }
      } else {
        const detail = backendError.response?.data?.detail;
        const message = typeof detail === 'string' ? detail : 'Registration failed.';
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
          <p className="text-slate-500 mt-2 font-medium">Create your intelligence account</p>
        </div>

        <div className="bg-card/40 backdrop-blur-2xl p-8 rounded-[2rem] border border-white/10 shadow-2xl">
          {/* Demo hint */}
          <div className="mb-6 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-xs text-slate-300">
            <p className="font-bold text-cyan-400 uppercase tracking-widest text-[10px] mb-1">Already have a demo account?</p>
            <p>Go to <Link to="/login" className="text-cyan-400 font-bold underline">Login</Link> and use <span className="font-mono">demo@vireoniq.com</span> / <span className="font-mono">Demo@1234</span></p>
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
              <Label htmlFor="password" className="text-slate-400 ml-1">Secure Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Min 8 chars, uppercase, number, symbol"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-12 bg-white/5 border-white/10 focus:border-primary rounded-xl"
                required
              />
            </div>
            <Button
              type="submit"
              className="w-full h-14 text-lg font-bold rounded-2xl shadow-lg shadow-primary/20"
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Register Securely'}
            </Button>
          </form>

          <div className="mt-8 pt-8 border-t border-white/5 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="text-primary font-bold hover:underline">Log in</Link>
          </div>
        </div>
      </div>
    </div>
  );
};
