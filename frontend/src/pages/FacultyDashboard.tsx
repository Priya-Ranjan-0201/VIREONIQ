import React, { useState, useEffect } from 'react';
import { Users, BookOpen, AlertCircle, PhoneCall, ChevronRight, BarChart3, Mail, Plus } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';

interface ClassData {
  id: string;
  class_name: string;
  join_code: string;
  student_count: number;
}

interface ClassOverview {
  analytics: {
    total_students: number;
    average_readiness: number;
    weakest_topics: string[];
    risk_level_student_count: number;
  };
  at_risk_students: {
    user_id: string;
    student_name: string;
    prs_score: number;
    activity_count: number;
    avoided_topics: string[];
  }[];
}

const DEFAULT_CLASSES: ClassData[] = [
  { id: 'cls-demo-cse-a', class_name: 'B.Tech CSE - Section A (2026)', join_code: 'CSE-2026-A', student_count: 48 },
  { id: 'cls-demo-cse-b', class_name: 'B.Tech CSE - Section B (Cloud & AI)', join_code: 'CSE-2026-B', student_count: 42 },
  { id: 'cls-demo-ece-a', class_name: 'B.Tech ECE - Core Systems Track', join_code: 'ECE-2026-A', student_count: 36 }
];

const DEFAULT_OVERVIEW_MAP: Record<string, ClassOverview> = {
  'cls-demo-cse-a': {
    analytics: {
      total_students: 48,
      average_readiness: 78.6,
      weakest_topics: ['Low-Level Concurrency', 'Distributed Caching', 'Dynamic Programming'],
      risk_level_student_count: 7
    },
    at_risk_students: [
      {
        user_id: 'std-001',
        student_name: 'Aditya Raj',
        prs_score: 52,
        activity_count: 3,
        avoided_topics: ['System Design', 'Socket Programming']
      },
      {
        user_id: 'std-002',
        student_name: 'Kavya Nair',
        prs_score: 58,
        activity_count: 5,
        avoided_topics: ['Graph Traversal', 'Tree Balancing']
      },
      {
        user_id: 'std-003',
        student_name: 'Manish Pandey',
        prs_score: 61,
        activity_count: 6,
        avoided_topics: ['Lock Contention', 'Memory Management']
      }
    ]
  },
  'cls-demo-cse-b': {
    analytics: {
      total_students: 42,
      average_readiness: 81.2,
      weakest_topics: ['Kubernetes Deployments', 'Kafka Event Streaming', 'SQL Indexing'],
      risk_level_student_count: 4
    },
    at_risk_students: [
      {
        user_id: 'std-004',
        student_name: 'Pooja Reddy',
        prs_score: 54,
        activity_count: 4,
        avoided_topics: ['Distributed Transactions', 'Raft Consensus']
      }
    ]
  }
};

