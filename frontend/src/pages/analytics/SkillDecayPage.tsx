import { useState, useEffect, useMemo } from 'react';
import {
  Brain,
  AlertTriangle,
  Clock,
  RefreshCw,
  CheckCircle2,
  Sparkles,
  Zap,
  TrendingUp,
  Sliders,
  Plus,
  X,
  HelpCircle,
  Award,
  ChevronRight,
  ShieldAlert,
  Calendar,
  History
} from 'lucide-react';
import { skillDecayApi, SkillDecayItem } from '@/api/skillDecayApi';
import { toast } from 'sonner';

// Authentic Question Bank for Spaced Repetition Flash-Recall
const PRACTICE_QUESTIONS: Record<string, { question: string; options: string[]; correctIdx: number; explanation: string }[]> = {
  'Dynamic Programming': [
    {
      question: 'What is the recurrence relation for the Coin Change problem (minimum coins to make amount A)?',
      options: [
        'dp[a] = min(dp[a - c] + 1) for all c in coins',
        'dp[a] = sum(dp[a - c]) for all c in coins',
        'dp[a] = max(dp[a - c]) for all c in coins',
        'dp[a] = dp[a - 1] + dp[a - 2]'
      ],
      correctIdx: 0,
      explanation: 'For minimum coins, we examine every valid coin c and take 1 + the optimal solution for the subproblem (a - c).'
    },
    {
      question: 'When is Tabulation (Bottom-Up) generally preferred over Memoization (Top-Down)?',
      options: [
        'To avoid call-stack overflow from deep recursion and improve cache locality',
        'When subproblems only need to be computed on-demand',
        'When solving tree-based recursive traversals',
        'When space complexity is strictly O(1)'
      ],
      correctIdx: 0,
      explanation: 'Bottom-up tabulation avoids recursion overhead and call-stack limits, often allowing iterative state-space compression.'
    }
  ],
  'System Design': [
    {
      question: 'Which partitioning strategy minimizes data movement when scaling a distributed cache cluster from N to N+1 nodes?',
      options: [
        'Consistent Hashing with Virtual Nodes',
        'Modulo Hashing (hash(key) % N)',
        'Round-Robin DNS routing',
        'Randomized Cache Partitioning'
      ],
      correctIdx: 0,
      explanation: 'Consistent hashing remaps only K/N keys on node addition/removal, preventing catastrophic cache invalidation.'
    },
    {
      question: 'In the CAP theorem, how does an AP system (e.g. Cassandra, DynamoDB) behave during a network partition?',
      options: [
        'Accepts writes and reads on all available nodes, resolving data divergence asynchronously (Eventual Consistency)',
        'Rejects all writes to protect strict serializability',
        'Halts all network traffic until partition heals',
        'Rolls back all uncommitted transactions'
      ],
      correctIdx: 0,
      explanation: 'AP systems prioritize Availability over linear consistency, allowing local partition reads and writes with eventual reconciliation.'
    }
  ],
  'Graph Algorithms': [
    {
      question: 'Which algorithm finds single-source shortest paths in a directed graph with negative edge weights (and detects negative cycles)?',
      options: [
        'Bellman-Ford Algorithm (O(V * E))',
        'Dijkstra\'s Algorithm with Min-Heap',
        'Breadth-First Search (BFS)',
        'Prim\'s Minimum Spanning Tree'
      ],
      correctIdx: 0,
      explanation: 'Dijkstra assumes non-negative weights. Bellman-Ford relaxes all edges V-1 times and detects negative cycles on the V-th iteration.'
    },
    {
      question: 'What is the time complexity of Dijkstra\'s algorithm using an adjacency list and a Binary Min-Heap priority queue?',
      options: [
        'O((V + E) log V)',
        'O(V^2)',
        'O(V * E)',
        'O(E log E + V^2)'
      ],
      correctIdx: 0,
      explanation: 'Each vertex is extracted once (O(V log V)) and each edge relaxation may update the heap (O(E log V)), yielding O((V + E) log V).'
    }
  ],
  'OS Concepts': [
    {
      question: 'Which of the following is NOT one of Coffman\'s four necessary conditions for Deadlock?',
      options: [
        'Preemption Allowed by the Scheduler',
        'Mutual Exclusion',
        'Hold and Wait',
        'Circular Wait'
      ],
      correctIdx: 0,
      explanation: 'Preemption being allowed actually PREVENTS deadlocks! The condition is "No Preemption" (resources cannot be forcibly taken).'
    },
    {
      question: 'What causes Thrashing in an operating system?',
      options: [
        'High page fault frequency causing the OS to spend more time swapping pages than executing instructions',
        'CPU overheating and throttling clock frequency',
        'Stack buffer overflow in user mode',
        'Deadlock between disk I/O and graphics memory'
      ],
      correctIdx: 0,
      explanation: 'Thrashing occurs when the working set exceeds physical RAM, causing continuous disk swapping and near-zero CPU throughput.'
    }
  ],
  'Networking': [
    {
      question: 'Why does the TCP connection termination handshake require the initiating host to stay in TIME_WAIT for 2 * MSL (Maximum Segment Lifetime)?',
      options: [
        'To ensure the final ACK is received by the peer and to allow lingering duplicate packets to expire in the network',
        'To negotiate encryption keys for the next session',
        'To calculate round-trip time jitter for congestion control',
        'To flush the hardware NIC buffer'
      ],
      correctIdx: 0,
      explanation: 'TIME_WAIT ensures the final ACK reaches the other end (retransmitting if lost) and prevents delayed packets from corrupting new connections.'
    },
    {
      question: 'Which DNS record type maps a domain name directly to an IPv6 address?',
      options: [
        'AAAA Record',
        'A Record',
        'CNAME Record',
        'MX Record'
      ],
      correctIdx: 0,
      explanation: 'A records map to 32-bit IPv4 addresses, while AAAA (quad-A) records map to 128-bit IPv6 addresses.'
    }
  ],
  'DBMS & SQL': [
    {
      question: 'Which ANSI SQL transaction isolation level prevents Dirty Reads and Non-Repeatable Reads, but may still permit Phantom Reads?',
      options: [
        'Repeatable Read',
        'Read Committed',
        'Serializable',
        'Read Uncommitted'
      ],
      correctIdx: 0,
      explanation: 'Repeatable Read locks read rows preventing modifications, but new range inserts (phantom rows) can still appear without range locks.'
    },
    {
      question: 'Why are B+ Trees preferred over Binary Search Trees or Hash Indexes for relational database indexing?',
      options: [
        'High fan-out minimizes disk I/O seeks and leaf node linked lists allow high-speed range queries',
        'Hash collisions never occur in B+ trees',
        'B+ trees require zero memory allocation',
        'B+ trees only support exact point lookups'
      ],
      correctIdx: 0,
      explanation: 'B+ Tree high branching factor matches disk block reads, and linked sequential leaf nodes make range scans (BETWEEN, >, <) extremely fast.'
    }
  ]
};

