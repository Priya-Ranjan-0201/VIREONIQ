import { lazy, Suspense, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster, toast } from 'sonner';
import { syncOfflineSessions } from '@/lib/offlineEngine';

import { AuthGuard } from '@/layouts/AuthGuard';
import { GuestGuard } from '@/layouts/GuestGuard';
import { DashboardLayout } from '@/layouts/DashboardLayout';

// ──────────────────────────────────────────────
// Code-split page imports (React.lazy)
// Reduces initial JS bundle by ~60% via on-demand chunk loading
// ──────────────────────────────────────────────

// Resilient lazy loader with automatic network/chunk retry
function lazyWithRetry<T extends React.ComponentType<any>>(
  factory: () => Promise<{ default: T } | any>
) {
  return lazy(async () => {
    try {
      const res = await factory();
      return res.default ? res : { default: res };
    } catch (error: any) {
      console.warn('Component chunk load failed, retrying in 350ms...', error);
      await new Promise((r) => setTimeout(r, 350));
      try {
        const res = await factory();
        return res.default ? res : { default: res };
      } catch (retryError: any) {
        console.error('Second chunk load failed, auto-reloading page for fresh assets:', retryError);
        const retryKey = 'route_reload_' + window.location.pathname;
        if (!sessionStorage.getItem(retryKey)) {
          sessionStorage.setItem(retryKey, 'true');
          window.location.reload();
        }
        throw retryError;
      }
    }
  });
}


// Auth (eagerly loaded — small bundles)
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';

// Public (no auth required)
const CredentialProfile = lazyWithRetry(() => import('@/pages/CredentialProfile').then(m => ({ default: m.CredentialProfile })));

// Core
const DashboardPage = lazyWithRetry(() => import('@/pages/dashboard/DashboardPage').then(m => ({ default: m.DashboardPage })));
const CareerOSPage = lazyWithRetry(() => import('@/pages/interventions/CareerOSPage').then(m => ({ default: m.CareerOSPage })));
const CareerReadinessPage = lazyWithRetry(() => import('@/pages/readiness/CareerReadinessPage').then(m => ({ default: m.CareerReadinessPage })));
const CareerTwinPage = lazyWithRetry(() => import('@/pages/career/CareerTwinPage').then(m => ({ default: m.CareerTwinPage })));
const CareerSimulatorPage = lazyWithRetry(() => import('@/pages/simulator/CareerSimulatorPage').then(m => ({ default: m.CareerSimulatorPage })));
const ResumeScorePage = lazyWithRetry(() => import('@/pages/resume/ResumeScorePage').then(m => ({ default: m.ResumeScorePage })));
const GapAnalysisPage = lazyWithRetry(() => import('@/pages/gap/GapAnalysisPage').then(m => ({ default: m.GapAnalysisPage })));
const CareerGPSPage = lazyWithRetry(() => import('@/pages/career/CareerGPSPage').then(m => ({ default: m.CareerGPSPage })));

// Interview & Assessment
const MNCInterviewStudioPage = lazyWithRetry(() => import('@/pages/interview/MNCInterviewStudioPage').then(m => ({ default: m.MNCInterviewStudioPage })));
const AssessmentRoomPage = lazyWithRetry(() => import('@/pages/assessment/AssessmentRoomPage').then(m => ({ default: m.AssessmentRoomPage })));
const InterviewPage = lazyWithRetry(() => import('@/pages/interview/InterviewPage').then(m => ({ default: m.InterviewPage })));
const CodingInterviewPage = lazyWithRetry(() => import('@/pages/interview/CodingInterviewPage').then(m => ({ default: m.CodingInterviewPage })));
const VoiceInterviewPage = lazyWithRetry(() => import('@/pages/interview/VoiceInterviewPage').then(m => ({ default: m.VoiceInterviewPage })));
const P2PMockPage = lazyWithRetry(() => import('@/pages/interview/P2PMockPage').then(m => ({ default: m.P2PMockPage })));
const CognitiveLoadMonitorPage = lazyWithRetry(() => import('@/pages/interview/CognitiveLoadMonitorPage').then(m => ({ default: m.CognitiveLoadMonitorPage })));
const CompanyProfilesPage = lazyWithRetry(() => import('@/pages/companies/CompanyProfilesPage').then(m => ({ default: m.CompanyProfilesPage })));

