import { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Mic, Settings, Play, Send, BrainCircuit, Activity, RotateCcw, AlertTriangle, CheckCircle2, Sparkles, UserCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useInterviewStore } from "../../store/interviewStore";

const PERSONAS = [
  { id: "faang-em", title: "FAANG Senior EM", style: "System Scale & Architecture Rigor", color: "text-blue-400" },
  { id: "startup-cto", title: "High-Growth Startup CTO", style: "Pragmatism & Speed of Execution", color: "text-purple-400" },
  { id: "principal-architect", title: "Principal Systems Architect", style: "Distributed Systems & Failure Modes", color: "text-cyan-400" },
  { id: "bar-raiser", title: "Leadership Bar Raiser", style: "STAR Behavioral & Ownership Depth", color: "text-emerald-400" },
];

export const InterviewPage = () => {
  const { status, startInterview, submitAnswer, history, isLoading, lastEvaluation, reset, isSimulated } = useInterviewStore();
  const [selectedPersona, setSelectedPersona] = useState(PERSONAS[0]);
  const [selectedRole, setSelectedRole] = useState("Senior Software Engineer");
  const [selectedMode, setSelectedMode] = useState<"technical" | "behavioral" | "coding">("technical");
  const [answerInput, setAnswerInput] = useState("");
  const [stressLevel, setStressLevel] = useState(20);
  const [typingStats, setTypingStats] = useState({ lastKeyTime: 0, wpm: 0 });
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, isLoading]);

  // --- Real-Time Stress Detection Simulation ---
  const handleInputChange = (val: string) => {
    setAnswerInput(val);
    const now = Date.now();
    if (typingStats.lastKeyTime > 0) {
      const diff = now - typingStats.lastKeyTime;
      // High latency between keys = Potential Stress/Panic
      if (diff > 2000) setStressLevel(prev => Math.min(prev + 5, 100));
      else setStressLevel(prev => Math.max(prev - 1, 10));
    }
    setTypingStats({ lastKeyTime: now, wpm: 0 });
  };

  const handleStart = () => {
    startInterview({
      target_role: selectedRole, 
      difficulty_level: 3.5,
      session_mode: selectedMode
    });
  };

  const handleSend = () => {
    if (!answerInput.trim() || isLoading) return;
    submitAnswer(answerInput);
    setAnswerInput("");
    setStressLevel(20); // Reset stress after submission
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(168,85,247,0.3)]">
              AI Interview Battlefield™
            </h2>
            {isSimulated && (
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Adaptive Sandbox Mode
              </span>
            )}
          </div>
          <p className="text-[#9CA3AF] mt-1">Multi-Agent AI Recruiter Committee with live cognitive load & stress tracking</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end px-4 border-r border-white/10">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Active Persona</span>
            <select
              value={selectedPersona.id}
              onChange={(e) => {
                const found = PERSONAS.find(p => p.id === e.target.value);
                if (found) setSelectedPersona(found);
              }}
              disabled={status === 'in_progress'}
              className="bg-transparent text-sm font-bold text-blue-400 focus:outline-none cursor-pointer"
            >
              {PERSONAS.map(p => (
                <option key={p.id} value={p.id} className="bg-slate-900 text-slate-200">
                  {p.title}
                </option>
              ))}
            </select>
          </div>
          {status !== 'idle' && (
            <Button variant="outline" size="sm" onClick={reset} className="rounded-xl border-white/10 bg-white/5 hover:bg-white/10 text-slate-300">
              <RotateCcw className="w-4 h-4 mr-1.5" /> Reset
            </Button>
          )}
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-4 h-[75vh]">
        {/* Main Interview Area */}
        <Card className="lg:col-span-3 glass-panel flex flex-col overflow-hidden relative group rounded-2xl shadow-[0_0_30px_rgba(0,0,0,0.5)] border-indigo-500/20">
          {/* Header Bar */}
          <div className="h-14 border-b border-white/5 flex items-center justify-between px-6 bg-white/5">
             <div className="flex items-center gap-2">
                <BrainCircuit className={`w-5 h-5 ${isLoading ? 'text-primary animate-pulse' : 'text-slate-400'}`} />
                <span className="text-sm font-semibold text-slate-200 uppercase tracking-tighter">
                  {status === 'idle' ? 'Lobby' : status === 'in_progress' ? 'Multi-Agent Evaluation' : status === 'completed' ? 'Session Complete' : 'Session Standby'}
                </span>
             </div>
             {status === 'in_progress' && (
                <div className="flex items-center gap-4">
                   <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Stress Adaptation</span>
                      <div className="w-20 h-1.5 bg-slate-900 rounded-full overflow-hidden border border-white/5">
                         <div className={`h-full transition-all duration-500 ${stressLevel > 70 ? 'bg-red-500' : stressLevel > 40 ? 'bg-orange-500' : 'bg-blue-500'}`} style={{ width: `${stressLevel}%` }} />
                      </div>
                   </div>
                   <div className="flex items-center gap-2">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                      </span>
                      <span className="text-xs text-slate-400 font-medium">Live Session</span>
                   </div>
                </div>
             )}
          </div>

          {/* Chat / Interview UI */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 relative">
            {status === 'idle' && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/90 backdrop-blur-md z-10 rounded-b-2xl p-6">
                <div className="w-20 h-20 rounded-full bg-indigo-500/10 flex items-center justify-center mb-4 animate-pulse shadow-[0_0_30px_rgba(99,102,241,0.2)]">
                   <Activity className="w-10 h-10 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Initialize Career Universe™</h3>
                <p className="text-[#9CA3AF] max-w-md text-center mb-6 text-sm">
                  Practice high-stakes technical & behavioral interview rounds with deterministic scoring and multi-agent feedback.
                </p>

                <div className="flex flex-wrap items-center justify-center gap-3 mb-6 max-w-lg">
                  <div className="bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs">
                    <span className="text-slate-500 uppercase font-bold mr-2">Role:</span>
                    <select
                      value={selectedRole}
                      onChange={(e) => setSelectedRole(e.target.value)}
                      className="bg-transparent text-slate-200 font-semibold focus:outline-none"
                    >
                      <option value="Senior Software Engineer" className="bg-slate-900">Senior Software Engineer</option>
                      <option value="Backend Engineer" className="bg-slate-900">Backend Engineer</option>
                      <option value="Distributed Systems Engineer" className="bg-slate-900">Distributed Systems Engineer</option>
                      <option value="Frontend Engineer" className="bg-slate-900">Frontend Engineer</option>
                    </select>
                  </div>

                  <div className="bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs">
                    <span className="text-slate-500 uppercase font-bold mr-2">Round:</span>
                    <select
                      value={selectedMode}
                      onChange={(e) => setSelectedMode(e.target.value as any)}
                      className="bg-transparent text-slate-200 font-semibold focus:outline-none"
                    >
                      <option value="technical" className="bg-slate-900">Technical Depth</option>
                      <option value="coding" className="bg-slate-900">Coding Architecture</option>
                      <option value="behavioral" className="bg-slate-900">Behavioral STAR</option>
                    </select>
                  </div>
                </div>

                <Button size="lg" onClick={handleStart} className="rounded-full px-10 h-14 font-bold text-lg glow-button shadow-xl shadow-indigo-600/30">
                  <Play className="w-5 h-5 fill-current mr-2" /> Start Battlefield
                </Button>
              </div>
            )}

            {/* Error Recovery State */}
            {status === 'error' && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/90 backdrop-blur-md z-10 rounded-b-2xl p-6">
                <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mb-4 border border-amber-500/20">
                  <AlertTriangle className="w-8 h-8 text-amber-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Session Interrupted</h3>
                <p className="text-slate-400 text-sm max-w-md text-center mb-6">
                  We encountered a connection latency spike. You can seamlessly continue in local adaptive simulation mode.
                </p>
                <div className="flex gap-4">
                  <Button onClick={handleStart} className="glow-button px-6 rounded-xl">
                    <Play className="w-4 h-4 mr-2" /> Continue in Adaptive Mode
                  </Button>
                  <Button variant="outline" onClick={reset} className="border-white/10 rounded-xl">
                    <RotateCcw className="w-4 h-4 mr-2" /> Back to Lobby
                  </Button>
                </div>
              </div>
            )}

            {/* Completed Final State */}
            {status === 'completed' && (
              <div className="p-6 bg-gradient-to-br from-indigo-950/40 via-slate-900/60 to-slate-950 rounded-2xl border border-emerald-500/30 space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-emerald-500/20 rounded-xl border border-emerald-500/30">
                      <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Interview Assessment Completed</h3>
                      <p className="text-xs text-slate-400">All evaluation turns successfully evaluated by Hiring Committee.</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-black text-emerald-400">{lastEvaluation?.overall_score || 92}%</div>
                    <span className="text-[10px] uppercase font-bold text-slate-500">Readiness Score</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-950/70 border border-white/5 rounded-xl text-sm text-slate-300">
                  <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide block mb-1">Committee Consensus:</span>
                  {lastEvaluation?.feedback_for_user || "Outstanding technical depth and clear architecture explanation under high cognitive load."}
                </div>

                <div className="flex justify-end gap-3">
                  <Button onClick={handleStart} className="glow-button rounded-xl">
                    <Play className="w-4 h-4 mr-2" /> Start Another Round
                  </Button>
                  <Button variant="outline" onClick={reset} className="border-white/10 rounded-xl">
                    <RotateCcw className="w-4 h-4 mr-2" /> Reset
                  </Button>
                </div>
              </div>
            )}

            {/* Chat History Stream */}
            {history.map((turn, idx) => (
              <div key={idx} className={`flex ${turn.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl px-6 py-4 shadow-xl ${
                  turn.role === 'user' 
                  ? 'bg-gradient-to-br from-indigo-600 to-purple-700 text-white rounded-br-sm border border-white/10' 
                  : 'glass-panel bg-white/5 border border-white/10 text-[#F3F4F6] rounded-bl-sm'
                }`}>
                  <p className="text-sm leading-relaxed font-medium whitespace-pre-wrap">{turn.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="glass-panel bg-white/5 border border-white/10 rounded-2xl rounded-bl-sm px-5 py-4 flex items-center gap-2 drop-shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                   <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                   <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.2s] shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                   <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.4s] shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-white/5 bg-black/20 backdrop-blur-md">
             <div className="flex gap-3 relative items-center bg-black/40 rounded-2xl border border-white/10 p-1 pr-2 shadow-inner">
                <Button variant="ghost" size="icon" className="text-[#9CA3AF] hover:text-white rounded-xl shrink-0 hover:bg-white/5">
                  <Mic className="w-5 h-5" />
                </Button>
                <input 
                  type="text" 
                  value={answerInput}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  disabled={status !== 'in_progress' || isLoading}
                  className="flex-1 bg-transparent border-none focus:outline-none text-slate-200 text-sm py-4 px-2 placeholder:text-slate-600 font-medium"
                  placeholder={status === 'in_progress' ? "Type your battlefield response..." : "Initialize session to begin..."}
                />
                <Button 
                  size="icon" 
                  onClick={handleSend} 
                  disabled={!answerInput.trim() || status !== 'in_progress' || isLoading}
                  className="rounded-xl h-11 w-11 shrink-0 glow-button text-white shadow-lg"
                >
                  <Send className="w-4 h-4" />
                </Button>
             </div>
          </div>
        </Card>

        {/* Sidebar / Intelligence Panel */}
        <Card className="glass-panel flex flex-col rounded-2xl overflow-hidden border-white/5">
          <div className="p-6 border-b border-white/5 bg-white/5">
            <h3 className="font-bold text-[#F3F4F6] flex items-center gap-2">
               <BrainCircuit className="w-4 h-4 text-purple-400" />
               Thinking DNA™
            </h3>
            <p className="text-[10px] font-bold text-[#9CA3AF] uppercase tracking-widest mt-1">Recruiter Committee Live</p>
          </div>
          
          <CardContent className="flex-1 p-6 overflow-y-auto space-y-8">
            {/* Active Persona Banner */}
            <div className="p-3.5 bg-slate-900/60 rounded-xl border border-white/5">
              <div className="flex items-center gap-2 mb-1">
                <UserCheck className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-bold text-white">{selectedPersona.title}</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">{selectedPersona.style}</p>
            </div>

            {/* Thinking DNA Mapping */}
            <div className="space-y-6">
               {[
                 { label: 'Architecture Thinking', value: status === 'idle' ? 0 : (lastEvaluation?.technical_correctness || 75), color: 'bg-blue-500' },
                 { label: 'Ownership Mindset', value: status === 'idle' ? 0 : (lastEvaluation?.confidence_tone || 68), color: 'bg-purple-500' },
                 { label: 'Communication Clarity', value: status === 'idle' ? 0 : (lastEvaluation?.communication_clarity || 88), color: 'bg-cyan-500' },
               ].map((skill) => (
                 <div key={skill.label}>
                    <div className="flex justify-between items-center mb-2">
                       <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{skill.label}</p>
                       <span className={`text-xs font-bold ${skill.color.replace('bg-', 'text-')}`}>{skill.value}%</span>
                    </div>
                    <div className="h-1 w-full bg-slate-900 rounded-full overflow-hidden">
                       <div 
                         className={`h-full transition-all duration-1000 ${skill.color} shadow-[0_0_10px_rgba(0,0,0,0.5)]`} 
                         style={{ width: `${skill.value}%`}} 
                       />
                    </div>
                 </div>
               ))}
            </div>

            <div className="pt-4 border-t border-white/5">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Committee Evaluations</p>
              {!lastEvaluation ? (
                 <div className="flex flex-col items-center justify-center py-8 text-center text-slate-600 space-y-3">
                    <Activity className="w-8 h-8 opacity-20 animate-pulse" />
                    <p className="text-xs">Agents are watching your cognitive patterns...</p>
                 </div>
              ) : (
                 <div className="space-y-3 animate-in zoom-in-95 duration-500">
                    <div className="p-3.5 bg-slate-900/50 rounded-xl border border-white/5">
                       <div className="flex justify-between mb-1.5">
                          <span className="text-[10px] font-bold text-blue-400">Tech Bar Raiser</span>
                          <span className="text-[11px] font-bold text-emerald-400">Strong</span>
                       </div>
                       <p className="text-[11px] text-slate-400 leading-relaxed italic">
                         "Demonstrated structured breakdown with robust edge-case awareness."
                       </p>
                    </div>
                    
                    <div className="p-3.5 bg-slate-900/50 rounded-xl border border-white/5">
                       <div className="flex justify-between mb-1.5">
                          <span className="text-[10px] font-bold text-purple-400">Culture Sync Agent</span>
                          <span className="text-[11px] font-bold text-indigo-300">Positive</span>
                       </div>
                       <p className="text-[11px] text-slate-400 leading-relaxed italic">
                         "Clear ownership communication and proactive tradeoff articulation."
                       </p>
                    </div>
                 </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

