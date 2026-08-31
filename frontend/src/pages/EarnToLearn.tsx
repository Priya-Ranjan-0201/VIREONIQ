import React, { useState, useEffect } from 'react';
import { Award, Zap, BookOpen, Share2, Bug, Check, Loader2, Lock } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';

// Premium Gate wrapper component for premium-locked views
export const PremiumGate: React.FC<{ children: React.ReactNode; featureName: string }> = ({ children, featureName }) => {
  const [hasAccess, setHasAccess] = useState<boolean | null>(null);

  useEffect(() => {
    api.get(`/earn/check-access?feature=${featureName}`)
      .then((res) => setHasAccess(res.data.access))
      .catch(() => setHasAccess(false));
  }, [featureName]);

  if (hasAccess === null) {
    return (
      <div className="flex justify-center items-center min-h-[40vh]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (!hasAccess) {
    return (
      <div className="glass-panel p-8 rounded-3xl text-center space-y-6 max-w-lg mx-auto my-12 animate-in fade-in zoom-in duration-300">
        <div className="w-16 h-16 bg-amber-500/10 text-amber-400 rounded-full flex items-center justify-center mx-auto border border-amber-500/20">
          <Lock className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h3 className="text-xl font-bold text-white">Premium Feature Locked</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            Access to this premium feature is restricted. Earn free days of premium access by contributing to the PlaceIQ student community.
          </p>
        </div>
        <button
          onClick={() => window.location.href = '/app/earn-to-learn'}
          className="px-6 py-3 bg-primary hover:bg-primary-hover text-slate-950 font-bold rounded-2xl text-xs transition"
        >
          Explore Earn-to-Learn Portal
        </button>
      </div>
    );
  }

  return <>{children}</>;
};

interface PremiumStatus {
  is_premium: boolean;
  premium_until: string | null;
  source: string;
  lifetime_earned_days: number;
  ledger_this_month: {
    [key: string]: {
      completed: number;
      max: number;
      days_earned: number;
    };
  };
}

export const EarnToLearn = () => {
  const [status, setStatus] = useState<PremiumStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [submitting, setSubmitting] = useState<string | null>(null);

  // Form states for content contribution
  const [translationText, setTranslationText] = useState('');
  const [targetLang, setTargetLang] = useState('hi'); // Hindi fallback
  const [conceptKey, setConceptKey] = useState('recursion');

  useEffect(() => {
    fetchPremiumStatus();
  }, []);

  const fetchPremiumStatus = async () => {
    try {
      const res = await api.get('/earn/my-status');
      setStatus(res.data);
    } catch (e) {
      toast.error('Failed to retrieve premium ledger.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitContent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!translationText.trim()) return;

    setSubmitting('translation');
    try {
      await api.post('/earn/submit-vernacular-content', {
        content_type: 'translation',
        content_text: translationText,
        target_language: targetLang
      });
      toast.success('Translation submitted to review queue! Approved contributions yield 5-10 Premium Days.');
      setTranslationText('');
      fetchPremiumStatus();
    } catch (e) {
      toast.error('Failed to submit contribution.');
    } finally {
      setSubmitting(null);
    }
  };

  const triggerMockContribution = async (type: string) => {
    setSubmitting(type);
    try {
      // Mock immediately credited contribution types
      await api.post('/earn/mock-immediate-contribution', { contribution_type: type });
      toast.success('Contribution recorded immediately! Premium status updated.');
      fetchPremiumStatus();
    } catch (e) {
      toast.error('Failed to record contribution.');
    } finally {
      setSubmitting(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
          Earn-to-Learn Economy
        </h2>
        <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
          Unlock Premium features by contributing interview insights, translations, and helping peers
        </p>
      </header>

      {/* Premium Status Card */}
      <div className="glass-panel p-6 rounded-3xl grid md:grid-cols-3 gap-6 items-center">
        <div className="space-y-2 md:col-span-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wider bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-lg">
              {status?.is_premium ? 'Premium Active' : 'Basic Tier'}
            </span>
            <span className="text-slate-400 text-xs">
              Lifetime Earned: <strong className="text-white">{status?.lifetime_earned_days || 0} days</strong>
            </span>
          </div>
          <h3 className="text-xl font-bold text-white">
            {status?.is_premium
              ? `Unlocked until ${status.premium_until ? new Date(status.premium_until).toLocaleDateString() : 'Forever'}`
              : 'Unlock Premium Features Free'}
          </h3>
          <p className="text-slate-400 text-xs max-w-xl">
            Premium users get access to unlimited AI sessions, advanced psychometric DNA analysis, priority mentor matchmaking, and more.
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex flex-col items-center justify-center text-center">
          <Award className="w-8 h-8 text-primary mb-2" />
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Tier Source</span>
          <span className="text-sm font-extrabold text-white mt-1 uppercase tracking-wider">
            {status?.source || 'Basic'}
          </span>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Contribution Portal */}
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Ecosystem Contributions</h3>

          {/* Translation form */}
          <form onSubmit={handleSubmitContent} className="space-y-4 bg-slate-900/50 p-4 border border-slate-850 rounded-2xl">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Submit Vernacular Translation</span>
              <p className="text-slate-500 text-[10px] mt-0.5">Help peers by translating concepts (DSA/Design) into local languages.</p>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Concept</label>
                <select
                  value={conceptKey}
                  onChange={(e) => setConceptKey(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white"
                >
                  <option value="recursion">Recursion</option>
                  <option value="dynamic_programming">Dynamic Programming</option>
                  <option value="locks">Optimistic/Pessimistic Locking</option>
                  <option value="db_indexing">Database Indexing</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Language</label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white"
                >
                  <option value="hi">Hindi</option>
                  <option value="te">Telugu</option>
                  <option value="ta">Tamil</option>
                  <option value="kn">Kannada</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Local Analogy or Explanation</label>
              <textarea
                rows={3}
                placeholder="Explain this concept using a local story or everyday analogy..."
                value={translationText}
                onChange={(e) => setTranslationText(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={submitting === 'translation' || !translationText.trim()}
              className="w-full py-2 bg-primary hover:bg-primary-hover text-slate-950 font-bold rounded-xl text-xs transition flex justify-center items-center gap-2"
            >
              {submitting === 'translation' && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              Submit to Review Queue
            </button>
          </form>

          {/* Other tasks list */}
          <div className="space-y-3">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Immediate Credit Tasks</span>
            
            <div className="flex justify-between items-center p-3.5 bg-slate-950/50 border border-slate-850 rounded-xl">
              <div>
                <h4 className="text-xs font-bold text-white">Attend Peer Mock (Interviewer)</h4>
                <p className="text-[10px] text-slate-500 mt-0.5">Help cohort peers by taking mock sessions (+3 Premium Days)</p>
              </div>
              <button
                onClick={() => triggerMockContribution('mentor_session_given')}
                disabled={!!submitting}
                className="px-3 py-1.5 bg-slate-850 hover:bg-slate-800 text-xs font-bold text-white rounded-xl transition"
              >
                Log Mock
              </button>
            </div>

            <div className="flex justify-between items-center p-3.5 bg-slate-950/50 border border-slate-850 rounded-xl">
              <div>
                <h4 className="text-xs font-bold text-white">Complete Study Group Meeting</h4>
                <p className="text-[10px] text-slate-500 mt-0.5">Finish peer practice session scheduled in cohort (+3 Premium Days)</p>
              </div>
              <button
                onClick={() => triggerMockContribution('study_group_completion')}
                disabled={!!submitting}
                className="px-3 py-1.5 bg-slate-850 hover:bg-slate-800 text-xs font-bold text-white rounded-xl transition"
              >
                Log Meeting
              </button>
            </div>
          </div>
        </div>

        {/* Limits & Ledger Tracker */}
        <div className="glass-panel p-6 rounded-3xl space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-semibold">Monthly Activity Caps</h3>
          {status?.ledger_this_month ? (
            <div className="space-y-4">
              {Object.entries(status.ledger_this_month).map(([key, item]) => {
                const label = key.replace(/_/g, ' ');
                const progressPercent = Math.min((item.completed / item.max) * 100, 100);
                return (
                  <div key={key} className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-white capitalize font-medium">{label}</span>
                      <span className="text-slate-400 font-bold">
                        {item.completed} / {item.max} ({item.days_earned}d earned)
                      </span>
                    </div>
                    <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-850">
                      <div
                        className="bg-primary h-full rounded-full transition-all duration-500"
                        style={{ width: `${progressPercent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-slate-500 text-xs">No active ledger tracked.</p>
          )}
        </div>
      </div>
    </div>
  );
};
export default EarnToLearn;
