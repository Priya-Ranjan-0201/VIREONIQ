import { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Send, BrainCircuit, Activity, Terminal, Code2, CheckCircle2, RotateCcw, Sparkles } from "lucide-react";
import Editor from "@monaco-editor/react";
import { useInterviewStore } from "../../store/interviewStore";
import { useCodeStore } from "../../store/codeStore";
import { cn } from "@/lib/utils";
import { CODING_LANGUAGES, LanguageConfig, PROBLEM_PRESETS, ProblemPreset } from "./codingInterviewData";

export const CodingInterviewPage = () => {
  const { status, startInterview, submitAnswer, history, isLoading, lastEvaluation, reset } = useInterviewStore();
  const { sourceCode, setSourceCode, executeCode, isExecuting, executionResult, setLanguageId, fetchLanguages } = useCodeStore();
  
  const getPreferredLang = (): LanguageConfig => {
    try {
      const stored = localStorage.getItem('vireoniq_preferred_coding_language');
      if (stored) {
        const found = CODING_LANGUAGES.find(l => l.key === stored);
        if (found) return found;
      }
    } catch {}
    return CODING_LANGUAGES[0];
  };

  const [chatInput, setChatInput] = useState("");
  const [selectedProblem, setSelectedProblem] = useState<ProblemPreset>(PROBLEM_PRESETS[0]);
  const [selectedLanguage, setSelectedLanguage] = useState<LanguageConfig>(getPreferredLang());
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchLanguages();
    const initLang = getPreferredLang();
    setSelectedLanguage(initLang);
    setLanguageId(initLang.id);

    if (status === 'idle') {
      startInterview({
        target_role: "Senior Software Engineer", 
        difficulty_level: 4.0,
        session_mode: "coding"
      });
    }

    const initialCode = PROBLEM_PRESETS[0].starterCodes[initLang.key] || PROBLEM_PRESETS[0].starterCodes.python || "";
    setSourceCode(initialCode);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, isLoading]);

  const handleSelectProblem = (prob: ProblemPreset) => {
    setSelectedProblem(prob);
    const code = prob.starterCodes[selectedLanguage.key] || prob.starterCodes.python || "";
    setSourceCode(code);
    startInterview({
      target_role: "Senior Software Engineer",
      difficulty_level: 4.0,
      session_mode: "coding"
    });
  };

  const handleSelectLanguage = (lang: LanguageConfig) => {
    setSelectedLanguage(lang);
    setLanguageId(lang.id);
    try {
      localStorage.setItem('vireoniq_preferred_coding_language', lang.key);
    } catch {}
    const code = selectedProblem.starterCodes[lang.key] || selectedProblem.starterCodes.python || "";
    setSourceCode(code);
  };

  const handleSendChat = () => {
    if (!chatInput.trim() || isLoading) return;
    submitAnswer(chatInput);
    setChatInput("");
  };

  const handleRunCode = async () => {
    await executeCode();
  };

  const handleSubmitSolution = () => {
    const outputString = executionResult ? `\n\nExecution Output:\n${executionResult.stdout || executionResult.compile_output || 'No output'}` : '';
    const payload = `Here is my solution for ${selectedProblem.title} implemented in ${selectedLanguage.name}:\n\`\`\`${selectedLanguage.monacoLang}\n${sourceCode}\n\`\`\`${outputString}`;
    submitAnswer(payload);
  };

  return (
    <div className="h-[85vh] flex flex-col space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-3 shrink-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-50 flex items-center gap-3">
            <Code2 className="w-8 h-8 text-indigo-400" /> AI Coding Sandbox
          </h2>
          <p className="text-slate-400 text-sm mt-1">Multi-Language (10+ Stacks) Algorithmic Interview Environment with AST Telemetry</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Problem Selector */}
          <select
            value={selectedProblem.id}
            onChange={(e) => {
              const p = PROBLEM_PRESETS.find(pr => pr.id === e.target.value);
              if (p) handleSelectProblem(p);
            }}
            className="bg-slate-900 border border-white/10 text-xs text-slate-200 font-semibold px-3 py-2 rounded-xl focus:outline-none cursor-pointer hover:border-indigo-500/40"
          >
            {PROBLEM_PRESETS.map(p => (
              <option key={p.id} value={p.id} className="bg-slate-950">
                Problem: {p.title}
              </option>
            ))}
          </select>

          {/* Language Selector */}
          <select
            value={selectedLanguage.key}
            onChange={(e) => {
              const lang = CODING_LANGUAGES.find(l => l.key === e.target.value);
              if (lang) handleSelectLanguage(lang);
            }}
            className="bg-slate-900 border border-indigo-500/30 text-xs text-indigo-300 font-bold px-3 py-2 rounded-xl focus:outline-none cursor-pointer hover:border-indigo-500 shadow-sm"
          >
            {CODING_LANGUAGES.map(l => (
              <option key={l.key} value={l.key} className="bg-slate-950 text-slate-200">
                {l.icon} {l.name}
              </option>
            ))}
          </select>

          <Button variant="outline" size="sm" onClick={reset} className="rounded-xl border-white/10 text-xs">
            <RotateCcw className="w-3.5 h-3.5 mr-1" /> Reset
          </Button>

          <Button onClick={handleSubmitSolution} disabled={isLoading || isExecuting} className="glow-button rounded-xl shadow-lg shadow-indigo-600/30 text-xs">
            <CheckCircle2 className="w-4 h-4 mr-1.5" /> Submit Solution
          </Button>
        </div>
      </header>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Left Pane: Chat & Interview Flow */}
        <Card className="col-span-12 lg:col-span-4 bg-slate-950 border-white/10 flex flex-col overflow-hidden rounded-2xl shadow-2xl">
          <div className="h-12 border-b border-white/5 flex items-center justify-between px-4 bg-slate-900/50">
             <div className="flex items-center">
                <BrainCircuit className={`w-4 h-4 mr-2 ${isLoading ? 'text-indigo-400 animate-pulse' : 'text-slate-400'}`} />
                <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">AI Technical Bar Raiser</span>
             </div>
             <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
               Active Round
             </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-white/10">
            {history.map((turn, idx) => (
              <div key={idx} className={`flex ${turn.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[90%] rounded-xl px-4 py-3 text-sm ${
                  turn.role === 'user' 
                  ? 'bg-indigo-600/20 border border-indigo-500/30 text-slate-200 rounded-br-sm' 
                  : 'bg-slate-900 border border-white/5 text-slate-300 rounded-bl-sm shadow-xl'
                }`}>
                  <p className="whitespace-pre-wrap">{turn.content}</p>
                </div>
              </div>
            ))}
            
            {lastEvaluation && lastEvaluation.feedback_for_user && (
               <div className="flex justify-start">
                  <div className="max-w-[90%] bg-emerald-950/30 border border-emerald-500/20 rounded-xl rounded-bl-sm px-4 py-3 text-sm text-emerald-300 shadow-xl">
                     <p className="font-bold text-[10px] uppercase tracking-widest mb-1 text-emerald-400">Evaluation Feedback</p>
                     <p className="whitespace-pre-wrap">{lastEvaluation.feedback_for_user}</p>
                  </div>
               </div>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-900 border border-white/5 rounded-xl rounded-bl-sm px-4 py-3 shadow-xl flex items-center gap-2">
                   <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                   <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                   <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Chat Input */}
          <div className="p-3 border-t border-white/5 bg-slate-900/30">
             <div className="flex gap-2 relative items-center bg-slate-950 rounded-xl border border-white/10 p-1 shadow-inner">
                <input 
                  type="text" 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                  disabled={isLoading}
                  className="flex-1 bg-transparent border-none focus:outline-none text-slate-200 text-sm py-2 px-3 placeholder:text-slate-600"
                  placeholder="Ask a question, clarify constraints, or explain complexity..."
                />
                <Button 
                  size="icon" 
                  onClick={handleSendChat} 
                  disabled={!chatInput.trim() || isLoading}
                  className="rounded-lg shrink-0 h-8 w-8 bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  <Send className="w-3.5 h-3.5" />
                </Button>
             </div>
          </div>
        </Card>

        {/* Right Pane: Editor (Top) & Console (Bottom) */}
        <div className="col-span-12 lg:col-span-8 flex flex-col gap-4 min-h-0">
           {/* Code Editor */}
           <Card className="flex-1 bg-[#1e1e1e] border-white/10 flex flex-col overflow-hidden rounded-2xl shadow-2xl min-h-0">
              <div className="h-12 border-b border-white/5 flex items-center justify-between px-4 bg-[#252526]">
                 <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-indigo-400 font-bold">{selectedProblem.title}</span>
                    <span className="text-[11px] text-emerald-400 font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-1.5">
                       <span>{selectedLanguage.icon}</span>
                       <span className="font-semibold">{selectedLanguage.badge}</span>
                    </span>
                 </div>
                 <div className="flex items-center gap-2">
                    <select
                      value={selectedLanguage.key}
                      onChange={(e) => {
                        const lang = CODING_LANGUAGES.find(l => l.key === e.target.value);
                        if (lang) handleSelectLanguage(lang);
                      }}
                      className="bg-slate-900 border border-white/10 text-xs text-indigo-300 font-semibold px-2.5 py-1 rounded-lg focus:outline-none cursor-pointer hover:border-indigo-500/40"
                    >
                      {CODING_LANGUAGES.map(l => (
                        <option key={l.key} value={l.key} className="bg-slate-950 text-slate-200">
                          {l.icon} {l.name}
                        </option>
                      ))}
                    </select>
                    <Button size="sm" onClick={handleRunCode} disabled={isExecuting} variant="secondary" className="h-7 text-xs px-3.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-sm">
                       {isExecuting ? <Activity className="w-3 h-3 animate-spin mr-1.5" /> : <Play className="w-3 h-3 mr-1.5" />}
                       Run Code
                    </Button>
                 </div>
              </div>
              <div className="flex-1 relative">
                 <Editor
                   height="100%"
                   language={selectedLanguage.monacoLang}
                   theme="vs-dark"
                   value={sourceCode}
                   onChange={(val) => setSourceCode(val || "")}
                   options={{
                     minimap: { enabled: false },
                     fontSize: 13,
                     fontFamily: "JetBrains Mono, monospace",
                     padding: { top: 16 },
                     scrollBeyondLastLine: false,
                     smoothScrolling: true,
                   }}
                 />
              </div>
           </Card>

           {/* Console Output */}
           <Card className="h-44 shrink-0 bg-[#1e1e1e] border-white/10 flex flex-col overflow-hidden rounded-2xl shadow-2xl">
              <div className="h-10 border-b border-white/5 flex items-center px-4 bg-[#252526]">
                 <Terminal className="w-4 h-4 mr-2 text-slate-400" />
                 <span className="text-xs font-semibold text-slate-200">Execution Console</span>
                 {executionResult && (
                   <span className={cn(
                     "ml-4 text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider font-bold",
                     executionResult.status?.id === 3 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                   )}>
                     {executionResult.status?.description || "Completed"}
                   </span>
                 )}
              </div>
              <div className="flex-1 p-4 overflow-y-auto font-mono text-xs">
                 {isExecuting ? (
                    <div className="text-slate-500 flex items-center">
                       <Activity className="w-4 h-4 mr-2 animate-spin" /> Compiling & Executing in Sandboxed Subprocess...
                    </div>
                 ) : executionResult ? (
                    <div className="space-y-2">
                       {executionResult.compile_output && <div className="text-red-400 whitespace-pre-wrap">{executionResult.compile_output}</div>}
                       {executionResult.stderr && <div className="text-red-400 whitespace-pre-wrap">{executionResult.stderr}</div>}
                       {executionResult.stdout && <div className="text-slate-300 whitespace-pre-wrap">{executionResult.stdout}</div>}
                       <div className="text-slate-500 text-[11px] mt-2 pt-2 border-t border-white/5">
                          Time: {executionResult.time}s • Memory: {executionResult.memory}KB
                       </div>
                    </div>
                 ) : (
                    <div className="text-slate-600">Click "Run Code" to compile and execute in the sandbox.</div>
                 )}
              </div>
           </Card>
        </div>
      </div>
    </div>
  );
};

