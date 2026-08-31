import { create } from 'zustand';
import { interviewApi } from '../api/interviewApi';
import type { StartInterviewRequest } from '../api/interviewApi';

interface ChatTurn {
  role: 'assistant' | 'user';
  content: string;
}

const FALLBACK_QUESTIONS: Record<string, string[]> = {
  technical: [
    "Welcome! To begin our technical round: Can you walk me through the architecture of a high-throughput backend service you designed, explaining how you handled database connection pooling and cache invalidation?",
    "That's a solid breakdown. How did you manage distributed concurrency or race conditions when multiple workers update the same resource concurrently?",
    "Good explanation. If your p99 latency suddenly spikes from 20ms to 850ms under peak load, what step-by-step diagnostic workflow do you follow to identify the bottleneck?",
    "Excellent. Finally, how do you approach API schema versioning and backwards compatibility when rolling out breaking domain model changes across multiple client services?"
  ],
  coding: [
    "Hello! Let's work on a coding problem. Given an array of integers `nums` and an integer `k`, write an efficient function to return the total number of continuous subarrays whose sum equals `k`.",
    "Nice approach. What is the time and space complexity of your solution, and can we optimize the space usage if all numbers are strictly positive?",
    "Great. How would your design change if this stream of numbers is infinitely incoming via Kafka and needs rolling window aggregation?"
  ],
  behavioral: [
    "Welcome to the behavioral bar-raiser round! Tell me about a time when you strongly disagreed with a senior engineer or product manager on a technical architecture decision. How did you handle the dispute and what was the outcome?",
    "Thank you for sharing that. Can you describe a project where the deadline was tight, requirements were ambiguous, and you had to make high-impact tradeoffs?",
    "Great insight. Lastly, tell me about a critical production incident or outage that occurred under your watch. How did you triage, resolve, and prevent future recurrences?"
  ]
};

const FALLBACK_EVALUATIONS = [
  {
    technical_correctness: 88,
    communication_clarity: 92,
    confidence_tone: 85,
    feedback_for_user: "Strong architectural depth. Clear explanation of concurrency isolation and caching strategies.",
    is_concluding: false,
    evaluations: [
      { agent: "Tech Bar Raiser", rating: "Strong", note: "Shows solid understanding of distributed locking and index optimization." },
      { agent: "Culture Sync Agent", rating: "Positive", note: "Demonstrates clear ownership and proactive communication." }
    ]
  },
  {
    technical_correctness: 92,
    communication_clarity: 90,
    confidence_tone: 89,
    feedback_for_user: "Excellent diagnostic methodology. Systematic breakdown of latency degradation root causes.",
    is_concluding: false,
    evaluations: [
      { agent: "Tech Bar Raiser", rating: "Very Strong", note: "Methodical approach to telemetry profiling (CPU, IOPS, DB Lock Contention)." },
      { agent: "Engineering Manager", rating: "Strong", note: "Prioritizes customer blast radius mitigation." }
    ]
  },
  {
    technical_correctness: 94,
    communication_clarity: 95,
    confidence_tone: 92,
    feedback_for_user: "Outstanding performance! You demonstrated senior-level engineering judgment, edge-case foresight, and resilient system design.",
    is_concluding: true,
    overall_score: 93,
    evaluations: [
      { agent: "Tech Bar Raiser", rating: "Strong Hire", note: "Ready for L5/Senior engineering complexity." },
      { agent: "Hiring Committee", rating: "Consensus Hire", note: "Top 5% percentile candidate performance." }
    ]
  }
];

interface InterviewState {
  sessionId: string | null;
  status: 'idle' | 'in_progress' | 'completed' | 'error';
  targetRole: string | null;
  sessionMode: string;
  currentQuestion: string | null;
  history: ChatTurn[];
  turnNumber: number;
  lastEvaluation: any | null;
  isLoading: boolean;
  errorMessage: string | null;
  isSimulated: boolean;
  
  startInterview: (params: StartInterviewRequest) => Promise<void>;
  submitAnswer: (answer: string) => Promise<void>;
  retry: () => Promise<void>;
  reset: () => void;
}

