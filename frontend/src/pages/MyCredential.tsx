import client from "@/api/client";
import { PreviewBanner, SampleDataBadge } from "@/components/shared/SampleDataBanner";
import { Award, Clipboard, Eye, RefreshCw, Shield } from "lucide-react";
import { useEffect, useState } from "react";
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

const SAMPLE_CREDENTIAL: Credential = {
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
  recruiter_summary: "Demonstration profile with benchmarked proficiency in backend service configurations.",
  credential_hash: "DEMO-SAMPLE-HASH-NOT-VERIFIED",
  public_url: "https://vireoniq.app/verify/sample-preview",
  is_public: true,
};

export const MyCredential = () => {
  const [credential, setCredential] = useState<Credential | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isComputing, setIsComputing] = useState(false);
  const [showSamplePreview, setShowSamplePreview] = useState(false);

  const fetchCredential = async () => {
    setIsLoading(true);
    try {
      const res = await client.get("/credentials/mine");
      if (res.data?.status === "computing") {
        setIsComputing(true);
        setCredential(null);
      } else if (res.data && res.data.tier) {
        setCredential(res.data);
        setIsComputing(false);
      } else {
        setIsComputing(true);
        setCredential(null);
      }
    } catch (e) {
      setIsComputing(true);
      setCredential(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      const res = await client.post("/credentials/regenerate");
      if (res.data && res.data.tier) {
        setCredential(res.data);
        setIsComputing(false);
        toast.success("Credential recomputed successfully!");
      } else {
        setIsComputing(true);
        toast.info("Credential calculation queued.");
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Regeneration rate limit (once per 24 hours) active.");
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleCopyLink = () => {
    const active = credential || (showSamplePreview ? SAMPLE_CREDENTIAL : null);
    if (active?.public_url) {
      navigator.clipboard.writeText(active.public_url);
      toast.success("Copied shareable link to clipboard!");
    }
  };

  const handleTogglePrivacy = async () => {
    if (!credential) return;
    try {
      const updatedPublic = !credential.is_public;
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
    return <div className="p-8 text-center text-slate-400">Loading skill credential...</div>;
  }

  const activeDisplay = credential || (showSamplePreview ? SAMPLE_CREDENTIAL : null);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">
              Verified Skill Credential
            </h2>
            {showSamplePreview && !credential && (
              <SampleDataBadge label="Sample Demonstration Preview" />
            )}
          </div>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">
            Decentralized proof-of-work badge verifying performance metrics
          </p>
        </div>
        <div className="flex gap-2">
          {isComputing && !credential && (
            <button
              onClick={() => setShowSamplePreview(!showSamplePreview)}
              className="px-4 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-bold text-slate-300 flex items-center gap-2"
            >
              <Eye className="w-4 h-4" />
              {showSamplePreview ? "Hide Sample Preview" : "View Sample Preview"}
            </button>
          )}
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-4 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-bold text-slate-300 flex items-center gap-2"
          >
            {isRegenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Re-Calculate scores"}
          </button>
        </div>
      </header>

      {/* Honest Computing Notice when no credential exists */}
      {isComputing && !credential && !showSamplePreview && (
        <div className="glass-panel p-8 rounded-3xl text-center space-y-4 max-w-xl mx-auto">
          <Award className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">Credential Pending Evaluation</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Your verified skill badge is computed from your completed interview practice sessions, code reviews, and technical assessments. Complete at least one technical session to generate your credential.
          </p>
          <button
            onClick={() => setShowSamplePreview(true)}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-semibold text-slate-300 inline-flex items-center gap-2"
          >
            <Eye className="w-4 h-4" /> View Sample Demonstration Badge
          </button>
        </div>
      )}

      {showSamplePreview && !credential && (
        <PreviewBanner
          title="Demonstration Credential Preview"
          description="Your actual credential requires completed interview sessions. The scores and hash displayed below are an illustrative demonstration preview."
          tier="Demonstration Only"
        />
      )}

      {activeDisplay && (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Badge Display */}
          <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-between text-center relative min-h-[350px]">
            <div>
              <Award className="w-16 h-16 text-primary mb-4 mx-auto" />
              <h3 className="text-lg font-bold text-white uppercase tracking-wider capitalize">
                {activeDisplay.tier} Tier Badge
              </h3>
              <div className="text-xs text-slate-400 mt-1">
                Stated PRS: {activeDisplay.overall_prs}% &bull; {activeDisplay.sessions_completed} sessions
              </div>
            </div>

            <div className="bg-slate-950/40 border border-slate-850 p-4 rounded-2xl w-full text-xs text-slate-400 max-w-[240px]">
              <span className="font-bold text-slate-500 uppercase block mb-1">Badge Hash</span>
              <code className="text-[10px] break-all">{activeDisplay.credential_hash}</code>
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
                disabled={!credential}
                className="text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
              >
                <Shield className={`w-4 h-4 ${activeDisplay.is_public ? "text-emerald-400" : "text-rose-400"}`} />
                <span>Visibility: {activeDisplay.is_public ? "Public" : "Private"}</span>
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-x-8 gap-y-4">
              {[
                { name: "Technical Depth", val: activeDisplay.technical_depth },
                { name: "Communication Clarity", val: activeDisplay.communication_clarity },
                { name: "Problem Solving", val: activeDisplay.problem_solving },
                { name: "Consistency Under Pressure", val: activeDisplay.consistency_under_pressure },
                { name: "Learning Velocity", val: activeDisplay.learning_velocity },
                { name: "Code QualityScore", val: activeDisplay.code_quality },
                { name: "System Thinking", val: activeDisplay.system_thinking },
                { name: "Domain Expertise", val: activeDisplay.domain_expertise },
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
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-2">
                Recruiter Summary Pitch
              </span>
              <p className="text-xs text-slate-300 font-medium leading-relaxed italic bg-slate-950/40 border border-slate-900 p-4 rounded-xl">
                "{activeDisplay.recruiter_summary}"
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
