import { useState } from 'react';
import { Outlet, useLocation, Link } from 'react-router-dom';
import { Sidebar } from '@/components/navigation/Sidebar';
import { NotificationCenter } from '@/components/navigation/NotificationCenter';
import { Menu, Sparkles, Brain, ShieldCheck, Search, Compass, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const DashboardLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();

  // Clean route name formatter with proper acronym capitalization
  const getPageTitle = (path: string) => {
    const segment = path.split('/').filter(Boolean).pop() || 'dashboard';
    const acronymMap: Record<string, string> = {
      'career-gps': 'Career GPS',
      'career-os': 'Career OS',
      'ats-score': 'ATS Score Checker',
      'mnc-interview': 'MNC Studio',
      'ai-copilot': 'AI Copilot',
      'p2p-mock': 'P2P Mock',
      'jd-matcher': 'JD Matcher'
    };
    if (acronymMap[segment]) return acronymMap[segment];
    return segment.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="relative flex h-svh overflow-hidden bg-[#060813] text-slate-100 selection:bg-indigo-500/30">
      {/* Background Ambient Lighting Orbs */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute -top-[20%] left-[15%] h-[650px] w-[650px] rounded-full bg-indigo-600/15 blur-[140px] animate-pulse-glow" />
        <div className="absolute top-[35%] -right-[15%] h-[700px] w-[700px] rounded-full bg-cyan-500/12 blur-[160px] animate-pulse-glow" />
        <div className="absolute -bottom-[15%] left-[25%] h-[600px] w-[600px] rounded-full bg-purple-600/12 blur-[150px]" />
        <div className="absolute top-[10%] -left-[10%] h-[400px] w-[400px] rounded-full bg-emerald-500/08 blur-[130px]" />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 lg:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 lg:relative lg:translate-x-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar onClose={() => setIsSidebarOpen(false)} />
      </div>

      {/* Main Content Area */}
      <div className="relative z-10 flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-white/5 bg-slate-950/40 backdrop-blur-2xl flex items-center justify-between px-6 lg:px-10 z-40 shadow-[0_4px_30px_rgba(0,0,0,0.2)]">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon" 
              className="lg:hidden text-slate-400 hover:text-white hover:bg-white/5 rounded-xl" 
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </Button>

            <div className="hidden sm:flex items-center gap-2 text-xs">
              <span className="text-slate-500 font-medium">VIREONIQ</span>
              <span className="text-slate-600">/</span>
              <span className="text-slate-200 font-semibold">{getPageTitle(location.pathname)}</span>
            </div>
          </div>

          {/* Center/Right Quick Pills */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 bg-white/[0.03] border border-white/10 px-3 py-1.5 rounded-full text-xs text-slate-300 backdrop-blur-md">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-medium text-slate-400">Readiness:</span>
              <span className="font-bold text-emerald-400">82.5%</span>
              <span className="text-slate-600">|</span>
              <span className="text-indigo-300 font-medium">Target: SDE-2</span>
            </div>

            <Link
              to="/app/ats-score"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 hover:bg-indigo-500/20 transition-all hover:scale-105"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>ATS Check</span>
            </Link>

            <Link
              to="/app/mnc-interview"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 hover:bg-cyan-500/20 transition-all hover:scale-105"
            >
              <Brain className="w-3.5 h-3.5" />
              <span>MNC Studio</span>
            </Link>

            <NotificationCenter />
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 custom-scrollbar">
          <div className="max-w-[1600px] mx-auto min-h-full pb-20">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