export const FacultyDashboard = () => {
  const [classes, setClasses] = useState<ClassData[]>(DEFAULT_CLASSES);
  const [selectedClassId, setSelectedClassId] = useState<string | null>(DEFAULT_CLASSES[0].id);
  const [overview, setOverview] = useState<ClassOverview | null>(DEFAULT_OVERVIEW_MAP['cls-demo-cse-a']);
  const [newClassName, setNewClassName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isNudging, setIsNudging] = useState<string | null>(null);

  // Load classes on mount
  useEffect(() => {
    fetchClasses();
  }, []);

  // Load stats when selection changes
  useEffect(() => {
    if (selectedClassId) {
      fetchClassOverview(selectedClassId);
    } else {
      setOverview(null);
    }
  }, [selectedClassId]);

  const fetchClasses = async () => {
    try {
      const res = await api.get('/faculty/classes');
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        setClasses(res.data);
        if (!selectedClassId) {
          setSelectedClassId(res.data[0].id);
        }
      } else {
        setClasses(DEFAULT_CLASSES);
        if (!selectedClassId) setSelectedClassId(DEFAULT_CLASSES[0].id);
      }
    } catch (e) {
      setClasses(DEFAULT_CLASSES);
      if (!selectedClassId) setSelectedClassId(DEFAULT_CLASSES[0].id);
    }
  };

  const fetchClassOverview = async (classId: string) => {
    setIsLoading(true);
    const fallbackOverview = DEFAULT_OVERVIEW_MAP[classId] || DEFAULT_OVERVIEW_MAP['cls-demo-cse-a'];
    try {
      const res = await api.get(`/faculty/classes/${classId}/overview`);
      setOverview(res.data || fallbackOverview);
    } catch (e) {
      setOverview(fallbackOverview);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassName.trim()) return;

    try {
      const res = await api.post('/faculty/classes', {
        class_name: newClassName,
        subject_topics: ['DSA', 'System Design', 'OS', 'DBMS']
      });
      toast.success(`Class "${res.data.class_name}" created! Join code: ${res.data.join_code}`);
      setNewClassName('');
      fetchClasses();
    } catch (e) {
      const simulated: ClassData = {
        id: `cls-sim-${Date.now()}`,
        class_name: newClassName,
        join_code: `${newClassName.toUpperCase().replace(/\s+/g, '-')}-2026`,
        student_count: 0
      };
      setClasses(prev => [...prev, simulated]);
      setSelectedClassId(simulated.id);
      setNewClassName('');
      toast.success(`Cohort "${newClassName}" created in Sandbox!`);
    }
  };

  const handleNudgeStudent = async (studentId: string) => {
    if (!selectedClassId) return;
    setIsNudging(studentId);
    try {
      await api.post(`/faculty/classes/${selectedClassId}/students/${studentId}/nudge`);
      toast.success('In-app nudge and invitation sent to student!');
    } catch (e) {
      toast.error('Failed to send intervention nudge.');
    } finally {
      setIsNudging(null);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
            Faculty Intelligence Portal
          </h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
            Track student placement analytics & coordinate mock interviews (Without exposing transcripts)
          </p>
        </div>
      </header>

      {/* Class Manager Bar */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-3xl space-y-4 md:col-span-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">Active Cohorts</h3>
          {classes.length === 0 ? (
            <p className="text-slate-500 text-xs py-4">No active cohorts. Create one to begin tracking.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {classes.map((cls) => (
                <button
                  key={cls.id}
                  onClick={() => setSelectedClassId(cls.id)}
                  className={`px-4 py-3 rounded-2xl border text-xs font-bold transition flex items-center gap-2 ${
                    selectedClassId === cls.id
                      ? 'bg-primary text-slate-950 border-primary'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                  }`}
                >
                  <Users className="w-4 h-4" />
                  {cls.class_name} ({cls.student_count} std)
                  <span className="opacity-75 font-mono px-1.5 py-0.5 bg-black/10 rounded">
                    Code: {cls.join_code}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Create Class */}
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">Launch Cohort</h3>
          <form onSubmit={handleCreateClass} className="flex gap-2">
            <input
              type="text"
              placeholder="Cohort name (e.g. CS-A)..."
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
              className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 focus:border-primary rounded-xl text-white outline-none text-xs"
            />
            <button
              type="submit"
              className="p-2 bg-primary hover:bg-primary-hover text-slate-950 font-bold rounded-xl transition"
            >
              <Plus className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
        </div>
      ) : overview ? (
        <div className="space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-panel p-5 rounded-2xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Class Strength</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl font-bold text-white">{overview.analytics.total_students}</span>
                <span className="text-slate-400 text-xs">students</span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Average Readiness</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl font-bold text-white">
                  {overview.analytics.average_readiness.toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block font-medium">Critical Risks</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl font-bold text-rose-500">
                  {overview.analytics.risk_level_student_count}
                </span>
                <span className="text-slate-400 text-xs">underperforming</span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Core Weakness</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-xs font-bold text-amber-400 truncate">
                  {overview.analytics.weakest_topics.join(', ') || 'None detected'}
                </span>
              </div>
            </div>
          </div>

          {/* At Risk List */}
          <div className="glass-panel p-6 rounded-3xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Placement Readiness Interventions</h3>
              <span className="px-2.5 py-1 bg-rose-500/10 text-rose-400 text-[10px] font-bold rounded-lg border border-rose-500/20">
                Action Required
              </span>
            </div>

            {overview.at_risk_students.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-slate-800 rounded-2xl text-xs text-slate-500">
                Excellent! No students currently flagged as underperforming or at-risk.
              </div>
            ) : (
              <div className="divide-y divide-slate-850">
                {overview.at_risk_students.map((student) => (
                  <div key={student.user_id} className="flex justify-between items-center py-4 first:pt-0 last:pb-0">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{student.student_name}</span>
                        <span className="px-1.5 py-0.5 bg-rose-500/10 text-rose-400 text-[9px] font-bold rounded">
                          PRS: {student.prs_score}%
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-500">
                        Completed {student.activity_count} interviews. Avoiding:{' '}
                        <span className="text-slate-400 font-semibold">
                          {student.avoided_topics.join(', ') || 'N/A'}
                        </span>
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleNudgeStudent(student.user_id)}
                        disabled={isNudging === student.user_id}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold rounded-xl hover:bg-primary/20 transition disabled:opacity-50"
                      >
                        <AlertCircle className="w-3.5 h-3.5" />
                        Nudge Student
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-10 text-slate-500 text-xs">
          Select or launch a cohort to explore placement insights.
        </div>
      )}
    </div>
  );
};
export default FacultyDashboard;
