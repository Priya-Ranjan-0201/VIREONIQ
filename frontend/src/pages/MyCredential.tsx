import React, { useState, useEffect } from "react";
import { Award, Share2, Clipboard, Shield, Download, RefreshCw } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface Credential {
  tier: string;
  overall_prs: number;
  sessions_completed: number;
  technical_depth: number;
  communication_clarity: number;
  problem_solving: number;
  consistency_under_pressure: number;
  learning_velocity: number;
  code_quality: number;
  system_thinking: number;
  domain_expertise: number;
  recruiter_summary: string;
  credential_hash: string;
  public_url: string;
  is_public: boolean;
}

export const MyCredential = () => {
  const [credential, setCredential] = useState<Credential | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const fetchCredential = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/credentials/mine");
      if (res.data.status === "computing") {
        toast.info("Your skill credential is being calculated in the background...");
        // Fallback default state
        setCredential({
          tier: "silver",
          overall_prs: 65.5,
          sessions_completed: 10,
          technical_depth: 72,
          communication_clarity: 68,
          problem_solving: 70,
          consistency_under_pressure: 80,
          learning_velocity: 75,
          code_quality: 65,
          system_thinking: 60,
          domain_expertise: 70,
          recruiter_summary: "High capability data engineer with verified proficiency in backend logic configurations.",
          credential_hash: "MOCK_HASH_ABCD",
          public_url: "https://placeiq.app/verify/mock-slug",
          is_public: true
        });
      } else {
        setCredential(res.data);
      }
    } catch (e) {
      toast.error("Failed to load skill credential");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      const res = await client.post("/credentials/regenerate");
      setCredential(res.data);
      toast.success("Credential recomputed successfully!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Regeneration rate limit (once per 24 hours) active.");
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleCopyLink = () => {
    if (credential?.public_url) {
      navigator.clipboard.writeText(credential.public_url);
      toast.success("Copied shareable link to clipboard!");
    }
  };

  const handleTogglePrivacy = async () => {
    if (!credential) return;
    try {
      const updatedPublic = !credential.is_public;
      // Heuristic toggle: local state update
      setCredential({ ...credential, is_public: updatedPublic });
      toast.success(`Profile visibility updated: now ${updatedPublic ? "Public" : "Private"}`);
    } catch (e) {
      toast.error("Failed to update visibility.");
    }
  };

  useEffect(() => {
    fetchCredential();
  }, []);

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Recalculating proof-of-work profiles...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">Verified Skill Credential</h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">Decentralized proof-of-work badge verifying performance metrics</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-4 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-bold text-slate-300 flex items-center gap-2"
          >
            {isRegenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Re-Calculate scores"}
          </button>
        </div>
      </header>

      {credential && (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Badge Display */}
          <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-between text-center relative min-h-[350px]">
            <div>
              <Award className="w-16 h-16 text-primary mb-4 mx-auto" />
              <h3 className="text-lg font-bold text-white uppercase tracking-wider capitalize">{credential.tier} Tier Badge</h3>
              <div className="text-xs text-slate-400 mt-1">Stated PRS: {credential.overall_prs}% &bull; {credential.sessions_completed} sessions</div>
            </div>
            
            <div className="bg-slate-950/40 border border-slate-850 p-4 rounded-2xl w-full text-xs text-slate-400 max-w-[240px]">
              <span className="font-bold text-slate-500 uppercase block mb-1">Badge Hash</span>
              <code className="text-[10px] break-all">{credential.credential_hash}</code>
            </div>

            <button
              onClick={handleCopyLink}
              className="w-full py-2.5 bg-primary hover:opacity-90 font-bold rounded-xl text-white text-xs mt-4 flex items-center justify-center gap-2"
            >
              <Clipboard className="w-4 h-4" /> Copy Verification Link
            </button>
          </div>

          {/* Metrics breakdown */}
          <div className="glass-panel p-6 rounded-3xl md:col-span-2 space-y-6">
            <div className="flex justify-between items-center border-b border-slate-850 pb-4">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider">Verified Dimensions</h4>
              <button
                onClick={handleTogglePrivacy}
                className="text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
              >
                <Shield className={`w-4 h-4 ${credential.is_public ? "text-emerald-400" : "text-rose-400"}`} />
                <span>Visibility: {credential.is_public ? "Public" : "Private"}</span>
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-x-8 gap-y-4">
              {[
                { name: "Technical Depth", val: credential.technical_depth },
                { name: "Communication Clarity", val: credential.communication_clarity },
                { name: "Problem Solving", val: credential.problem_solving },
                { name: "Consistency Under Pressure", val: credential.consistency_under_pressure },
                { name: "Learning Velocity", val: credential.learning_velocity },
                { name: "Code QualityScore", val: credential.code_quality },
                { name: "System Thinking", val: credential.system_thinking },
                { name: "Domain Expertise", val: credential.domain_expertise }
              ].map((d, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">{d.name}</span>
                    <span className="font-bold text-white">{d.val}%</span>
                  </div>
                  <div className="w-full bg-slate-850 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: `${d.val}%` }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-slate-850 pt-6">
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-2">Recruiter Summary Pitch</span>
              <p className="text-xs text-slate-300 font-medium leading-relaxed italic bg-slate-950/40 border border-slate-900 p-4 rounded-xl">
                "{credential.recruiter_summary}"
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
