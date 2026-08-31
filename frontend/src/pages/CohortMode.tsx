import React, { useState, useEffect } from 'react';
import { Users, Calendar, Video, Star, Award, ShieldAlert, Check, Plus, MessageSquare, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';

interface StudySession {
  id: string;
  group_name: string;
  scheduled_at: string;
  interviewer_name: string;
  interviewee_name: string;
  meeting_link: string | null;
  status: string; // scheduled | completed | cancelled
}

export const CohortMode = () => {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Scheduling Form
  const [peerId, setPeerId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [isInterviewer, setIsInterviewer] = useState(true);

  // Feedback Form
  const [activeFeedbackSessionId, setActiveFeedbackSessionId] = useState<string | null>(null);
  const [techRating, setTechRating] = useState(5);
  const [commRating, setCommRating] = useState(5);
  const [confRating, setConfRating] = useState(5);
  const [notes, setNotes] = useState('');

  // Mock list of peers in cohort study group
  const mockPeers = [
    { id: 'peer1', name: 'Rohan Sharma' },
    { id: 'peer2', name: 'Ananya Goel' },
    { id: 'peer3', name: 'Kabir Mehta' }
  ];

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await api.get('/cohorts/sessions');
      setSessions(res.data);
    } catch (e) {
      toast.error('Failed to load study group sessions.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleScheduleSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!peerId || !scheduledAt) return;

    setSubmitting(true);
    try {
      await api.post('/cohorts/schedule-session', {
        peer_id: peerId,
        scheduled_at: scheduledAt,
        role: isInterviewer ? 'interviewer' : 'interviewee'
      });
      toast.success('Peer interview session scheduled!');
      setPeerId('');
      setScheduledAt('');
      fetchSessions();
    } catch (e) {
      toast.error('Failed to schedule session.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeFeedbackSessionId) return;

    try {
      await api.post('/cohorts/feedback', {
        session_id: activeFeedbackSessionId,
        technical_rating: techRating,
        communication_rating: commRating,
        confidence_rating: confRating,
        notes: notes
      });
      toast.success('Feedback submitted! You earned +3 Premium Days.');
      setActiveFeedbackSessionId(null);
      setNotes('');
      fetchSessions();
    } catch (e) {
      toast.error('Failed to submit feedback.');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
          Cohort Peer Practice (Mock Rotation)
        </h2>
        <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
          Schedule rotating peer interviews, coordinate video calls, and exchange detailed performance feedback
        </p>
      </header>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Schedule Panel */}
        <div className="glass-panel p-6 rounded-3xl space-y-5 md:col-span-1">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Schedule Session</h3>
          <form onSubmit={handleScheduleSession} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Choose Cohort Peer</label>
              <select
                value={peerId}
                onChange={(e) => setPeerId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
              >
                <option value="">Select a classmate...</option>
                {mockPeers.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Select Date & Time</label>
              <input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Your Role</label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setIsInterviewer(true)}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl border transition ${
                    isInterviewer ? 'bg-primary text-slate-950 border-primary' : 'bg-slate-950 text-slate-400 border-slate-800'
                  }`}
                >
                  Interviewer
                </button>
                <button
                  type="button"
                  onClick={() => setIsInterviewer(false)}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl border transition ${
                    !isInterviewer ? 'bg-primary text-slate-950 border-primary' : 'bg-slate-950 text-slate-400 border-slate-800'
                  }`}
                >
                  Interviewee
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting || !peerId || !scheduledAt}
              className="w-full py-2.5 bg-primary hover:bg-primary-hover text-slate-950 font-bold rounded-xl text-xs transition"
            >
              Confirm Match
            </button>
          </form>
        </div>

        {/* Sessions List */}
        <div className="glass-panel p-6 rounded-3xl space-y-4 md:col-span-2">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Scheduled Peer Mocks</h3>
          
          {isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="w-6 h-6 text-primary animate-spin" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="text-slate-500 text-xs py-8 text-center border border-dashed border-slate-850 rounded-2xl">
              No sessions scheduled. Partner with classmates above.
            </p>
          ) : (
            <div className="space-y-3">
              {sessions.map((sess) => (
                <div key={sess.id} className="p-4 bg-slate-900 border border-slate-850 rounded-2xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">
                          {sess.interviewer_name} ➔ {sess.interviewee_name}
                        </span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                          sess.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-primary/10 text-primary'
                        }`}>
                          {sess.status}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500 block mt-1">
                        📅 {new Date(sess.scheduled_at).toLocaleString()}
                      </span>
                    </div>

                    {sess.meeting_link && sess.status === 'scheduled' && (
                      <a
                        href={sess.meeting_link}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/25 rounded-xl text-[10px] font-bold transition"
                      >
                        <Video className="w-3.5 h-3.5" />
                        Join Room
                      </a>
                    )}
                  </div>

                  {sess.status === 'scheduled' && (
                    <div className="flex justify-end gap-2 pt-2 border-t border-slate-850">
                      <button
                        onClick={() => setActiveFeedbackSessionId(sess.id)}
                        className="px-3 py-1 bg-slate-800 hover:bg-slate-750 text-white rounded-lg text-[10px] font-bold transition flex items-center gap-1"
                      >
                        <MessageSquare className="w-3 h-3" />
                        Submit Review
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Feedback Dialog Overlay */}
      {activeFeedbackSessionId && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-3xl max-w-md w-full space-y-5 animate-in zoom-in duration-200">
            <div>
              <h3 className="text-base font-bold text-white">Submit Peer Review</h3>
              <p className="text-slate-500 text-[10px] mt-0.5">Rate technical skills, structure, and communication.</p>
            </div>

            <form onSubmit={handleSubmitFeedback} className="space-y-4">
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Technical</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={techRating}
                    onChange={(e) => setTechRating(parseInt(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-white text-center font-bold"
                  />
                </div>
                <div>
                  <label className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Communication</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={commRating}
                    onChange={(e) => setCommRating(parseInt(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-white text-center font-bold"
                  />
                </div>
                <div>
                  <label className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Confidence</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={confRating}
                    onChange={(e) => setConfRating(parseInt(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-white text-center font-bold"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Evaluation Notes & Rubric Remarks</label>
                <textarea
                  rows={4}
                  placeholder="Provide structured feedback (GCA, dynamic behaviors, coding rubrics, etc)..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-xl p-3 text-xs text-white outline-none"
                />
              </div>

              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setActiveFeedbackSessionId(null)}
                  className="px-4 py-2 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl text-xs hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-slate-950 font-bold rounded-xl text-xs hover:bg-primary-hover"
                >
                  Post Review
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default CohortMode;
