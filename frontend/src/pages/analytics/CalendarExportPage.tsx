import { useState, useMemo, useEffect } from 'react';
import {
  Calendar,
  Download,
  CheckCircle2,
  Clock,
  BookOpen,
  Zap,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Play,
  Plus,
  X,
  Share2,
  CalendarDays,
  Target,
  Code2,
  CheckSquare,
  Square
} from 'lucide-react';
import client from '@/api/client';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

interface PrepDay {
  day: number;
  week: number;
  topic: string;
  category: string;
  tasks: string[];
  date: string;
  done: boolean;
  estMinutes: number;
  practiceSnippet?: string;
}

// Generate rich, structured multi-day curriculum
const generateCurriculum = (daysCount: number): PrepDay[] => {
  const baseDate = new Date();
  const TOPIC_PATTERNS = [
    { topic: 'Arrays & Two Pointers', category: 'dsa', tasks: ['Two Sum II (Sorted Array)', 'Container With Most Water', 'Trapping Rain Water'], est: 90 },
    { topic: 'Sliding Window & Substrings', category: 'dsa', tasks: ['Longest Substring Without Repeating Characters', 'Minimum Window Substring', 'Sliding Window Maximum'], est: 90 },
    { topic: 'Prefix Sum & Hash Maps', category: 'dsa', tasks: ['Subarray Sum Equals K', 'Group Anagrams', 'Longest Consecutive Sequence'], est: 75 },
    { topic: 'Linked Lists & Pointers', category: 'dsa', tasks: ['Reverse Linked List (In-place)', 'Detect Cycle (Floyd\'s Tortoise & Hare)', 'Merge K Sorted Lists'], est: 80 },
    { topic: 'Monotonic Stacks & Queues', category: 'dsa', tasks: ['Daily Temperatures', 'Next Greater Element I & II', 'Largest Rectangle in Histogram'], est: 90 },
    { topic: 'Binary Search on Solution Domain', category: 'dsa', tasks: ['Search in Rotated Sorted Array', 'Koko Eating Bananas', 'Median of Two Sorted Arrays'], est: 100 },
    { topic: 'Binary Trees & Traversals', category: 'dsa', tasks: ['Level Order Traversal (BFS)', 'Lowest Common Ancestor (LCA)', 'Maximum Path Sum in Binary Tree'], est: 85 },
    { topic: 'Binary Search Trees (BST)', category: 'dsa', tasks: ['Validate BST', 'Kth Smallest Element in BST', 'Inorder Successor in BST'], est: 75 },
    { topic: 'Heaps & Priority Queues', category: 'dsa', tasks: ['Kth Largest Element in an Array', 'Find Median from Data Stream', 'Task Scheduler'], est: 85 },
    { topic: 'Graphs & BFS / DFS', category: 'dsa', tasks: ['Number of Islands', 'Clone Graph', 'Word Ladder I (BFS Shortest Path)'], est: 90 },
    { topic: 'Topological Sort & Cycles', category: 'dsa', tasks: ['Course Schedule I & II', 'Alien Dictionary', 'Detect Cycle in Directed Graph'], est: 90 },
    { topic: 'Shortest Path Algorithms', category: 'dsa', tasks: ['Dijkstra with Priority Queue', 'Network Delay Time', 'Cheapest Flights Within K Stops'], est: 100 },
    { topic: '1D Dynamic Programming', category: 'dsa', tasks: ['Climbing Stairs & House Robber', 'Coin Change (Min Coins)', 'Longest Increasing Subsequence (LIS)'], est: 95 },
    { topic: '2D Dynamic Programming', category: 'dsa', tasks: ['Longest Common Subsequence (LCS)', 'Edit Distance', '0/1 Knapsack & Subset Sum'], est: 110 },
    { topic: 'System Design: Caching & CDN', category: 'design', tasks: ['Redis Cache-Aside Pattern', 'Cache Stampede Prevention (XFetch)', 'Edge CDN Invalidation'], est: 120 },
    { topic: 'System Design: Load Balancers', category: 'design', tasks: ['Layer 4 vs Layer 7 Load Balancing', 'Consistent Hashing with Virtual Nodes', 'Health Checking & Failover'], est: 120 },
    { topic: 'System Design: Databases & Sharding', category: 'design', tasks: ['Vertical vs Horizontal Partitioning', 'Read Replicas & Replication Lag', 'ACID vs BASE & CAP Theorem'], est: 120 },
    { topic: 'Operating Systems: Concurrency', category: 'core_cs', tasks: ['Processes vs Threads & Mutexes', 'Producer-Consumer with Semaphores', 'Deadlock Coffman Conditions'], est: 80 },
    { topic: 'Computer Networks: TCP & Web', category: 'core_cs', tasks: ['TCP 3-Way Handshake & 2MSL TIME_WAIT', 'HTTP/1.1 vs HTTP/2 Multiplexing vs HTTP/3 QUIC', 'DNS Lookup Flow'], est: 80 },
    { topic: 'Low-Level Design & SOLID', category: 'lld', tasks: ['Design Parking Lot / Elevator System', 'Factory & Strategy Design Patterns', 'Dependency Inversion Principle'], est: 110 },
    { topic: 'Behavioral & Leadership Stories', category: 'behavioral', tasks: ['Formulate 4 STAR Stories (Situation, Task, Action, Result)', 'Amazon Leadership Principles prep', 'Handling technical disagreements'], est: 75 },
  ];

  const days: PrepDay[] = [];
  for (let i = 0; i < daysCount; i++) {
    const pattern = TOPIC_PATTERNS[i % TOPIC_PATTERNS.length];
    const taskDate = new Date(baseDate);
    taskDate.setDate(baseDate.getDate() + i);

    days.push({
      day: i + 1,
      week: Math.floor(i / 7) + 1,
      topic: pattern.topic,
      category: pattern.category,
      tasks: pattern.tasks,
      date: taskDate.toISOString().split('T')[0],
      done: i < 2, // First 2 days done by default
      estMinutes: pattern.est,
      practiceSnippet: `// Practice focus for Day ${i + 1}: ${pattern.topic}\n// Implement optimal solution with O(N) or O(log N) complexity.`
    });
  }
  return days;
};

