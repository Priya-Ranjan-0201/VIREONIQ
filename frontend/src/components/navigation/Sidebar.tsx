import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, FileText, Target, MessageSquare, Briefcase, ClipboardList,
  CreditCard, Settings, LogOut, Zap, BarChart3, Mic, ShieldCheck, Users2,
  BookOpen, X, Navigation, Trophy, Crown, Dna, Brain, Building2,
  TrendingUp, Activity, Eye, Calendar, Cpu, RefreshCw, Globe, Award, Flame, Sparkles, Compass,
  CheckCircle2, DollarSign, Code2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';

const navSections = [
  {
    label: 'Core Intelligence',
    items: [
      { name: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard, badge: 'Live' },
      { name: 'Daily Career OS', href: '/app/career-os', icon: Compass },
      { name: 'Career Digital Twin', href: '/app/career-twin', icon: Brain },
      { name: 'Career GPS', href: '/app/career-gps', icon: Navigation },
      { name: 'Community Hub', href: '/app/community', icon: Flame },
    ],
  },
  {
    label: 'Resume & Documents',
    items: [
      { name: 'Resume Score (NLP)', href: '/app/resume', icon: FileText },
      { name: 'ATS Compatibility', href: '/app/ats-score', icon: Sparkles, badge: 'ATS 90+' },
      { name: 'JD Match Engine', href: '/app/jd-match', icon: Target, badge: 'Smart' },
      { name: 'AI STAR Rewriter', href: '/app/resume-rewriter', icon: Sparkles, badge: 'STAR' },
      { name: 'AI Resume Builder', href: '/app/resume-builder', icon: Sparkles, badge: 'MNC' },
      { name: 'Gap Analysis', href: '/app/gap-analysis', icon: Target },
    ],
  },
  {
    label: 'Interview Studio',
    items: [
      { name: 'MNC Interview Studio', href: '/app/mnc-interview', icon: Cpu, badge: '8-Round' },
      { name: 'Adaptive Assessment', href: '/app/assessment', icon: Brain },
      { name: 'AI Interview Simulator', href: '/app/interview', icon: MessageSquare },
      { name: 'Voice Mode', href: '/app/voice-interview', icon: Mic },
      { name: 'Coding Sandbox', href: '/app/coding-interview', icon: Code2 },
      { name: 'P2P Matchmaker', href: '/app/p2p-mock', icon: Users2 },
      { name: 'Company Profiles', href: '/app/company-profiles', icon: Building2 },
      { name: 'Cognitive Load', href: '/app/cognitive-load', icon: Activity },
    ],
  },
  {
    label: 'Market & Portfolio',
    items: [
      { name: 'Developer Portfolio', href: '/app/portfolio', icon: Code2, badge: 'GitHub' },
      { name: 'Salary Predictor', href: '/app/salary-predictor', icon: DollarSign, badge: 'PPP' },
      { name: 'Market Intelligence', href: '/app/market-intelligence', icon: TrendingUp },
      { name: 'Psychometric DNA', href: '/app/psychometric-dna', icon: Dna },
      { name: 'Skill Credential', href: '/app/credential', icon: Award },
      { name: 'Talent Passport', href: '/app/passport', icon: ShieldCheck },
      { name: 'Benchmarks', href: '/app/benchmarks', icon: BarChart3 },
    ],
  },
  {
    label: 'Learning & Growth',
    items: [
      { name: 'Syllabus Optimizer', href: '/app/syllabus-optimizer', icon: BookOpen },
      { name: 'Micro-Internships', href: '/app/micro-internships', icon: Briefcase },
      { name: 'Skill Decay Tracker', href: '/app/skill-decay', icon: Brain },
      { name: 'Prep Calendar', href: '/app/prep-calendar', icon: Calendar },
      { name: 'Career Rebirth', href: '/app/rebirth', icon: RefreshCw },
      { name: 'Language Bridge', href: '/app/language-bridge', icon: Globe },
      { name: 'High School Trajectory', href: '/app/highschool', icon: BookOpen },
    ],
  },
  {
    label: 'Gamification & Rewards',
    items: [
      { name: 'Gamification Hub', href: '/app/gamification', icon: Trophy },
      { name: 'Global Leaderboard', href: '/app/leaderboard', icon: Crown },
    ],
  },
  {
    label: 'Opportunities & Mentors',
    items: [
      { name: 'Opportunities', href: '/app/opportunities', icon: Briefcase },
      { name: 'Application Tracker', href: '/app/applications', icon: ClipboardList },
      { name: 'Offer Comparison', href: '/app/offer-comparison', icon: ClipboardList },
      { name: 'Offer Negotiator', href: '/app/offer-negotiator', icon: Zap },
      { name: 'Routing Intelligence', href: '/app/routing-intelligence', icon: Navigation },
      { name: 'Mentor Network', href: '/app/mentors', icon: Users2 },
      { name: 'Company Truth DB', href: '/app/truth', icon: ClipboardList },
      { name: 'Employer Truth Score', href: '/app/employer-truth', icon: Trophy },
    ],
  },
  {
    label: 'Admin & Portal',
    items: [
      { name: 'College Admin', href: '/app/college-admin', icon: Building2 },
      { name: 'Parent View', href: '/app/parent-view', icon: Eye },
      { name: 'Talent Discovery', href: '/app/recruiter-dashboard', icon: ShieldCheck },
    ],
  },
  {
    label: 'Settings & Account',
    items: [
      { name: 'Billing & Plans', href: '/app/billing', icon: CreditCard },
      { name: 'Settings & Security', href: '/app/settings', icon: Settings },
    ],
  },
];