const INITIAL_SKILLS: SkillDecayItem[] = [
  { topic: 'Dynamic Programming', retention: 0.34, mastery: 0.85, stability_days: 12, days_since_practice: 18, alert: true, category: 'dsa' },
  { topic: 'System Design', retention: 0.52, mastery: 0.78, stability_days: 21, days_since_practice: 14, alert: false, category: 'architecture' },
  { topic: 'Graph Algorithms', retention: 0.28, mastery: 0.72, stability_days: 7, days_since_practice: 22, alert: true, category: 'dsa' },
  { topic: 'OS Concepts', retention: 0.65, mastery: 0.80, stability_days: 30, days_since_practice: 8, alert: false, category: 'core_cs' },
  { topic: 'DBMS & SQL', retention: 0.88, mastery: 0.92, stability_days: 45, days_since_practice: 3, alert: false, category: 'core_cs' },
  { topic: 'Networking', retention: 0.21, mastery: 0.61, stability_days: 5, days_since_practice: 30, alert: true, category: 'core_cs' },
];

const getRetentionColor = (r: number) => (r >= 0.7 ? '#10B981' : r >= 0.4 ? '#F59E0B' : '#EF4444');
const getRetentionLabel = (r: number) => (r >= 0.7 ? 'Strong' : r >= 0.4 ? 'Fading' : 'Critical');

