import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Users2, Search, ArrowRight, Video, MessageCircle, ShieldCheck, Zap, RotateCcw, CheckCircle2, Sparkles } from "lucide-react";
import { useAuthStore } from "@/store/authStore";

export const P2PMockPage = () => {
  const { user } = useAuthStore();
  const [status, setStatus] = useState<"idle" | "searching" | "matched" | "in_room">("idle");
  const [matchedPeer, setMatchedPeer] = useState<any>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const searchTimeoutRef = useRef<any>(null);

  const startMatching = () => {
    setStatus("searching");
    const userId = user?.id || "demo-candidate-1";
    
    // Attempt real WebSocket connection
    try {
      const wsUrl = `ws://localhost:8000/api/v1/ws/matchmaker/${userId}`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "find_match" }));
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "match_found") {
            setMatchedPeer({
              name: data.peer_name || "Alex K.",
              role: data.peer_role || "Senior Backend Engineer",
              company: data.peer_company || "Uber",
              avatar: "A",
              rating: "4.9/5.0"
            });
            setStatus("matched");
            if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
          }
        } catch (e) {
          // ignore malformed websocket messages
        }
      };
      
      ws.onerror = () => {
        // Fallback to simulated match
      };

      socketRef.current = ws;
    } catch (e) {
      // Offline fallback
    }

    // Fallback simulation timer after 3.2 seconds
    searchTimeoutRef.current = setTimeout(() => {
      setMatchedPeer({
        name: "Alex K.",
        role: "Senior Backend Engineer",
        company: "Uber",
        avatar: "A",
        rating: "4.9/5.0"
      });
      setStatus("matched");
    }, 3200);
  };

  const handleCancel = () => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    if (socketRef.current) socketRef.current.close();
    setStatus("idle");
  };

  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
      socketRef.current?.close();
    };
  }, []);

  return (
    <div className="h-full flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-50 flex items-center gap-3">
             <Users2 className="w-8 h-8 text-indigo-400" /> P2P Mocking Matchmaker
          </h2>
          <p className="text-slate-400 text-sm mt-1">Connect with verified peers globally and practice real-world collaborative interview scenarios.</p>
        </div>
        {status !== 'idle' && (
          <Button variant="outline" size="sm" onClick={handleCancel} className="rounded-xl border-white/10 text-xs">
            <RotateCcw className="w-3.5 h-3.5 mr-1" /> Reset
          </Button>
        )}
      </header>

      <div className="grid gap-8 lg:grid-cols-2 flex-1">
         {/* Matchmaker Panel */}
         <Card className="bg-slate-950 border-white/10 rounded-3xl overflow-hidden shadow-2xl flex flex-col items-center justify-center p-12 text-center relative">
            {status === "idle" && (
              <>
                <div className="w-24 h-24 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-8 shadow-[0_0_30px_rgba(99,102,241,0.2)]">
                   <Search className="w-10 h-10 text-indigo-400 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Find a Mock Interview Partner</h3>
                <p className="text-slate-400 max-w-sm mb-8 text-sm italic leading-relaxed">
                   "The best way to master interviews is through mutual practice. Pair up with calibrated engineers for a 60-minute reciprocal round."
                </p>
                <Button onClick={startMatching} size="lg" className="rounded-2xl px-10 py-7 text-base font-bold glow-button shadow-xl shadow-indigo-600/30">
                   Start Matchmaking <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </>
            )}

            {status === "searching" && (
              <div className="space-y-8 w-full max-w-sm">
                 <div className="relative flex items-center justify-center">
                    <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping" />
                    <div className="w-24 h-24 rounded-full bg-indigo-600 flex items-center justify-center z-10 shadow-xl shadow-indigo-600/40">
                       <Zap className="w-10 h-10 text-white animate-bounce" />
                    </div>
                 </div>
                 <h3 className="text-2xl font-bold text-white">Searching Global Talent Pool...</h3>
                 <div className="space-y-2">
                    <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-white/5">
                       <div className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 animate-pulse" style={{ width: '75%' }} />
                    </div>
                    <p className="text-[11px] text-slate-500 font-bold uppercase tracking-widest">Matching SDE-2 & Senior Backend peers...</p>
                 </div>
                 <Button variant="ghost" onClick={handleCancel} className="text-slate-500 hover:text-red-400 text-xs">Cancel Search</Button>
              </div>
            )}

            {status === "matched" && matchedPeer && (
              <div className="space-y-8 animate-in zoom-in-95 duration-500 w-full max-w-md">
                 <div className="bg-emerald-500/20 text-emerald-400 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest inline-flex items-center gap-1.5 border border-emerald-500/30">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Match Found • 98% Compatibility
                 </div>
                 <h3 className="text-2xl font-black text-white">Peer Match Connected</h3>
                 
                 <div className="flex items-center justify-center gap-8 py-2">
                    <div className="text-center">
                       <div className="w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-indigo-600/30 mb-2">You</div>
                       <p className="text-xs font-bold text-slate-200">You</p>
                       <p className="text-[10px] text-slate-500 font-mono">Candidate Round 1</p>
                    </div>
                    
                    <div className="flex flex-col items-center">
                       <div className="text-xs font-bold text-indigo-400 px-2 py-1 bg-indigo-950/80 rounded-md border border-indigo-800">VS</div>
                       <span className="text-[10px] text-slate-500 mt-1 font-mono">60 Mins</span>
                    </div>

                    <div className="text-center">
                       <div className="w-16 h-16 rounded-2xl bg-purple-600 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-purple-600/30 mb-2">{matchedPeer.avatar}</div>
                       <p className="text-xs font-bold text-slate-200">{matchedPeer.name}</p>
                       <p className="text-[10px] text-slate-500 font-mono">{matchedPeer.role}</p>
                    </div>
                 </div>

                 <div className="p-3.5 bg-slate-900/60 border border-white/5 rounded-xl text-left text-xs text-slate-300 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Peer Rating:</span>
                      <span className="text-amber-400 font-bold">★ {matchedPeer.rating}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Agenda:</span>
                      <span className="text-slate-300">30m Distributed Systems + 30m AST Code Review</span>
                    </div>
                 </div>

                 <div className="flex gap-3 justify-center">
                    <Button 
                      onClick={() => window.location.href = '/app/interview'} 
                      className="rounded-xl px-6 py-5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs glow-button shadow-lg"
                    >
                       <Video className="w-4 h-4 mr-2" /> Launch Interactive Room
                    </Button>
                    <Button variant="outline" onClick={handleCancel} className="rounded-xl border-white/10 text-xs px-4">
                       Decline
                    </Button>
                 </div>
              </div>
            )}
         </Card>

         {/* Information Panel */}
         <div className="space-y-6">
            <Card className="bg-slate-950 border-white/10 rounded-3xl p-8 shadow-2xl">
               <h4 className="text-sm font-bold text-slate-100 mb-6 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" /> P2P Rules of Engagement
               </h4>
               <ul className="space-y-4">
                  {[
                    "Each session is 60 minutes structured into 30m Candidate + 30m Interviewer roles.",
                    "Professionalism and constructive feedback are tracked for community reputation.",
                    "Completing verified P2P mocks increases your 'Peer Reliability' CRI atom.",
                    "Both participants receive an automated multi-agent rubric summary upon conclusion."
                  ].map((rule, idx) => (
                    <li key={idx} className="flex gap-3">
                       <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                       <p className="text-sm text-slate-400 leading-relaxed">{rule}</p>
                    </li>
                  ))}
               </ul>
            </Card>

            <Card className="bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
               <div className="absolute -right-8 -bottom-8 opacity-5 group-hover:opacity-10 transition-opacity">
                  <Users2 className="w-48 h-48" />
               </div>
               <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
                 <Sparkles className="w-4 h-4" />
                 Crowdsourced Calibrated Pool
               </div>
               <h4 className="text-lg font-bold text-white mb-2">12,000+ Active Candidates Mocking Weekly</h4>
               <p className="text-xs text-slate-400 leading-relaxed">
                  Real-time peer assessments contribute validated evidence points to your verified Career Passport.
               </p>
            </Card>
         </div>
      </div>
    </div>
  );
};

