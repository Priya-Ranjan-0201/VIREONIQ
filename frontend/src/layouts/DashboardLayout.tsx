import { NotificationCenter } from '@/components/navigation/NotificationCenter';
import { Sidebar } from '@/components/navigation/Sidebar';
import { Button } from '@/components/ui/button';
import { Brain, Menu, Sparkles, Zap } from 'lucide-react';
import { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

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
    <div className="relative flex h-svh overflow-hidden bg-[#050714] text-slate-100 selection:bg-indigo-500/40">
      {/* Dynamic Cosmic Aurora Background Lighting Orbs */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        {/* Primary Indigo/Violet Ethereal Bloom */}
        <div className="absolute -top-[25%] left-[20%] h-[750px] w-[750px] rounded-full bg-gradient-to-tr from-indigo-600/30 to-purple-600/20 blur-[150px] animate-aurora-1" />
        {/* Electric Cyan Neon Accent */}
        <div className="absolute top-[25%] -right-[10%] h-[700px] w-[700px] rounded-full bg-gradient-to-bl from-cyan-500/20 via-blue-600/15 to-transparent blur-[160px] animate-aurora-2" />
        {/* Ethereal Violet/Fuchsia Core */}
        <div className="absolute -bottom-[20%] left-[30%] h-[650px] w-[650px] rounded-full bg-gradient-to-r from-fuchsia-600/15 via-purple-600/20 to-indigo-700/15 blur-[160px] animate-aurora-3" />
        {/* Subtle Emerald Mint Ambient Highlight */}
        <div className="absolute top-[15%] -left-[10%] h-[500px] w-[500px] rounded-full bg-emerald-500/12 blur-[140px] animate-pulse-glow" />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/75 backdrop-blur-md z-50 lg:hidden transition-opacity"
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
        <header className="h-16 border-b border-white/[0.08] bg-slate-950/60 backdrop-blur-3xl flex items-center justify-between px-6 lg:px-10 z-40 shadow-[0_4px_30px_rgba(0,0,0,0.35)]">
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
              <span className="text-slate-400 font-bold tracking-wider">VIREONIQ</span>
              <span className="text-slate-600">/</span>
              <span className="text-white font-semibold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                {getPageTitle(location.pathname)}
              </span>
            </div>
          </div>

          {/* Center/Right Quick Pills */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 bg-white/[0.04] border border-white/10 px-3 py-1.5 rounded-full text-xs text-slate-300 backdrop-blur-md shadow-sm">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-medium text-slate-400">Readiness:</span>
              <span className="font-bold text-emerald-400">82.5%</span>
              <span className="text-slate-600">|</span>
              <span className="text-indigo-300 font-medium">Target: SDE-2</span>
            </div>

            <Link
              to="/app/ats-score"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-200 hover:bg-indigo-500/25 transition-all hover:scale-105 shadow-[0_0_12px_rgba(99,102,241,0.2)]"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
              <span>ATS Check</span>
            </Link>

            <Link
              to="/app/mnc-interview"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-200 hover:bg-cyan-500/25 transition-all hover:scale-105 shadow-[0_0_12px_rgba(0,242,254,0.2)]"
            >
              <Brain className="w-3.5 h-3.5 text-cyan-300" />
              <span>MNC Studio</span>
            </Link>

            <Link
              to="/app/career-os"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-full bg-purple-500/15 border border-purple-500/30 text-purple-200 hover:bg-purple-500/25 transition-all hover:scale-105 shadow-[0_0_12px_rgba(168,85,247,0.2)]"
            >
              <Zap className="w-3.5 h-3.5 text-purple-300" />
              <span>Daily OS</span>
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