export const SkillDecayPage = () => {
  const [skills, setSkills] = useState<SkillDecayItem[]>(INITIAL_SKILLS);
  const [timeTravelDays, setTimeTravelDays] = useState<number>(0);
  const [activePracticeTopic, setActivePracticeTopic] = useState<string | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [showExplanation, setShowExplanation] = useState<boolean>(false);
  const [isSubmittingPractice, setIsSubmittingPractice] = useState<boolean>(false);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [newTopicName, setNewTopicName] = useState<string>('');

  // Load from backend if available
  useEffect(() => {
    skillDecayApi
      .getSkillDecayStatus()
      .then((data) => {
        if (data && data.length > 0) {
          // Merge with any custom local properties
          setSkills((prev) => {
            const map = new Map(prev.map((s) => [s.topic, s]));
            data.forEach((d) => {
              const existing = map.get(d.topic);
              map.set(d.topic, {
                ...d,
                category: existing?.category || 'core_cs'
              });
            });
            return Array.from(map.values());
          });
        }
      })
      .catch((err) => {
        console.warn('Using calibrated Ebbinghaus memory model state:', err);
      });
  }, []);

  // Compute decayed retention with optional Ebbinghaus time travel simulation
  // Mathematical formula: R = M * e^(-(days + simulated_days) / S)
  const displayedSkills = useMemo(() => {
    return skills.map((skill) => {
      const effectiveDays = skill.days_since_practice + timeTravelDays;
      // Exponential Ebbinghaus decay
      const decayedRetention = skill.mastery * Math.exp(-effectiveDays / Math.max(1, skill.stability_days));
      const boundedRetention = Math.max(0.05, Math.min(1.0, decayedRetention));
      const alert = boundedRetention < 0.4;

      return {
        ...skill,
        effectiveDays,
        retention: boundedRetention,
        alert
      };
    });
  }, [skills, timeTravelDays]);

  const filteredSkills = useMemo(() => {
    if (filterCategory === 'all') return displayedSkills;
    return displayedSkills.filter((s) => s.category === filterCategory);
  }, [displayedSkills, filterCategory]);

  const criticals = useMemo(() => displayedSkills.filter((s) => s.alert), [displayedSkills]);

  // Overall memory health index (average percentage)
  const avgRetention = useMemo(() => {
    if (displayedSkills.length === 0) return 0;
    const total = displayedSkills.reduce((acc, s) => acc + s.retention, 0);
    return Math.round((total / displayedSkills.length) * 100);
  }, [displayedSkills]);

  // Open Practice Booster Modal
  const handleOpenPractice = (topicName: string) => {
    setActivePracticeTopic(topicName);
    setSelectedAnswers({});
    setShowExplanation(false);
  };

  // Complete Practice & Restore Retention
  const handleCompletePractice = async () => {
    if (!activePracticeTopic) return;
    setIsSubmittingPractice(true);

    try {
      await skillDecayApi.practiceTopic(activePracticeTopic, 0.95);
    } catch (e) {
      console.warn('Using local retention restoration:', e);
    }

    // Update state to restore memory retention and expand stability
    setSkills((prev) =>
      prev.map((s) => {
        if (s.topic === activePracticeTopic) {
          return {
            ...s,
            retention: 0.95,
            days_since_practice: 0,
            stability_days: Math.min(90, Math.round(s.stability_days * 1.5)), // Spaced repetition stability bonus
            alert: false,
            mastery: Math.min(1.0, s.mastery + 0.04)
          };
        }
        return s;
      })
    );

    setIsSubmittingPractice(false);
    setActivePracticeTopic(null);
    toast.success(`🎉 Retention for "${activePracticeTopic}" restored to 95%! Stability boosted. +50 XP!`);
  };

  // Add custom skill topic
  const handleAddCustomTopic = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newTopicName.trim();
    if (!trimmed) return;

    if (skills.some((s) => s.topic.toLowerCase() === trimmed.toLowerCase())) {
      toast.error('This topic is already being tracked.');
      return;
    }

    const newSkill: SkillDecayItem = {
      topic: trimmed,
      retention: 0.9,
      mastery: 0.85,
      stability_days: 14,
      days_since_practice: 1,
      alert: false,
      category: 'dsa'
    };

    setSkills((prev) => [newSkill, ...prev]);
    setNewTopicName('');
    setShowAddModal(false);
    toast.success(`Added "${trimmed}" to Skill Decay Tracker!`);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-16">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between md:items-end gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-purple-400 tracking-wide uppercase mb-1">
            <Sparkles className="w-3.5 h-3.5" /> Spaced Repetition Engine
          </div>
          <h2 className="text-3xl font-black tracking-tight text-slate-50 flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shadow-lg shadow-purple-500/10">
              <Brain className="w-5 h-5" />
            </div>
            Skill Decay Tracker
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
            Ebbinghaus forgetting curve ($R = e^{'{'}-t/S{'}'}$) — predicts when interview recall degrades and triggers active spaced rehearsals before concepts vanish.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2.5 bg-slate-900 border border-purple-500/30 hover:border-purple-500/60 text-purple-300 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg"
          >
            <Plus className="w-4 h-4" /> Track New Skill
          </button>
        </div>
      </header>

      {/* Summary KPI Ribbon */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-950/80 border border-white/5 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" /> Overall Retention
          </span>
          <div className="text-2xl font-black text-white mt-1 flex items-baseline gap-2">
            <span>{avgRetention}%</span>
            <span className="text-xs font-bold text-emerald-400">Target: 75%+</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
            <div className="bg-purple-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${avgRetention}%` }} />
          </div>
        </div>

        <div className="bg-slate-950/80 border border-white/5 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-red-400" /> Urgent Attention
          </span>
          <div className="text-2xl font-black text-red-400 mt-1">
            {criticals.length} {criticals.length === 1 ? 'Topic' : 'Topics'}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">Recall fallen below 40% threshold</p>
        </div>

        <div className="bg-slate-950/80 border border-white/5 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-cyan-400" /> Avg Memory Half-Life
          </span>
          <div className="text-2xl font-black text-cyan-400 mt-1">18.5 Days</div>
          <p className="text-[10px] text-slate-500 mt-1">Stability constant S expands on review</p>
        </div>

        <div className="bg-slate-950/80 border border-white/5 p-4 rounded-2xl">
          <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> Spaced Rehearsal
          </span>
          <div className="text-2xl font-black text-amber-400 mt-1">Active (12d streak)</div>
          <p className="text-[10px] text-slate-500 mt-1">+50 XP awarded per rehearsal</p>
        </div>
      </div>

      {/* Alert Banner / Peak Status */}
      {criticals.length > 0 ? (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-lg shadow-red-500/5">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center shrink-0 text-red-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <p className="font-extrabold text-red-400 text-sm">
                {criticals.length} Topic{criticals.length > 1 ? 's' : ''} Need Urgent Review
              </p>
              <p className="text-slate-300 text-xs mt-0.5">
                {criticals.map((s) => s.topic).join(', ')} — memory retention fallen below 40%. Practice now to prevent memory extinction before interview rounds.
              </p>
            </div>
          </div>
          <button
            onClick={() => handleOpenPractice(criticals[0].topic)}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl font-bold text-xs shrink-0 shadow-lg shadow-red-500/20 flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Rehearse #{criticals[0].topic}
          </button>
        </div>
      ) : (
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 flex items-center justify-between shadow-lg shadow-emerald-500/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-emerald-400 text-sm">All Skills at Peak Retention!</h4>
              <p className="text-xs text-slate-300 mt-0.5">
                Your spaced repetition schedule is up to date. Memory decay is completely neutralized.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold">
            100% Prepared
          </span>
        </div>
      )}

      {/* Interactive Time-Travel Simulator Bar */}
      <div className="bg-slate-900/70 p-4 rounded-2xl border border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="w-8 h-8 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
            <History className="w-4 h-4" />
          </div>
          <div>
            <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
              Ebbinghaus Forgetting Simulator
              <span className="text-[10px] font-normal text-slate-400">(Mathematical Decay Curve)</span>
            </span>
            <p className="text-[10px] text-slate-500">
              Simulate: <strong className="text-purple-300">{timeTravelDays === 0 ? 'Today (Real)' : `+${timeTravelDays} Days in the Future`}</strong>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {[0, 7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setTimeTravelDays(d)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                timeTravelDays === d
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                  : 'bg-slate-950 border border-white/5 text-slate-400 hover:text-white'
              }`}
            >
              {d === 0 ? 'Today' : `+${d}d`}
            </button>
          ))}
          {timeTravelDays > 0 && (
            <button
              onClick={() => setTimeTravelDays(0)}
              className="text-[11px] text-purple-400 hover:text-purple-300 underline ml-2 font-semibold"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {[
          { id: 'all', label: 'All Tracked Topics' },
          { id: 'dsa', label: 'Algorithms & Data Structures' },
          { id: 'architecture', label: 'System Design' },
          { id: 'core_cs', label: 'Core Computer Science' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterCategory(tab.id)}
            className={`px-3.5 py-1.5 rounded-xl font-bold transition-all shrink-0 ${
              filterCategory === tab.id
                ? 'bg-primary text-white shadow-md'
                : 'bg-slate-950 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Grid of Topic Decay Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredSkills.map((skill) => {
          const pct = Math.round(skill.retention * 100);
          const color = getRetentionColor(skill.retention);
          const label = getRetentionLabel(skill.retention);

          return (
            <div
              key={skill.topic}
              className={`bg-slate-950 border rounded-2xl p-6 transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between ${
                skill.alert ? 'border-red-500/30' : 'border-white/10'
              }`}
            >
              <div>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="font-extrabold text-base text-slate-100">{skill.topic}</h4>
                    <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      {skill.effectiveDays}d since practice
                      {timeTravelDays > 0 && (
                        <span className="text-[10px] text-purple-400 font-mono">
                          (+{timeTravelDays}d simulated)
                        </span>
                      )}
                    </p>
                  </div>
                  <span
                    className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border"
                    style={{ background: color + '15', color, borderColor: color + '40' }}
                  >
                    {label}
                  </span>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between text-xs text-slate-400 mb-1.5 font-medium">
                    <span>Ebbinghaus Retention</span>
                    <span className="font-bold font-mono text-sm" style={{ color }}>
                      {pct}%
                    </span>
                  </div>
                  <div className="h-2.5 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-white/5">
                    <div
                      className="h-full rounded-full transition-all duration-700 shadow-sm"
                      style={{ width: `${pct}%`, background: color }}
                    />
                  </div>
                </div>

                <div className="flex justify-between text-xs text-slate-500 pt-2 border-t border-white/5">
                  <span>
                    Baseline Mastery: <strong className="text-slate-300">{Math.round(skill.mastery * 100)}%</strong>
                  </span>
                  <span>
                    Half-Life Stability: <strong className="text-slate-300">{skill.stability_days}d</strong>
                  </span>
                </div>
              </div>

              {/* Practice Button (Now always interactive!) */}
              <div className="mt-5">
                <button
                  onClick={() => handleOpenPractice(skill.topic)}
                  className={`w-full py-2.5 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2 shadow-md ${
                    skill.alert
                      ? 'bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300'
                      : pct < 70
                      ? 'bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300'
                      : 'bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-300'
                  }`}
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  {skill.alert ? 'Practice Now (Urgent)' : 'Active Recall Practice'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* ==================== ACTIVE RECALL / PRACTICE MODAL ==================== */}
      {activePracticeTopic && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4 overflow-y-auto"
          onClick={() => setActivePracticeTopic(null)}
        >
          <div
            className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl p-6 sm:p-8 space-y-6 my-8 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                  <Brain className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-black text-white">{activePracticeTopic}</h3>
                    <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[10px] font-bold uppercase">
                      Active Rehearsal
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Reinforces neural pathways and resets the Ebbinghaus memory decay curve back to 95%.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActivePracticeTopic(null)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Questions Bank */}
            <div className="space-y-6">
              {(PRACTICE_QUESTIONS[activePracticeTopic] || PRACTICE_QUESTIONS['Dynamic Programming']).map((q, qIdx) => (
                <div key={qIdx} className="bg-slate-900/70 p-5 rounded-2xl border border-white/5 space-y-3">
                  <p className="text-sm font-bold text-white flex items-start gap-2">
                    <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-300 flex items-center justify-center text-xs shrink-0 mt-0.5">
                      {qIdx + 1}
                    </span>
                    <span>{q.question}</span>
                  </p>

                  <div className="space-y-2">
                    {q.options.map((opt, optIdx) => {
                      const isSelected = selectedAnswers[qIdx] === optIdx;
                      const isCorrect = optIdx === q.correctIdx;

                      let btnStyle = 'bg-slate-950/80 border-white/5 text-slate-300 hover:bg-white/5';
                      if (isSelected) {
                        btnStyle = isCorrect
                          ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-semibold'
                          : 'bg-red-500/20 border-red-500 text-red-300 font-semibold';
                      }

                      return (
                        <button
                          key={optIdx}
                          onClick={() => setSelectedAnswers((prev) => ({ ...prev, [qIdx]: optIdx }))}
                          className={`w-full text-left p-3 rounded-xl border text-xs transition-all flex items-center justify-between ${btnStyle}`}
                        >
                          <span>{opt}</span>
                          {isSelected && (
                            <span>{isCorrect ? '✓ Correct' : '✗ Incorrect'}</span>
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {selectedAnswers[qIdx] !== undefined && (
                    <p className="text-[11px] text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-white/5 leading-relaxed">
                      💡 <strong>Concept Insight:</strong> {q.explanation}
                    </p>
                  )}
                </div>
              ))}
            </div>

            {/* Completion Modal Actions */}
            <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => setActivePracticeTopic(null)}
                className="py-3 px-4 rounded-xl border border-slate-700 text-slate-400 hover:text-white text-xs font-bold"
              >
                Cancel
              </button>
              <button
                onClick={handleCompletePractice}
                disabled={isSubmittingPractice}
                className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-purple-600/25 flex items-center justify-center gap-2"
              >
                {isSubmittingPractice ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Saving Memory State...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" /> Complete Rehearsal & Restore Retention (95%)
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==================== ADD CUSTOM TOPIC MODAL ==================== */}
      {showAddModal && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setShowAddModal(false)}
        >
          <div
            className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-md p-6 space-y-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-purple-400" /> Track New Skill
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddCustomTopic} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-400 block mb-1.5">
                  Skill / Topic Name
                </label>
                <input
                  value={newTopicName}
                  onChange={(e) => setNewTopicName(e.target.value)}
                  placeholder="e.g. Kubernetes, React 19, Kafka, Go Concurrency..."
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-purple-500"
                  autoFocus
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold"
                >
                  Start Tracking
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