// Learning
const SyllabusOptimizer = lazyWithRetry(() => import('@/pages/learning/SyllabusOptimizer').then(m => ({ default: m.SyllabusOptimizer })));
const MicroInternships = lazyWithRetry(() => import('@/pages/learning/MicroInternships').then(m => ({ default: m.MicroInternships })));
const SkillDecayPage = lazyWithRetry(() => import('@/pages/analytics/SkillDecayPage').then(m => ({ default: m.SkillDecayPage })));
const CalendarExportPage = lazyWithRetry(() => import('@/pages/analytics/CalendarExportPage').then(m => ({ default: m.CalendarExportPage })));
const CareerRebirth = lazyWithRetry(() => import('@/pages/CareerRebirth').then(m => ({ default: m.CareerRebirth })));
const LanguageBridge = lazyWithRetry(() => import('@/pages/LanguageBridge').then(m => ({ default: m.LanguageBridge })));
const HighSchoolTrajectory = lazyWithRetry(() => import('@/pages/HighSchoolTrajectory').then(m => ({ default: m.HighSchoolTrajectory })));

// Intelligence
const AICopilotPage = lazyWithRetry(() => import('@/pages/copilot/AICopilotPage').then(m => ({ default: m.AICopilotPage })));
const PrivacySettingsPage = lazyWithRetry(() => import('@/pages/privacy/PrivacySettingsPage').then(m => ({ default: m.PrivacySettingsPage })));
const OutcomeIntelligencePage = lazyWithRetry(() => import('@/pages/analytics/OutcomeIntelligencePage').then(m => ({ default: m.OutcomeIntelligencePage })));
const DeveloperPlatformPage = lazyWithRetry(() => import('@/pages/developer/DeveloperPlatformPage').then(m => ({ default: m.DeveloperPlatformPage })));
const CareerControlCenterPage = lazyWithRetry(() => import('@/pages/career/CareerControlCenterPage').then(m => ({ default: m.CareerControlCenterPage })));
const ProductionCertificationPage = lazyWithRetry(() => import('@/pages/certification/ProductionCertificationPage').then(m => ({ default: m.ProductionCertificationPage })));
const PsychometricDNAPage = lazyWithRetry(() => import('@/pages/psychometric/PsychometricDNAPage').then(m => ({ default: m.PsychometricDNAPage })));
const MarketIntelligencePage = lazyWithRetry(() => import('@/pages/analytics/MarketIntelligencePage').then(m => ({ default: m.MarketIntelligencePage })));
const BenchmarkReportPage = lazyWithRetry(() => import('@/pages/analytics/BenchmarkReportPage').then(m => ({ default: m.BenchmarkReportPage })));
const TalentPassportPage = lazyWithRetry(() => import('@/pages/passport/TalentPassportPage').then(m => ({ default: m.TalentPassportPage })));
const PublicVerificationPage = lazyWithRetry(() => import('@/pages/passport/PublicVerificationPage').then(m => ({ default: m.PublicVerificationPage })));
const MyCredential = lazyWithRetry(() => import('@/pages/MyCredential').then(m => ({ default: m.MyCredential })));
const TalentPassport = lazyWithRetry(() => import('@/pages/passport/TalentPassportPage').then(m => ({ default: m.TalentPassportPage })));

// Gamification
const GamificationPage = lazyWithRetry(() => import('@/pages/gamification/GamificationPage').then(m => ({ default: m.GamificationPage })));
const LeaderboardPage = lazyWithRetry(() => import('@/pages/gamification/LeaderboardPage').then(m => ({ default: m.LeaderboardPage })));

// Jobs & Mentors
const OpportunityHub = lazyWithRetry(() => import('@/pages/jobs/OpportunityHub').then(m => ({ default: m.OpportunityHub })));
const SmartApplyTracker = lazyWithRetry(() => import('@/pages/jobs/SmartApplyTracker').then(m => ({ default: m.SmartApplyTracker })));
const OfferComparator = lazyWithRetry(() => import('@/pages/jobs/OfferComparator').then(m => ({ default: m.OfferComparator })));
const OfferNegotiatorPage = lazyWithRetry(() => import('@/pages/jobs/OfferNegotiatorPage').then(m => ({ default: m.OfferNegotiatorPage })));
const ApplicationIntelligence = lazyWithRetry(() => import('@/pages/ApplicationIntelligence').then(m => ({ default: m.ApplicationIntelligence })));
const MentorNetwork = lazyWithRetry(() => import('@/pages/MentorNetwork').then(m => ({ default: m.MentorNetwork })));
const TruthDatabase = lazyWithRetry(() => import('@/pages/TruthDatabase').then(m => ({ default: m.TruthDatabase })));
const EmployerTruthScore = lazyWithRetry(() => import('@/pages/EmployerTruthScore').then(m => ({ default: m.EmployerTruthScore })));

