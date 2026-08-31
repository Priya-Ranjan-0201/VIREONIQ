import React, { useState, useEffect } from 'react';
import {
  Brain,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowRight,
  ShieldCheck,
  Zap,
  Code2,
  Terminal,
  RotateCcw,
  Sparkles,
  Award,
  Layers,
  ChevronRight
} from 'lucide-react';
import { careerIntelligenceApi } from '@/api/careerIntelligenceApi';
import type { AssessmentQuestionData, AssessmentResultData } from '@/api/careerIntelligenceApi';

export const AssessmentRoomPage: React.FC = () => {
  const [targetRole, setTargetRole] = useState<string>('Backend Engineer');
  const [mode, setMode] = useState<'ASSESSMENT' | 'PRACTICE'>('ASSESSMENT');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<AssessmentQuestionData | null>(null);
  const [questionIndex, setQuestionIndex] = useState<number>(0);
  const [codeSubmission, setCodeSubmission] = useState<string>('');
  const [textSubmission, setTextSubmission] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [lastFeedback, setLastFeedback] = useState<any>(null);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResultData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const startSession = async () => {
    setLoading(true);
    setAssessmentResult(null);
    setLastFeedback(null);
    try {
      const data = await careerIntelligenceApi.startAssessmentSession(targetRole, mode);
      setSessionId(data.session_id);
      setQuestionIndex(1);
      const firstQ = await careerIntelligenceApi.getNextAssessmentQuestion(data.session_id);
      setCurrentQuestion(firstQ);
      if (firstQ.starter_code) {
        setCodeSubmission(firstQ.starter_code);
      } else {
        setCodeSubmission('');
      }
      setTextSubmission('');
    } catch (err) {
      console.error('Failed to start assessment session', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNextOrSubmit = async () => {
    if (!sessionId || !currentQuestion) return;
    setIsSubmitting(true);
    try {
      const resp = await careerIntelligenceApi.submitAssessmentResponse(
        sessionId,
        currentQuestion.question_id,
        {
          code_submission: codeSubmission,
          response_text: textSubmission,
          duration_seconds: 45.0
        }
      );
      setLastFeedback(resp);

      // Load next question
      const nextQ = await careerIntelligenceApi.getNextAssessmentQuestion(sessionId);
      if (nextQ.status === 'ALL_QUESTIONS_COMPLETED' || !nextQ.question_id) {
        // Complete session
        const finalData = await careerIntelligenceApi.completeAssessmentSession(sessionId);
        setAssessmentResult(finalData);
        setCurrentQuestion(null);
      } else {
        setCurrentQuestion(nextQ);
        setQuestionIndex(prev => prev + 1);
        if (nextQ.starter_code) {
          setCodeSubmission(nextQ.starter_code);
        } else {
          setCodeSubmission('');
        }
        setTextSubmission('');
      }
    } catch (err) {
      console.error('Failed to submit question response', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-sm uppercase tracking-wider mb-1">
              <Brain className="w-4 h-4" />
              Adaptive Capability Assessment Engine v4.0.0
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Role Assessment & Coding Sandbox
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Grounded, adaptive evaluation measuring actual engineering capability across code, system design, and communication.
            </p>
          </div>

          {!sessionId && (
            <div className="flex items-center gap-3">
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2"
              >
                <option value="Backend Engineer">Backend Engineer</option>
                <option value="Full Stack Engineer">Full Stack Engineer</option>
                <option value="AI/ML Engineer">AI/ML Engineer</option>
              </select>

              <div className="flex bg-slate-900 border border-slate-700 rounded-lg p-1 text-xs font-semibold">
                <button
                  onClick={() => setMode('ASSESSMENT')}
                  className={`px-3 py-1.5 rounded-md transition ${mode === 'ASSESSMENT' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  ASSESSMENT
                </button>
                <button
                  onClick={() => setMode('PRACTICE')}
                  className={`px-3 py-1.5 rounded-md transition ${mode === 'PRACTICE' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  PRACTICE
                </button>
              </div>

              <button
                onClick={startSession}
                disabled={loading}
                className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition shadow-lg shadow-indigo-500/20"
              >
                <Play className="w-4 h-4 fill-white" />
                Start Challenge
              </button>
            </div>
          )}
        </div>

        {/* Live Active Question View */}
        {sessionId && currentQuestion && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Prompt Column */}
            <div className="lg:col-span-5 space-y-4">
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono px-2.5 py-1 rounded bg-indigo-950/80 border border-indigo-800/60 text-indigo-300 font-semibold">
                    Question {questionIndex} • {currentQuestion.competency}
                  </span>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {currentQuestion.difficulty}
                  </span>
                </div>

                <h3 className="text-base font-semibold text-slate-100">
                  {currentQuestion.prompt}
                </h3>

                {currentQuestion.has_hidden_tests && (
                  <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 rounded-lg p-2.5">
                    <ShieldCheck className="w-4 h-4 shrink-0" />
                    <span>Includes 4 hidden validation test suites (AST & boundary checks).</span>
                  </div>
                )}
              </div>

              {/* Real-Time Last Feedback Snippet */}
              {lastFeedback && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <span>Previous Question Evaluated:</span>
                    <span className="text-indigo-400">{lastFeedback.evaluated_score}/100</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    {lastFeedback.feedback_preview}
                  </p>
                  <div className="text-[11px] font-mono text-slate-500">
                    Next Adaptive Tier: {lastFeedback.adaptive_difficulty_next}
                  </div>
                </div>
              )}
            </div>

            {/* Right Editor / Input Column */}
            <div className="lg:col-span-7 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                    {currentQuestion.question_type === 'CODING_CHALLENGE' ? (
                      <>
                        <Code2 className="w-4 h-4 text-indigo-400" />
                        <span>Python Runtime / Sandbox</span>
                      </>
                    ) : (
                      <>
                        <Terminal className="w-4 h-4 text-violet-400" />
                        <span>Structured Response Terminal</span>
                      </>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 font-mono">
                    Auto-Telemetry Active
                  </span>
                </div>

                {currentQuestion.question_type === 'CODING_CHALLENGE' ? (
                  <textarea
                    value={codeSubmission}
                    onChange={(e) => setCodeSubmission(e.target.value)}
                    rows={12}
                    placeholder="Write Python solution here..."
                    className="w-full bg-slate-950 font-mono text-sm text-emerald-300 border border-slate-800 rounded-lg p-4 focus:outline-none focus:border-indigo-500 resize-none leading-relaxed"
                  />
                ) : (
                  <textarea
                    value={textSubmission}
                    onChange={(e) => setTextSubmission(e.target.value)}
                    rows={12}
                    placeholder="Provide structured reasoning, architecture, or STAR explanation..."
                    className="w-full bg-slate-950 font-sans text-sm text-slate-200 border border-slate-800 rounded-lg p-4 focus:outline-none focus:border-indigo-500 resize-none leading-relaxed"
                  />
                )}

                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs text-slate-500">
                    Answers are evaluated against pre-defined blueprints with zero LLM hallucination.
                  </span>
                  <button
                    onClick={handleNextOrSubmit}
                    disabled={isSubmitting}
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg text-sm transition"
                  >
                    {isSubmitting ? 'Evaluating AST & Rubric...' : 'Submit & Continue'}
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Final Assessment Result View */}
        {assessmentResult && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6">
            <div className="flex items-center gap-3 text-emerald-400">
              <Award className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold text-white">Assessment Complete</h2>
                <p className="text-slate-400 text-sm">
                  Generated {assessmentResult.evidence_created_count} verified evidence atoms into your Career Digital Twin.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-5">
                <span className="text-xs text-slate-500 uppercase font-mono">Overall Assessment Score</span>
                <div className="text-3xl font-bold text-indigo-400 mt-1">{assessmentResult.overall_score}/100</div>
                <div className="text-xs text-slate-400 mt-1 font-mono">Mode: {assessmentResult.mode}</div>
              </div>

              <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-5">
                <span className="text-xs text-slate-500 uppercase font-mono">Updated Career Readiness</span>
                <div className="text-3xl font-bold text-emerald-400 mt-1">{assessmentResult.recalculated_career_readiness}/100</div>
                <div className="text-xs text-slate-400 mt-1">CRI 2.0 Recalibrated</div>
              </div>

              <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-5">
                <span className="text-xs text-slate-500 uppercase font-mono">Evidence Atoms Created</span>
                <div className="text-3xl font-bold text-violet-400 mt-1">+{assessmentResult.evidence_created_count}</div>
                <div className="text-xs text-slate-400 mt-1">Elevated to ASSESSED tier</div>
              </div>
            </div>

            {/* Recalibrated Next Best Action */}
            {assessmentResult.highest_roi_next_action && (
              <div className="bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/30 rounded-xl p-6 space-y-3">
                <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 uppercase tracking-wide">
                  <Sparkles className="w-4 h-4" />
                  Recalibrated Next Best Career Action (Post-Assessment)
                </div>
                <h4 className="text-lg font-bold text-white">
                  {assessmentResult.highest_roi_next_action.title}
                </h4>
                <p className="text-sm text-slate-300">
                  {assessmentResult.highest_roi_next_action.why_this_action}
                </p>
                <div className="flex flex-wrap items-center gap-3 pt-2 text-xs">
                  <span className="bg-slate-800 px-3 py-1 rounded text-slate-300 font-mono">
                    Effort: {assessmentResult.highest_roi_next_action.estimated_effort_hours}
                  </span>
                  <span className="bg-emerald-950/60 border border-emerald-800/50 text-emerald-300 px-3 py-1 rounded font-mono">
                    Projected Delta: {assessmentResult.highest_roi_next_action.preview.projected_delta}
                  </span>
                </div>
              </div>
            )}

            <div className="flex justify-end pt-4">
              <button
                onClick={() => { setSessionId(null); setAssessmentResult(null); }}
                className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-5 py-2.5 rounded-lg text-sm transition"
              >
                <RotateCcw className="w-4 h-4" />
                Start New Assessment Session
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
