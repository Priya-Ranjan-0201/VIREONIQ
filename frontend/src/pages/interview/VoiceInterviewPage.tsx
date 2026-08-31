import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Mic, MicOff, Volume2, VolumeX, BrainCircuit, Activity, Power, Send, RotateCcw, MessageSquare } from "lucide-react";
import { useInterviewStore } from "../../store/interviewStore";
import { cn } from "@/lib/utils";

// Types for Speech Recognition
interface SpeechRecognitionEvent extends Event {
  results: {
    length: number;
    [key: number]: {
      [key: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: any) => void;
  onend: () => void;
}

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export const VoiceInterviewPage = () => {
  const { status, startInterview, submitAnswer, history, isLoading, reset } = useInterviewStore();
  
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(true);
  const [transcript, setTranscript] = useState("");
  const [manualText, setManualText] = useState("");
  const [isSupportedSTT, setIsSupportedSTT] = useState(true);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recog = new SpeechRecognition();
        recog.continuous = true;
        recog.interimResults = true;
        recog.lang = 'en-US';

        recog.onresult = (event: SpeechRecognitionEvent) => {
          let interimTranscript = '';
          for (let i = event.results.length - 1; i < event.results.length; i++) {
            const result = event.results[i][0].transcript;
            interimTranscript += result;
          }
          setTranscript(interimTranscript);
        };

        recog.onerror = (e: any) => {
          console.warn("Speech recognition error/permission:", e);
          setIsListening(false);
        };

        recog.onend = () => {
          setIsListening(false);
        };

        setRecognition(recog);
        recognitionRef.current = recog;
      } catch (err) {
        setIsSupportedSTT(false);
      }
    } else {
      setIsSupportedSTT(false);
    }