export const Sidebar = ({ onClose }: { onClose?: () => void }) => {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-full h-full border-r border-white/10 bg-slate-950/80 backdrop-blur-2xl flex flex-col overflow-hidden shadow-[20px_0_40px_rgba(0,0,0,0.5)]">
      {/* Brand Header */}
      <div className="p-6 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary via-indigo-500 to-accent flex items-center justify-center font-black text-white shadow-lg shadow-indigo-500/30">
            V
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-indigo-200 to-accent bg-clip-text text-transparent font-heading">
                VIREONIQ
              </h1>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                X
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>AI Core Online</span>
            </div>
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="lg:hidden text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5 transition-colors">
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto custom-scrollbar space-y-4">
        {navSections.map((section) => (
          <div key={section.label} className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3 py-1">
              {section.label}
            </p>
            {section.items.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "flex items-center justify-between px-3 py-2 rounded-xl transition-all duration-200 group text-xs font-medium",
                    isActive
                      ? "bg-gradient-to-r from-primary/20 via-indigo-500/15 to-transparent text-white border-l-2 border-primary shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1)] font-semibold"
                      : "text-slate-400 hover:text-slate-100 hover:bg-white/[0.04] border-l-2 border-transparent"
                  )}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <item.icon className={cn(
                      "w-4 h-4 shrink-0 transition-colors",
                      isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300"
                    )} />
                    <span className="truncate">{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className={cn(
                      "text-[9px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider shrink-0",
                      isActive
                        ? "bg-indigo-500/30 text-indigo-200 border border-indigo-400/40"
                        : "bg-white/5 text-slate-400 group-hover:text-slate-300"
                    )}>
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User Profile Footer */}
      <div className="p-3 border-t border-white/5 bg-slate-950/60">
        <div className="flex items-center justify-between p-2 rounded-xl bg-white/[0.03] border border-white/5">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-accent flex items-center justify-center font-bold text-xs text-white shadow-md shadow-primary/20 shrink-0">
              {user?.full_name?.[0] || 'U'}
            </div>
            <div className="overflow-hidden min-w-0">
              <p className="text-xs font-semibold truncate text-slate-200">{user?.full_name || 'Candidate'}</p>
              <p className="text-[10px] text-slate-500 truncate">{user?.email || 'user@vireoniq.com'}</p>
            </div>
          </div>
          <button 
            onClick={logout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-white/5 transition-colors shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