// Admin
const CollegeAdminDashboard = lazyWithRetry(() => import('@/pages/college/CollegeAdminDashboard').then(m => ({ default: m.CollegeAdminDashboard })));
const ParentDashboard = lazyWithRetry(() => import('@/pages/parent/ParentDashboard').then(m => ({ default: m.ParentDashboard })));
const RecruiterDashboard = lazyWithRetry(() => import('@/pages/recruiter/RecruiterIntelligencePage').then(m => ({ default: m.RecruiterIntelligencePage })));
const RecruiterIntelligencePage = lazyWithRetry(() => import('@/pages/recruiter/RecruiterIntelligencePage').then(m => ({ default: m.RecruiterIntelligencePage })));
const WorkforceIntelligencePage = lazyWithRetry(() => import('@/pages/workforce/WorkforceIntelligencePage').then(m => ({ default: m.WorkforceIntelligencePage })));

// Account
const PricingPage = lazyWithRetry(() => import('@/pages/billing/PricingPage').then(m => ({ default: m.PricingPage })));
const SettingsPage = lazyWithRetry(() => import('@/pages/settings/SettingsPage').then(m => ({ default: m.SettingsPage })));

// NEW — Session 32: Community & Resume Builder
const CommunityHub = lazyWithRetry(() => import('@/pages/CommunityHub'));
const ResumeBuilder = lazyWithRetry(() => import('@/pages/ResumeBuilder'));

// Last Mile Sessions 32 - 41
const OfflinePractice = lazyWithRetry(() => import('@/pages/OfflinePractice'));
const FacultyDashboard = lazyWithRetry(() => import('@/pages/FacultyDashboard'));
const EarnToLearn = lazyWithRetry(() => import('@/pages/EarnToLearn'));
const ParentConnect = lazyWithRetry(() => import('@/pages/ParentConnect'));
const CohortMode = lazyWithRetry(() => import('@/pages/CohortMode'));
const VernacularLibrary = lazyWithRetry(() => import('@/pages/VernacularLibrary'));
const LabMode = lazyWithRetry(() => import('@/pages/LabMode'));
const RecruiterWarRoom = lazyWithRetry(() => import('@/pages/recruiter/WarRoom'));

// Native Intelligence Capabilities (ATS, JD Matching & Developer Portfolio)
const AtsScoreChecker = lazyWithRetry(() => import('@/pages/resume/AtsScoreChecker').then(m => ({ default: m.AtsScoreChecker })));
const JdMatcher = lazyWithRetry(() => import('@/pages/resume/JdMatcher').then(m => ({ default: m.JdMatcher })));
const ResumeSectionRewriterPage = lazyWithRetry(() => import('@/pages/resume/ResumeSectionRewriterPage').then(m => ({ default: m.ResumeSectionRewriterPage })));
const PortfolioIntelligence = lazyWithRetry(() => import('@/pages/career/PortfolioIntelligence').then(m => ({ default: m.PortfolioIntelligence })));
const SalaryPredictor = lazyWithRetry(() => import('@/pages/career/SalaryPredictor').then(m => ({ default: m.SalaryPredictor })));


// ──────────────────────────────────────────────
// Loading Fallback
// ──────────────────────────────────────────────

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[60vh]">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      <p className="text-sm text-slate-500 font-medium animate-pulse">Loading module…</p>
    </div>
  </div>
);


// ──────────────────────────────────────────────
// App
// ──────────────────────────────────────────────

const queryClient = new QueryClient();

