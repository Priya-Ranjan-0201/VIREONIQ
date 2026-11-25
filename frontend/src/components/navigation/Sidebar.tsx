import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';
import {
    Activity,
    Award,
    BarChart3,
    BookOpen,
    Brain,
    Briefcase,
    Building2,
    Calendar,
    ClipboardList,
    Code2,
    Compass,
    Cpu,
    CreditCard,
    Crown, Dna,
    DollarSign,
    Eye,
    FileText,
    Flame,
    Globe,
    LayoutDashboard,
    LogOut,
    MessageSquare,
    Mic,
    Navigation,
    RefreshCw,
    Settings,
    ShieldCheck,
    Sparkles,
    Target,
    TrendingUp,
    Trophy,
    Users2,
    X,
    Zap
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const navSections = [
  {
    label: 'Core intelligence',
    items: [
      { name: 'Dashboard', href: '/app/dashboard', icon: LayoutDashboard },
      { name: 'Daily Career OS', href: '/app/career-os', icon: Compass },
      { name: 'Career Digital Twin', href: '/app/career-twin', icon: Brain },
      { name: 'Career GPS', href: '/app/career-gps', icon: Navigation },
      { name: 'Community Hub', href: '/app/community', icon: Flame },
    ],
  },
  {
    label: 'Resume & documents',
    items: [
      { name: 'Resume Score (NLP)', href: '/app/resume', icon: FileText },
      { name: 'ATS Compatibility', href: '/app/ats-score', icon: Sparkles, badge: '90+' },
      { name: 'JD Match Engine', href: '/app/jd-match', icon: Target },
      { name: 'AI STAR Rewriter', href: '/app/resume-rewriter', icon: Sparkles },
      { name: 'AI Resume Builder', href: '/app/resume-builder', icon: Sparkles },
      { name: 'Gap Analysis', href: '/app/gap-analysis', icon: Target },
    ],
  },
  {
    label: 'Interview studio',
    items: [
      { name: 'MNC Interview Studio', href: '/app/mnc-interview', icon: Cpu, badge: 'MNC' },
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
    label: 'Market & portfolio',
    items: [
      { name: 'Developer Portfolio', href: '/app/portfolio', icon: Code2 },
      { name: 'Salary Predictor', href: '/app/salary-predictor', icon: DollarSign },
      { name: 'Market Intelligence', href: '/app/market-intelligence', icon: TrendingUp },
      { name: 'Psychometric DNA', href: '/app/psychometric-dna', icon: Dna },
      { name: 'Skill Credential', href: '/app/credential', icon: Award },
      { name: 'Talent Passport', href: '/app/passport', icon: ShieldCheck },
      { name: 'Benchmarks', href: '/app/benchmarks', icon: BarChart3 },
    ],
  },
  {
    label: 'Learning & growth',
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
    label: 'Gamification & rewards',
    items: [
      { name: 'Gamification Hub', href: '/app/gamification', icon: Trophy },
      { name: 'Global Leaderboard', href: '/app/leaderboard', icon: Crown },
    ],
  },
  {
    label: 'Opportunities & mentors',
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
    label: 'Admin & portal',
    items: [
      { name: 'College Admin', href: '/app/college-admin', icon: Building2 },
      { name: 'Parent View', href: '/app/parent-view', icon: Eye },
      { name: 'Talent Discovery', href: '/app/recruiter-dashboard', icon: ShieldCheck },
    ],
  },
  {
    label: 'Settings & account',
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
    <aside className="w-full h-full border-r border-slate-200/90 dark:border-white/[0.08] bg-[#f5f7fa] dark:bg-[#07080d] flex flex-col overflow-hidden transition-colors">
      {/* Brand Header */}
      <div className="h-14 px-5 border-b border-slate-200/80 dark:border-white/[0.08] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 flex items-center justify-center font-bold text-xs tracking-tight shadow-2xs">
            V
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold tracking-tight text-slate-900 dark:text-[#eef0f5] font-heading">
              VIREONIQ
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-200/70 dark:bg-white/[0.06] text-slate-600 dark:text-slate-400 border border-slate-300/60 dark:border-white/10">
              v2.0
            </span>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="lg:hidden text-slate-400 hover:text-slate-700 dark:hover:text-white p-1 rounded-md hover:bg-slate-200/50 dark:hover:bg-white/5 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto custom-scrollbar space-y-4">
        {navSections.map((section) => (
          <div key={section.label} className="space-y-0.5">
            <p className="text-[11px] font-medium text-slate-400 dark:text-slate-500 px-2.5 py-1">
              {section.label}
            </p>
            {section.items.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "flex items-center justify-between px-2.5 py-1.5 rounded-lg transition-colors duration-150 group text-xs",
                    isActive
                      ? "bg-slate-200/80 dark:bg-white/[0.08] text-slate-900 dark:text-white font-medium"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/40 dark:hover:bg-white/[0.04]"
                  )}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <item.icon className={cn(
                      "w-4 h-4 shrink-0 transition-colors",
                      isActive ? "text-slate-900 dark:text-white" : "text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300"
                    )} />
                    <span className="truncate">{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className={cn(
                      "text-[10px] font-mono px-1.5 py-0.2 rounded shrink-0",
                      isActive
                        ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold"
                        : "bg-slate-200 dark:bg-white/[0.06] text-slate-500 dark:text-slate-400"
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
      <div className="p-3 border-t border-slate-200/80 dark:border-white/[0.08] bg-[#f5f7fa] dark:bg-[#07080d] shrink-0">
        <div className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-[#11141c] border border-slate-200/80 dark:border-white/[0.06] shadow-2xs">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-7 h-7 rounded-md bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 flex items-center justify-center font-semibold text-xs shrink-0">
              {user?.full_name?.[0] || 'U'}
            </div>
            <div className="overflow-hidden min-w-0">
              <p className="text-xs font-medium truncate text-slate-800 dark:text-slate-200">{user?.full_name || 'Candidate'}</p>
              <p className="text-[10px] text-slate-500 truncate font-mono">{user?.email || 'user@vireoniq.com'}</p>
            </div>
          </div>
          <button 
            onClick={logout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-500 rounded-md hover:bg-slate-100 dark:hover:bg-white/5 transition-colors shrink-0 cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
