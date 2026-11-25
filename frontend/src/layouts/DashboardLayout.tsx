import { NotificationCenter } from '@/components/navigation/NotificationCenter';
import { Sidebar } from '@/components/navigation/Sidebar';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/uiverse/ThemeToggle';
import { UiverseBackground } from '@/components/uiverse/UiverseBackground';
import { Brain, FileText, Menu } from 'lucide-react';
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
    <div className="relative flex h-svh overflow-hidden bg-[#f5f7fa] dark:bg-[#0b0d14] text-slate-900 dark:text-[#eef0f5] selection:bg-[#0ea5e9]/30 selection:text-white transition-colors duration-200">
      {/* Precision Background Grid */}
      <UiverseBackground showGrid={true} />

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-xs z-50 lg:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-200 lg:relative lg:translate-x-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar onClose={() => setIsSidebarOpen(false)} />
      </div>

      {/* Main Content Area */}
      <div className="relative z-10 flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Header: Quiet Chrome */}
        <header className="h-14 border-b border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#07080d]/90 backdrop-blur-md flex items-center justify-between px-4 sm:px-6 z-40 transition-colors">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="icon" 
              className="lg:hidden text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 rounded-lg h-8 w-8" 
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="w-4 h-4" />
            </Button>

            <div className="hidden sm:flex items-center gap-2 text-xs">
              <span className="text-slate-400 dark:text-slate-500 font-medium">VIREONIQ</span>
              <span className="text-slate-300 dark:text-slate-700">/</span>
              <span className="text-slate-800 dark:text-slate-200 font-medium">
                {getPageTitle(location.pathname)}
              </span>
            </div>
          </div>

          {/* Right Action Tools: Restrained, Quiet Actions */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="hidden xl:flex items-center gap-2 bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.06] px-2.5 py-1 rounded-md text-[11px] font-mono text-slate-600 dark:text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Engine Online</span>
            </div>

            <Link
              to="/app/ats-score"
              className="hidden md:inline-flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-white/[0.05] hover:bg-slate-200/80 dark:hover:bg-white/[0.08] border border-slate-200/80 dark:border-white/[0.08] text-slate-700 dark:text-slate-300 transition-colors"
            >
              <FileText className="w-3.5 h-3.5 text-slate-500" />
              <span>ATS Check</span>
            </Link>

            <Link
              to="/app/mnc-interview"
              className="hidden lg:inline-flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-white/[0.05] hover:bg-slate-200/80 dark:hover:bg-white/[0.08] border border-slate-200/80 dark:border-white/[0.08] text-slate-700 dark:text-slate-300 transition-colors"
            >
              <Brain className="w-3.5 h-3.5 text-slate-500" />
              <span>MNC Studio</span>
            </Link>

            {/* Celestial Day/Night Theme Switch */}
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
          <div className="max-w-[1520px] mx-auto min-h-full pb-16">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