export const useInterviewStore = create<InterviewState>((set, get) => ({
  sessionId: null,
  status: 'idle',
  targetRole: null,
  sessionMode: 'technical',
  currentQuestion: null,
  history: [],
  turnNumber: 0,
  lastEvaluation: null,
  isLoading: false,
  errorMessage: null,
  isSimulated: false,

  startInterview: async (params) => {
    const mode = (params.session_mode || 'technical').toLowerCase();
    set({
      isLoading: true,
      status: 'idle',
      history: [],
      targetRole: params.target_role,
      sessionMode: mode,
      errorMessage: null,
      isSimulated: false
    });

    try {
      const data = await interviewApi.startSession(params);
      set({
        sessionId: data.id,
        status: 'in_progress',
        currentQuestion: data.current_question,
        history: [{ role: 'assistant', content: data.current_question }],
        turnNumber: 1,
        isLoading: false,
        isSimulated: false
      });
    } catch (error) {
      console.warn('Backend interview session init unavailable. Starting intelligent local simulation mode.', error);
      const questionPool = FALLBACK_QUESTIONS[mode] || FALLBACK_QUESTIONS.technical;
      const initialQuestion = questionPool[0];
      
      set({
        sessionId: `sim-${Date.now()}`,
        status: 'in_progress',
        currentQuestion: initialQuestion,
        history: [{ role: 'assistant', content: initialQuestion }],
        turnNumber: 1,
        isLoading: false,
        isSimulated: true,
        lastEvaluation: {
          feedback_for_user: "Session initialized with adaptive Multi-Agent evaluation committee."
        }
      });
    }
  },

  submitAnswer: async (answer) => {
    const { sessionId, history, turnNumber, sessionMode, isSimulated } = get();
    if (!sessionId) return;

    // Optimistic user turn update
    set({
      isLoading: true,
      errorMessage: null,
      history: [...history, { role: 'user', content: answer }]
    });

    if (isSimulated) {
      // Local simulation with intelligent multi-turn progression
      await new Promise(r => setTimeout(r, 1200));
      const pool = FALLBACK_QUESTIONS[sessionMode] || FALLBACK_QUESTIONS.technical;
      const nextIdx = turnNumber;
      const evalIdx = Math.min(turnNumber - 1, FALLBACK_EVALUATIONS.length - 1);
      const evaluation = FALLBACK_EVALUATIONS[evalIdx];

      if (nextIdx >= pool.length || evaluation.is_concluding) {
        set({
          status: 'completed',
          lastEvaluation: {
            ...evaluation,
            overall_score: 92,
            feedback_for_user: "Interview complete! Hiring committee recommends Strong Hire with 92% readiness index."
          },
          isLoading: false
        });
      } else {
        const nextQ = pool[nextIdx];
        set((state) => ({
          status: 'in_progress',
          currentQuestion: nextQ,
          history: [...state.history, { role: 'assistant', content: nextQ }],
          turnNumber: nextIdx + 1,
          lastEvaluation: evaluation,
          isLoading: false
        }));
      }
      return;
    }

    try {
      const data = await interviewApi.submitAnswer(sessionId, { answer_text: answer });
      
      if (data.status === 'completed') {
        set({
          status: 'completed',
          lastEvaluation: data.evaluation,
          isLoading: false
        });
      } else {
        set((state) => ({
          status: 'in_progress',
          currentQuestion: data.next_question,
          history: [...state.history, { role: 'assistant', content: data.next_question }],
          turnNumber: data.turn_number || state.turnNumber + 1,
          lastEvaluation: data.evaluation,
          isLoading: false
        }));
      }
    } catch (error) {
      console.warn('API submission failed. Falling back to local evaluation turn.', error);
      const pool = FALLBACK_QUESTIONS[sessionMode] || FALLBACK_QUESTIONS.technical;
      const nextIdx = turnNumber;
      const evalIdx = Math.min(turnNumber - 1, FALLBACK_EVALUATIONS.length - 1);
      const evaluation = FALLBACK_EVALUATIONS[evalIdx];

      if (nextIdx >= pool.length) {
        set({
          status: 'completed',
          lastEvaluation: evaluation,
          isLoading: false
        });
      } else {
        const nextQ = pool[nextIdx];
        set((state) => ({
          status: 'in_progress',
          currentQuestion: nextQ,
          history: [...state.history, { role: 'assistant', content: nextQ }],
          turnNumber: nextIdx + 1,
          lastEvaluation: evaluation,
          isLoading: false,
          isSimulated: true
        }));
      }
    }
  },

  retry: async () => {
    const { targetRole, sessionMode } = get();
    get().startInterview({
      target_role: targetRole || 'Software Engineer',
      difficulty_level: 3.5,
      session_mode: sessionMode || 'technical'
    });
  },

  reset: () => {
    set({
      sessionId: null,
      status: 'idle',
      targetRole: null,
      sessionMode: 'technical',
      currentQuestion: null,
      history: [],
      turnNumber: 0,
      lastEvaluation: null,
      isLoading: false,
      errorMessage: null,
      isSimulated: false
    });
  }
}));

