import React, { useState, useEffect } from 'react';
import { Download, Wifi, WifiOff, RefreshCw, Play, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';
import axios from 'axios';
import {
  saveOfflineBundle,
  getOfflineBundle,
  queueOfflineSession,
  getPendingSessions,
  syncOfflineSessions
} from '@/lib/offlineEngine';
import type { OfflineSession } from '@/lib/offlineEngine';

export const OfflinePractice = () => {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [cachedBundles, setCachedBundles] = useState<{ [key: string]: boolean }>({});
  const [pendingSessionsCount, setPendingSessionsCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Active Session state
  const [activeSession, setActiveSession] = useState<{
    role: string;
    questions: any[];
    currentIdx: number;
    answers: { question_id: string; answer_text: string; duration_s: number; timestamp: string }[];
    startTime: number;
  } | null>(null);
  
  const [currentAnswer, setCurrentAnswer] = useState('');

  const roles = [
    { key: 'software_engineer', name: 'Software Engineer' },
    { key: 'frontend_developer', name: 'Frontend Developer' },
    { key: 'backend_developer', name: 'Backend Developer' },
    { key: 'product_manager', name: 'Product Manager' }
  ];

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    checkCachedBundles();
    updatePendingCount();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const checkCachedBundles = async () => {
    const status: { [key: string]: boolean } = {};
    for (const role of roles) {
      const bundle = await getOfflineBundle(role.key);
      status[role.key] = !!bundle;
    }
    setCachedBundles(status);
  };

  const updatePendingCount = async () => {
    const pending = await getPendingSessions();
    setPendingSessionsCount(pending.length);
  };

  const downloadBundle = async (roleKey: string) => {
    if (!isOnline) {
      toast.error('You must be online to download offline question bundles.');
      return;
    }
    setDownloading(roleKey);
    try {
      // Mock question generator API or static bundles fallback
      const response = await api.get(`/offline/bundle/${roleKey}`);
      if (response.data && response.data.download_url) {
        const bundleRes = await axios.get(response.data.download_url);
        if (bundleRes.data && Array.isArray(bundleRes.data.questions)) {
          await saveOfflineBundle(roleKey, bundleRes.data.questions);
          toast.success(`Offline bundle for ${roleKey} downloaded successfully!`);
          checkCachedBundles();
        } else {
          throw new Error('Invalid questions structure in bundle file');
        }
      } else {
        throw new Error('Invalid bundle metadata response');
      }
    } catch (e) {
      console.error(e);
      toast.error(`Failed to download bundle for ${roleKey}. Falling back to default static bundle.`);
      
      // Fallback local static questions mock
      const mockQuestions = [
        {
          id: 'q1',
          question_text: 'Explain the difference between optimistic locking and pessimistic locking database mechanisms.',
          rubric: 'Looking for isolation levels, lock types, write contention scenarios, and performance trade-offs.',
          key_points: ['Pessimistic: locks records immediately', 'Optimistic: checks version column during commit', 'Optimistic is better for high-read low-write contention']
        },
        {
          id: 'q2',
          question_text: 'What are the main trade-offs when choosing between a microservices architecture and a monolithic architecture?',
          rubric: 'Should mention operational complexity, deployment velocity, network overhead, and domain partitioning.',
          key_points: ['Monolith: single deployment, simple latency', 'Microservices: autonomous scaling, high operational overhead', 'Conway\'s Law alignment']
        },
        {
          id: 'q3',
          question_text: 'How does Redis achieve low latency, and what are its persistence strategies (AOF and RDB)?',
          rubric: 'Should cover in-memory storage, single-threaded event loop, snapshotting, and append-only logs.',
          key_points: ['In-memory operation', 'RDB snapshot: point-in-time backup', 'AOF: log of all write operations']
        }
      ];
      await saveOfflineBundle(roleKey, mockQuestions);
      checkCachedBundles();
    } finally {
      setDownloading(null);
    }
  };

  const triggerSync = async () => {
    if (!isOnline) {
      toast.error('Cannot sync while offline.');
      return;
    }
    setSyncing(true);
    const result = await syncOfflineSessions();
    setSyncing(false);
    if (result.success) {
      if (result.syncedCount > 0) {
        toast.success(`Successfully synchronized ${result.syncedCount} mock sessions!`);
      } else {
        toast.info('No pending sessions to synchronize.');
      }
      updatePendingCount();
    } else {
      toast.error('Synchronization failed. Will retry automatically when online.');
    }
  };

  const startSession = async (roleKey: string) => {
    const bundle = await getOfflineBundle(roleKey);
    if (!bundle) {
      toast.error('Please download the offline bundle first.');
      return;
    }
    setActiveSession({
      role: roleKey,
      questions: bundle.questions,
      currentIdx: 0,
      answers: [],
      startTime: Date.now()
    });
  };

  const handleNextQuestion = () => {
    if (!activeSession) return;
    if (!currentAnswer.trim()) {
      toast.error('Please enter an answer to proceed.');
      return;
    }

    const duration = Math.round((Date.now() - activeSession.startTime) / 1000);
    const currentQ = activeSession.questions[activeSession.currentIdx];

    const updatedAnswers = [
      ...activeSession.answers,
      {
        question_id: currentQ.id,
        answer_text: currentAnswer,
        duration_s: duration,
        timestamp: new Date().toISOString()
      }
    ];

    if (activeSession.currentIdx + 1 < activeSession.questions.length) {
      setActiveSession({
        ...activeSession,
        currentIdx: activeSession.currentIdx + 1,
        answers: updatedAnswers,
        startTime: Date.now()
      });
      setCurrentAnswer('');
    } else {
      // End session
      const finalSession: OfflineSession = {
        id: Math.random().toString(36).substring(2, 11),
        role_category: activeSession.role,
        answers: updatedAnswers,
        completed_at: new Date().toISOString()
      };
      
      queueOfflineSession(finalSession).then(() => {
        toast.success('Offline session completed and saved to offline queue!');
        setActiveSession(null);
        setCurrentAnswer('');
        updatePendingCount();
        if (isOnline) {
          triggerSync();
        }
      });
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
            Offline-First Practice Engine
          </h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
            Train without Internet. Auto-sync, NLP rubrics, and local simulation
          </p>
        </div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-2xl border ${
          isOnline ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
        }`}>
          {isOnline ? <Wifi className="w-5 h-5" /> : <WifiOff className="w-5 h-5" />}
          <span className="text-xs font-bold uppercase tracking-wider">{isOnline ? 'Online' : 'Offline'}</span>
        </div>
      </header>

      {pendingSessionsCount > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/20 p-5 rounded-3xl flex justify-between items-center">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-amber-400 w-6 h-6" />
            <div>
              <h4 className="font-bold text-white text-sm">Offline Sessions Queued</h4>
              <p className="text-slate-400 text-xs mt-1">
                You have {pendingSessionsCount} practice sessions saved locally waiting to sync.
              </p>
            </div>
          </div>
          <button
            onClick={triggerSync}
            disabled={syncing || !isOnline}
            className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold rounded-2xl text-xs transition"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            Sync Now
          </button>
        </div>
      )}

      {!activeSession ? (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Bundle Downloader */}
          <div className="glass-panel p-6 rounded-3xl space-y-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Download Question Bundles</h3>
            <div className="space-y-4">
              {roles.map((role) => (
                <div key={role.key} className="flex justify-between items-center p-4 bg-slate-900/50 border border-slate-800 rounded-2xl">
                  <div>
                    <h4 className="text-sm font-semibold text-white">{role.name}</h4>
                    <span className="text-xs text-slate-400 mt-1 block">
                      {cachedBundles[role.key] ? '✅ Offline Available' : '📥 Download Required'}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => downloadBundle(role.key)}
                      disabled={downloading === role.key || !isOnline}
                      className="p-2.5 bg-slate-850 hover:bg-slate-800 disabled:opacity-50 text-slate-300 rounded-xl transition border border-slate-800"
                    >
                      <Download className={`w-4 h-4 ${downloading === role.key ? 'animate-bounce' : ''}`} />
                    </button>
                    {cachedBundles[role.key] && (
                      <button
                        onClick={() => startSession(role.key)}
                        className="flex items-center gap-1.5 px-4 py-2 bg-primary/10 border border-primary/25 text-primary hover:bg-primary/20 text-xs font-bold rounded-xl transition"
                      >
                        <Play className="w-3.5 h-3.5" /> Start
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Guide */}
          <div className="glass-panel p-6 rounded-3xl space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Offline Guide</h3>
              <ul className="space-y-3 text-xs text-slate-400">
                <li className="flex gap-2">
                  <CheckCircle className="text-primary w-4 h-4 shrink-0" />
                  <span>Download bundles when you have stable internet (e.g., library or hostel).</span>
                </li>
                <li className="flex gap-2">
                  <CheckCircle className="text-primary w-4 h-4 shrink-0" />
                  <span>Open PlaceIQ anytime, select a downloaded role, and practice without network requirements.</span>
                </li>
                <li className="flex gap-2">
                  <CheckCircle className="text-primary w-4 h-4 shrink-0" />
                  <span>Your answers will be stored securely on your browser using IndexedDB.</span>
                </li>
                <li className="flex gap-2">
                  <CheckCircle className="text-primary w-4 h-4 shrink-0" />
                  <span>Once connected, your sessions automatically sync. The AI will evaluate them and reward XP!</span>
                </li>
              </ul>
            </div>
            <div className="pt-4 border-t border-slate-850">
              <div className="flex items-center justify-between text-xs font-medium text-slate-400">
                <span>Cached bundles storage:</span>
                <span className="text-white font-bold">IndexedDB Storage</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Active Practice Interface */
        <div className="glass-panel p-8 rounded-3xl space-y-8">
          <div className="flex justify-between items-center border-b border-slate-850 pb-5">
            <div>
              <span className="text-xs font-bold text-primary uppercase tracking-wider">
                Offline Simulation mode ({roles.find(r => r.key === activeSession.role)?.name})
              </span>
              <h3 className="text-lg font-bold text-white mt-1">
                Question {activeSession.currentIdx + 1} of {activeSession.questions.length}
              </h3>
            </div>
            <button
              onClick={() => setActiveSession(null)}
              className="text-xs text-slate-400 hover:text-white transition"
            >
              Exit Practice
            </button>
          </div>

          <div className="space-y-4">
            <p className="text-white text-base leading-relaxed font-semibold">
              {activeSession.questions[activeSession.currentIdx].question_text}
            </p>
            {activeSession.questions[activeSession.currentIdx].rubric && (
              <div className="bg-slate-900/50 p-4 border border-slate-800 rounded-2xl">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">Evaluation Focus</span>
                <p className="text-slate-400 text-xs leading-relaxed">
                  {activeSession.questions[activeSession.currentIdx].rubric}
                </p>
              </div>
            )}
          </div>

          <div className="space-y-3">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Your Response</label>
            <textarea
              rows={6}
              placeholder="Type your detailed architectural or algorithm strategy here..."
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              className="w-full p-4 bg-slate-950 border border-slate-800 focus:border-primary rounded-2xl text-white outline-none text-sm leading-relaxed"
            />
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-850">
            <button
              onClick={handleNextQuestion}
              className="flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primary-hover text-slate-950 font-bold rounded-2xl text-sm transition"
            >
              {activeSession.currentIdx + 1 === activeSession.questions.length ? 'Finish & Save' : 'Next Question'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
export default OfflinePractice;
