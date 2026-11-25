import { NotificationCenter } from '@/components/navigation/NotificationCenter';
import { Sidebar } from '@/components/navigation/Sidebar';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/uiverse/ThemeToggle';
import { UiverseBackground } from '@/components/uiverse/UiverseBackground';
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
      'jd-matcher': 'JD Matcher',
    };
    if (acronymMap[segment]) return acronymMap[segment];
    return segment.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="relative flex h-svh overflow-hidden bg-[#f8fafc] dark:bg-[#080b18] text-slate-800 dark:text-slate-100 selection:bg-[#fdbcb4]/40 selection:text-slate-900 transition-colors duration-400">
      {/* Dynamic Cosmic Aurora Background Lighting with Quad-Color Palette */}
      <UiverseBackground showGrid={true} />

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 dark:bg-black/75 backdrop-blur-md z-50 lg:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 lg:relative lg:translate-x-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar onClose={() => setIsSidebarOpen(false)} />
      </div>

      {/* Main Content Area */}
      <div className="relative z-10 flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Header with Uiverse Glassmorphism & Theme Switch */}
        <header className="h-16 border-b border-slate-200/80 dark:border-white/[0.08] bg-white/75 dark:bg-slate-950/65 backdrop-blur-3xl flex items-center justify-between px-4 sm:px-6 lg:px-8 z-40 shadow-sm dark:shadow-[0_4px_30px_rgba(0,0,0,0.35)] transition-colors">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="icon" 
              className="lg:hidden text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl" 
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </Button>

            <div className="hidden sm:flex items-center gap-2 text-xs">
              <span className="text-slate-500 dark:text-slate-400 font-bold tracking-wider">VIREONIQ</span>
              <span className="text-slate-400 dark:text-slate-600">/</span>
              <span className="text-slate-900 dark:text-white font-semibold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#fdbcb4] shadow-[0_0_8px_#fdbcb4]" />
                {getPageTitle(location.pathname)}
              </span>
            </div>
          </div>

          {/* Center/Right Quick Pills & Uiverse Day/Night Switch */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="hidden xl:flex items-center gap-2 bg-slate-100/90 dark:bg-white/[0.04] border border-slate-200/90 dark:border-white/10 px-3 py-1.5 rounded-full text-xs text-slate-700 dark:text-slate-300 backdrop-blur-md shadow-xs whitespace-nowrap shrink-0">
              <div className="w-2 h-2 rounded-full bg-[#22c55e] shadow-[0_0_8px_#22c55e] animate-pulse shrink-0" />
              <span className="font-medium text-slate-500 dark:text-slate-400">Engine:</span>
              <span className="font-semibold text-[#22c55e]">Active</span>
              <span className="text-slate-300 dark:text-slate-600">|</span>
              <span className="text-sky-700 dark:text-[#add8e6] font-medium">Calibrated v2.0</span>
            </div>

            <Link
              to="/app/ats-score"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-[#fdbcb4]/20 border border-[#fdbcb4]/50 text-slate-800 dark:text-[#fdbcb4] hover:bg-[#fdbcb4]/30 transition-all hover:scale-105 shadow-xs whitespace-nowrap shrink-0"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#fdbcb4] shrink-0" />
              <span>ATS Check</span>
            </Link>

            <Link
              to="/app/mnc-interview"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-[#add8e6]/25 border border-[#add8e6]/50 text-sky-900 dark:text-[#add8e6] hover:bg-[#add8e6]/35 transition-all hover:scale-105 shadow-xs whitespace-nowrap shrink-0"
            >
              <Brain className="w-3.5 h-3.5 text-[#add8e6] shrink-0" />
              <span>MNC Studio</span>
            </Link>

            <Link
              to="/app/career-os"
              className="hidden md:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-[#22c55e]/20 border border-[#22c55e]/40 text-emerald-900 dark:text-[#4ade80] hover:bg-[#22c55e]/30 transition-all hover:scale-105 shadow-xs whitespace-nowrap shrink-0"
            >
              <Zap className="w-3.5 h-3.5 text-[#22c55e] shrink-0" />
              <span>Daily OS</span>
            </Link>

            {/* Uiverse Celestial Day/Night Theme Switch */}
            <div className="shrink-0">
              <ThemeToggle />
            </div>

            <div className="shrink-0">
              <NotificationCenter />
            </div>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden min-w-0 max-w-full p-4 sm:p-6 lg:p-8 custom-scrollbar">
          <div className="max-w-[1600px] mx-auto min-h-full pb-20">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