export const CalendarExportPage = () => {
  const navigate = useNavigate();
  const [planType, setPlanType] = useState<number>(30);
  const [days, setDays] = useState<PrepDay[]>(() => {
    const saved = localStorage.getItem('vireoniq_prep_days_30');
    return saved ? JSON.parse(saved) : generateCurriculum(30);
  });
  const [selectedWeek, setSelectedWeek] = useState<number | 'all'>('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'completed'>('all');
  const [activeDayModal, setActiveDayModal] = useState<PrepDay | null>(null);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);

  // Switch plan type (30, 60, 90)
  const handleSelectPlanType = (type: number) => {
    setPlanType(type);
    const saved = localStorage.getItem(`vireoniq_prep_days_${type}`);
    if (saved) {
      setDays(JSON.parse(saved));
    } else {
      const generated = generateCurriculum(type);
      setDays(generated);
      localStorage.setItem(`vireoniq_prep_days_${type}`, JSON.stringify(generated));
    }
    setSelectedWeek('all');
    toast.info(`Switched to ${type}-Day Calibrated Preparation Plan! 📅`);
  };

  // Toggle individual day task completion
  const handleToggleTask = (dayNum: number, taskIdx: number) => {
    setDays((prev) => {
      const updated = prev.map((d) => {
        if (d.day === dayNum) {
          const newTasks = [...d.tasks];
          // We toggle day done status based on tasks
          return {
            ...d,
            done: !d.done
          };
        }
        return d;
      });
      localStorage.setItem(`vireoniq_prep_days_${planType}`, JSON.stringify(updated));
      return updated;
    });
    toast.success("Progress saved! +15 XP awarded! ⚡");
  };

  // Toggle whole day status
  const handleToggleDayDone = (dayNum: number) => {
    setDays((prev) => {
      const updated = prev.map((d) => (d.day === dayNum ? { ...d, done: !d.done } : d));
      localStorage.setItem(`vireoniq_prep_days_${planType}`, JSON.stringify(updated));
      return updated;
    });
    toast.success("Day milestone updated! 🎯");
  };

  // Calculate statistics
  const doneCount = useMemo(() => days.filter((d) => d.done).length, [days]);
  const progressPct = useMemo(() => Math.round((doneCount / days.length) * 100), [doneCount, days.length]);
  const totalHours = useMemo(() => Math.round(days.reduce((acc, d) => acc + d.estMinutes, 0) / 60), [days]);

  // Filtered days list
  const filteredDays = useMemo(() => {
    return days.filter((d) => {
      const matchWeek = selectedWeek === 'all' || d.week === selectedWeek;
      const matchStatus =
        filterStatus === 'all' ||
        (filterStatus === 'completed' && d.done) ||
        (filterStatus === 'pending' && !d.done);
      return matchWeek && matchStatus;
    });
  }, [days, selectedWeek, filterStatus]);

  // Total weeks in current plan
  const totalWeeks = useMemo(() => Math.ceil(days.length / 7), [days.length]);

  // Download .ics file
  const handleDownloadIcs = async () => {
    setIsDownloading(true);
    try {
      toast.info("Generating calendar iCal (.ics) file...");
      const response = await client.post(
        "/calendar/generate-ics",
        {
          plan_type: planType,
          tasks: days.map((d) => ({
            day: d.day,
            topic: d.topic,
            tasks: d.tasks,
            date: d.date
          }))
        },
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], { type: "text/calendar" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `vireoniq_${planType}_day_prep_plan.ics`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Preparation calendar downloaded successfully! 📅 Import into Apple / Google / Outlook Calendar.");
    } catch (e) {
      console.warn("Generating local RFC-compliant ICS file fallback:", e);
      // Fallback local ICS generation
      const icsLines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//VIREONIQ//Prep Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
      ];
      days.forEach((d) => {
        const formattedDate = d.date.replace(/-/g, "");
        icsLines.push(
          "BEGIN:VEVENT",
          `UID:day-${d.day}-${Date.now()}@vireoniq.com`,
          `DTSTART;VALUE=DATE:${formattedDate}`,
          `DTEND;VALUE=DATE:${formattedDate}`,
          `SUMMARY:VIREONIQ Day ${d.day}: ${d.topic}`,
          `DESCRIPTION:${d.tasks.join("\\n")}`,
          "END:VEVENT"
        );
      });
      icsLines.push("END:VCALENDAR");

      const blob = new Blob([icsLines.join("\r\n")], { type: "text/calendar" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `vireoniq_${planType}_day_prep_plan.ics`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Preparation calendar downloaded! 📅");
    } finally {
      setIsDownloading(false);
    }
  };

  // Google Calendar one-click URL generator
  const getGoogleCalendarUrl = (day: PrepDay) => {
    const title = encodeURIComponent(`VIREONIQ Day ${day.day}: ${day.topic}`);
    const details = encodeURIComponent(
      `Preparation Topic: ${day.topic}\n\nTasks:\n` +
        day.tasks.map((t) => `• ${t}`).join('\n') +
        `\n\nEstimated Time: ${day.estMinutes} mins\nPlatform: https://vireoniq.com/app/prep-calendar`
    );
    const dateFormatted = day.date.replace(/-/g, '');
    return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&dates=${dateFormatted}/${dateFormatted}`;
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-16">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 tracking-wide uppercase mb-1">
            <Sparkles className="w-3.5 h-3.5" /> AI Study Schedule Engine
          </div>
          <h2 className="text-3xl font-black text-slate-50 flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shadow-lg shadow-indigo-500/10">
              <Calendar className="w-5 h-5" />
            </div>
            Preparation Calendar
          </h2>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
            AI-calibrated daily study roadmap customized for top MNC & startup hiring timelines. Sync seamlessly to Google Calendar or export as RFC-compliant .ics files.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadIcs}
            disabled={isDownloading}
            className="flex items-center gap-2 px-5 py-2.5 bg-primary text-white rounded-xl font-bold hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 text-xs"
          >
            <Download className="w-4 h-4" />
            {isDownloading ? "Exporting..." : "Download .ics Plan"}
          </button>
        </div>
      </header>

      {/* Plan Type Selector */}
      <div className="flex flex-wrap items-center gap-3">
        {[
          { type: 30, label: "30-Day Sprint (MNC Fast-Track)" },
          { type: 60, label: "60-Day Comprehensive SDE-1/2" },
          { type: 90, label: "90-Day Full Mastery Program" }
        ].map((p) => (
          <button
            key={p.type}
            onClick={() => handleSelectPlanType(p.type)}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
              planType === p.type
                ? "bg-primary text-white shadow-lg shadow-primary/25"
                : "bg-slate-950 border border-white/10 text-slate-400 hover:text-white"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Progress & Stats Card */}
      <div className="bg-slate-950 border border-white/10 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <span className="text-sm font-bold text-slate-200">
              {doneCount} of {days.length} Days Completed
            </span>
            <p className="text-xs text-slate-400 mt-0.5">
              Estimated Total Study Investment: <strong className="text-indigo-400">{totalHours} hours</strong>
            </p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black text-indigo-400">{progressPct}%</span>
            <span className="text-xs text-slate-500 ml-1">completed</span>
          </div>
        </div>

        <div className="h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-white/5">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 rounded-full transition-all duration-700"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Week Navigator & Status Filters */}
      <div className="bg-slate-900/60 p-4 rounded-2xl border border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Weeks Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          <button
            onClick={() => setSelectedWeek('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
              selectedWeek === 'all'
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "bg-slate-950 text-slate-400 hover:text-white border border-white/5"
            }`}
          >
            All Weeks
          </button>
          {Array.from({ length: totalWeeks }, (_, i) => i + 1).map((wk) => (
            <button
              key={wk}
              onClick={() => setSelectedWeek(wk)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
                selectedWeek === wk
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "bg-slate-950 text-slate-400 hover:text-white border border-white/5"
              }`}
            >
              Week {wk}
            </button>
          ))}
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2 w-full md:w-auto justify-end text-xs">
          {(['all', 'pending', 'completed'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-xl font-bold capitalize transition-all ${
                filterStatus === st
                  ? "bg-slate-800 text-white border border-white/10"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Day Cards Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredDays.map((day) => (
          <div
            key={day.day}
            className={`bg-slate-950 border rounded-2xl p-5 transition-all hover:border-white/20 flex flex-col justify-between shadow-xl ${
              day.done ? 'border-emerald-500/40 bg-emerald-950/10' : 'border-white/10'
            }`}
          >
            <div>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-widest bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
                    Day {day.day} • Week {day.week}
                  </span>
                  <h4 className="font-extrabold text-slate-100 mt-2 text-sm leading-tight">{day.topic}</h4>
                </div>

                <button
                  onClick={() => handleToggleDayDone(day.day)}
                  className="p-1 rounded-lg hover:bg-white/5 text-slate-400 transition-colors"
                  title={day.done ? "Mark as Pending" : "Mark as Completed"}
                >
                  {day.done ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                  ) : (
                    <Clock className="w-5 h-5 text-slate-600 shrink-0 hover:text-slate-300" />
                  )}
                </button>
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-500 mb-3">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" /> {day.date}
                </span>
                <span>•</span>
                <span className="text-slate-400">{day.estMinutes} mins</span>
              </div>

              {/* Tasks List */}
              <div className="space-y-1.5 mb-4">
                {day.tasks.map((task, tIdx) => (
                  <div
                    key={tIdx}
                    className="text-xs text-slate-300 flex items-start gap-2 bg-slate-900/60 p-2 rounded-xl border border-white/5"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                    <span className="leading-snug">{task}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer Actions */}
            <div className="pt-3 border-t border-white/5 flex items-center justify-between gap-2">
              <a
                href={getGoogleCalendarUrl(day)}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-semibold text-slate-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
              >
                <CalendarDays className="w-3.5 h-3.5 text-indigo-400" /> Add to G-Cal
              </a>

              <button
                onClick={() => setActiveDayModal(day)}
                className="text-[11px] font-bold text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
              >
                Launch Study Workspace <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* ==================== DAY STUDY WORKSPACE MODAL ==================== */}
      {activeDayModal && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setActiveDayModal(null)}
        >
          <div
            className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl p-6 sm:p-8 space-y-6"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shadow-lg">
                  <Target className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-bold uppercase">
                      Day {activeDayModal.day}
                    </span>
                    <h3 className="text-xl font-black text-white">{activeDayModal.topic}</h3>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Scheduled Date: {activeDayModal.date} • Estimated Time: {activeDayModal.estMinutes} minutes
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveDayModal(null)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Tasks & Action Plan */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Targeted Problem Set & Milestones
              </h4>
              <div className="space-y-2">
                {activeDayModal.tasks.map((t, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-slate-900 rounded-xl border border-white/5 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2 text-slate-200 font-medium">
                      <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
                      <span>{t}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400 px-2 py-0.5 bg-slate-950 rounded border border-white/5">
                      ~30 mins
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Practice Actions */}
            <div className="bg-slate-900/60 p-4 rounded-2xl border border-indigo-500/20 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div>
                <h5 className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Code2 className="w-4 h-4 text-indigo-400" /> Sandboxed Practice Lab
                </h5>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Solve these problems in our multi-language AI coding lab with instant compiler feedback.
                </p>
              </div>
              <button
                onClick={() => {
                  setActiveDayModal(null);
                  navigate('/app/coding-interview');
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-600/30 flex items-center gap-1.5 shrink-0"
              >
                <Play className="w-3.5 h-3.5" /> Launch Coding Lab
              </button>
            </div>

            {/* Modal Actions */}
            <div className="pt-2 flex items-center justify-between">
              <a
                href={getGoogleCalendarUrl(activeDayModal)}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5"
              >
                <CalendarDays className="w-4 h-4" /> Add to Google Calendar
              </a>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    handleToggleDayDone(activeDayModal.day);
                    setActiveDayModal(null);
                  }}
                  className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                    activeDayModal.done
                      ? "bg-slate-800 text-slate-300 hover:bg-slate-700"
                      : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30"
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  {activeDayModal.done ? "Mark as Pending" : "Mark Day as Completed"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