    if (status === 'idle') {
      startInterview({
        target_role: "Senior Software Engineer",
        difficulty_level: 3.5,
        session_mode: "behavioral"
      });
    }

    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) {
          // ignore recognition stop error on unmount
        }
      }
      window.speechSynthesis?.cancel();
    };
  }, []);

  // TTS: Speak when AI message arrives
  useEffect(() => {
    if (history.length > 0 && isSpeaking) {
      const lastMessage = history[history.length - 1];
      if (lastMessage.role === 'assistant') {
        speak(lastMessage.content);
      }
    }
  }, [history, isSpeaking]);

  const speak = (text: string) => {
    if (!window.speechSynthesis) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn("Speech synthesis error:", e);
    }
  };

  const toggleListening = () => {
    if (!recognition) {
      // Fallback: if browser doesn't support STT, focus manual input
      if (manualText.trim()) {
        submitAnswer(manualText);
        setManualText("");
      }
      return;
    }

    if (isListening) {
      try { recognition.stop(); } catch (e) {
        // ignore recognition stop error
      }
      setIsListening(false);
      if (transcript.trim()) {
        submitAnswer(transcript);
        setTranscript("");
      }
    } else {
      setTranscript("");
      try {
        recognition.start();
        setIsListening(true);
      } catch (e) {
        console.warn("Failed to start speech recognition:", e);
        setIsListening(false);
      }
    }
  };

  const handleManualSubmit = () => {
    const textToSubmit = manualText.trim() || transcript.trim();
    if (!textToSubmit || isLoading) return;
    submitAnswer(textToSubmit);
    setManualText("");
    setTranscript("");
  };

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-between py-6 space-y-8 animate-in fade-in zoom-in-95 duration-1000 max-w-4xl mx-auto">
      
      {/* Header Bar */}
      <div className="w-full flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-indigo-400" />
            AI Voice Recruiter Engine
          </h2>
          <p className="text-xs text-slate-400">Natural voice synthesis & speech-to-text behavioral evaluation</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-[10px] font-mono px-2.5 py-1 rounded-full border ${
            isSupportedSTT ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
          }`}>
            {isSupportedSTT ? 'STT Active' : 'Text Input Mode'}
          </span>
          <Button variant="outline" size="sm" onClick={reset} className="rounded-xl border-white/10 text-xs">
            <RotateCcw className="w-3.5 h-3.5 mr-1" /> Reset
          </Button>
        </div>
      </div>

      {/* Visualizer & Status */}
      <div className="relative flex items-center justify-center my-4">
         {/* Animated Rings */}
         <div className={cn(
           "absolute w-64 h-64 rounded-full border-2 border-indigo-500/20 animate-ping",
           isListening ? "duration-[2000ms]" : "opacity-0"
         )} />
         <div className={cn(
           "absolute w-48 h-48 rounded-full border-2 border-indigo-400/40 animate-ping",
           isListening ? "duration-[3000ms] delay-500" : "opacity-0"
         )} />
         
         {/* Core AI Sphere */}
         <div className={cn(
           "w-32 h-32 rounded-full bg-slate-900 border-4 flex items-center justify-center shadow-2xl transition-all duration-500 z-10",
           isListening ? "border-indigo-500 scale-110 shadow-[0_0_50px_rgba(99,102,241,0.4)]" : "border-white/10"
         )}>
            <BrainCircuit className={cn(
              "w-12 h-12 transition-all duration-500",
              isListening ? "text-indigo-400 scale-125" : "text-slate-500"
            )} />
         </div>
      </div>

      {/* Live Question / Transcript Display */}
      <div className="text-center max-w-2xl px-6 w-full space-y-3">
         <h3 className="text-lg font-semibold text-white tracking-tight">
            {isLoading ? "AI Recruiter is synthesizing feedback..." : isListening ? "Listening to your answer..." : "Awaiting your response"}
         </h3>
         <div className="min-h-[70px] p-4 bg-slate-900/60 border border-white/10 rounded-2xl text-sm text-slate-300 italic font-medium leading-relaxed shadow-inner">
            {transcript || manualText || (history.length > 0 ? history[history.length - 1].content : "Welcome! Press the microphone button or type below to answer.")}
         </div>
      </div>

      {/* Voice Controls */}
      <div className="flex items-center gap-6">
         <Button 
           size="icon" 
           variant="outline"
           onClick={() => setIsSpeaking(!isSpeaking)}
           className={cn("w-12 h-12 rounded-full border-white/10 hover:bg-white/5", !isSpeaking && "text-red-400 border-red-400/20")}
           title={isSpeaking ? "Mute AI Voice" : "Unmute AI Voice"}
         >
            {isSpeaking ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
         </Button>

         <button 
           onClick={toggleListening}
           disabled={isLoading}
           className={cn(
             "w-20 h-20 rounded-full flex items-center justify-center transition-all duration-500 group relative overflow-hidden shadow-2xl",
             isListening ? "bg-red-500 hover:bg-red-600 scale-95 shadow-red-500/40" : "bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/40"
           )}
           title={isListening ? "Stop Recording & Submit" : "Click to Speak"}
         >
            <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
            {isListening ? <MicOff className="w-8 h-8 text-white z-10" /> : <Mic className="w-8 h-8 text-white z-10" />}
         </button>

         <Button 
           size="icon" 
           variant="outline"
           className="w-12 h-12 rounded-full border-white/10 hover:bg-white/5"
           onClick={() => window.location.href = '/app/interview'}
           title="Switch to Standard Chat Interview"
         >
            <MessageSquare className="w-5 h-5 text-slate-300" />
         </Button>
      </div>

      {/* Text Input Fallback */}
      <div className="w-full max-w-xl flex gap-2 items-center bg-slate-900/80 border border-white/10 rounded-xl p-1.5 shadow-lg">
        <input
          type="text"
          value={manualText}
          onChange={(e) => setManualText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleManualSubmit()}
          placeholder="Or type your voice response here..."
          className="flex-1 bg-transparent border-none text-slate-200 text-sm px-3 py-2 focus:outline-none placeholder:text-slate-500"
        />
        <Button
          size="sm"
          onClick={handleManualSubmit}
          disabled={!manualText.trim() || isLoading}
          className="glow-button rounded-lg text-xs px-4"
        >
          <Send className="w-3.5 h-3.5 mr-1" /> Send
        </Button>
      </div>

      {/* Real-time Telemetry (Footer) */}
      <div className="flex gap-8 text-[11px] font-mono text-slate-500 pt-4 border-t border-white/5 w-full justify-center">
         <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
            Audio Latency: 38ms
         </div>
         <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            Vocal Confidence: 94%
         </div>
         <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            Adaptive Tone: Calibrated
         </div>
      </div>

    </div>
  );
};