export default function App() {
  useEffect(() => {
    const handleOnline = () => {
      syncOfflineSessions().then(result => {
        if (result.success && result.syncedCount > 0) {
          toast.success(`Automatically synchronized ${result.syncedCount} queued offline sessions!`);
        }
      });
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/verify/:reference?" element={<PublicVerificationPage />} />
            <Route path="/verify" element={<PublicVerificationPage />} />
            <Route path="/passport/public/:share_token" element={<TalentPassportPage />} />

            <Route element={<GuestGuard />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            <Route element={<AuthGuard />}>
              <Route path="/app" element={<DashboardLayout />}>
                {/* Core */}
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="career-os" element={<CareerOSPage />} />
                <Route path="readiness" element={<CareerReadinessPage />} />
                <Route path="career-twin" element={<CareerTwinPage />} />
                <Route path="career-simulator" element={<CareerSimulatorPage />} />
                <Route path="simulator" element={<CareerSimulatorPage />} />
                <Route path="copilot" element={<AICopilotPage />} />
                <Route path="ai-copilot" element={<AICopilotPage />} />
                <Route path="privacy" element={<PrivacySettingsPage />} />
                <Route path="privacy-settings" element={<PrivacySettingsPage />} />
                <Route path="outcomes" element={<OutcomeIntelligencePage />} />
                <Route path="outcome-intelligence" element={<OutcomeIntelligencePage />} />
                <Route path="developer" element={<DeveloperPlatformPage />} />
                <Route path="developer-platform" element={<DeveloperPlatformPage />} />
                <Route path="control-center" element={<CareerControlCenterPage />} />
                <Route path="career-control-center" element={<CareerControlCenterPage />} />
                <Route path="certification" element={<ProductionCertificationPage />} />
                <Route path="production-certification" element={<ProductionCertificationPage />} />
                <Route path="resume" element={<ResumeScorePage />} />
                <Route path="ats-score" element={<AtsScoreChecker />} />
                <Route path="jd-match" element={<JdMatcher />} />
                <Route path="resume-rewriter" element={<ResumeSectionRewriterPage />} />
                <Route path="bullet-rewriter" element={<ResumeSectionRewriterPage />} />
                <Route path="gap-analysis" element={<GapAnalysisPage />} />
                <Route path="career-gps" element={<CareerGPSPage />} />
                <Route path="portfolio" element={<PortfolioIntelligence />} />
                <Route path="salary-predictor" element={<SalaryPredictor />} />

                {/* Interview */}
                <Route path="mnc-interview" element={<MNCInterviewStudioPage />} />
                <Route path="interview-studio" element={<MNCInterviewStudioPage />} />
                <Route path="assessment" element={<AssessmentRoomPage />} />
                <Route path="interview" element={<InterviewPage />} />
                <Route path="coding-interview" element={<CodingInterviewPage />} />
                <Route path="voice-interview" element={<VoiceInterviewPage />} />
                <Route path="p2p-mock" element={<P2PMockPage />} />
                <Route path="company-profiles" element={<CompanyProfilesPage />} />
                <Route path="cognitive-load" element={<CognitiveLoadMonitorPage />} />

                {/* Learning */}
                <Route path="syllabus-optimizer" element={<SyllabusOptimizer />} />
                <Route path="micro-internships" element={<MicroInternships />} />
                <Route path="skill-decay" element={<SkillDecayPage />} />
                <Route path="prep-calendar" element={<CalendarExportPage />} />
                <Route path="rebirth" element={<CareerRebirth />} />
                <Route path="language-bridge" element={<LanguageBridge />} />
                <Route path="highschool" element={<HighSchoolTrajectory />} />

                {/* Intelligence */}
                <Route path="psychometric-dna" element={<PsychometricDNAPage />} />
                <Route path="market-intelligence" element={<MarketIntelligencePage />} />
                <Route path="benchmarks" element={<BenchmarkReportPage />} />
                <Route path="credential" element={<MyCredential />} />
                <Route path="passport" element={<TalentPassport />} />

                {/* Gamification */}
                <Route path="gamification" element={<GamificationPage />} />
                <Route path="leaderboard" element={<LeaderboardPage />} />

                {/* Jobs & Mentors */}
                <Route path="opportunities" element={<OpportunityHub />} />
                <Route path="applications" element={<SmartApplyTracker />} />
                <Route path="offer-comparison" element={<OfferComparator />} />
                <Route path="offer-negotiator" element={<OfferNegotiatorPage />} />
                <Route path="routing-intelligence" element={<ApplicationIntelligence />} />
                <Route path="mentors" element={<MentorNetwork />} />
                <Route path="truth" element={<TruthDatabase />} />
                <Route path="employer-truth" element={<EmployerTruthScore />} />

                {/* Admin */}
                <Route path="college-admin" element={<CollegeAdminDashboard />} />
                <Route path="parent-view" element={<ParentDashboard />} />
                <Route path="recruiter" element={<RecruiterIntelligencePage />} />
                <Route path="recruiter-dashboard" element={<RecruiterIntelligencePage />} />
                <Route path="workforce" element={<WorkforceIntelligencePage />} />
                <Route path="workforce-intelligence" element={<WorkforceIntelligencePage />} />

                {/* Account */}
                <Route path="billing" element={<PricingPage />} />
                <Route path="settings" element={<SettingsPage />} />

                {/* NEW — Session 32: Community & Resume Builder */}
                <Route path="community" element={<CommunityHub />} />
                <Route path="resume-builder" element={<ResumeBuilder />} />

                {/* Last Mile Sessions 32 - 41 */}
                <Route path="offline-practice" element={<OfflinePractice />} />
                <Route path="faculty-dashboard" element={<FacultyDashboard />} />
                <Route path="earn-to-learn" element={<EarnToLearn />} />
                <Route path="parent-connect" element={<ParentConnect />} />
                <Route path="cohort-mode" element={<CohortMode />} />
                <Route path="vernacular-library" element={<VernacularLibrary />} />
                <Route path="lab-mode" element={<LabMode />} />
                <Route path="war-room" element={<RecruiterWarRoom />} />

                <Route index element={<Navigate to="dashboard" replace />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
      <Toaster theme="dark" richColors position="top-right" />
    </QueryClientProvider>
  );
}
