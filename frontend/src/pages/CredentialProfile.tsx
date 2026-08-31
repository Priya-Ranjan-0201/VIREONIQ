import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Award, ShieldCheck } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface PublicCredential {
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
  public_url: string;
  issued_at: string;
  last_updated_at: string;
}

const LinkedinIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
    <rect width="4" height="12" x="2" y="9" />
    <circle cx="4" cy="4" r="2" />
  </svg>
);

const TwitterIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z" />
  </svg>
);

export const CredentialProfile = () => {
  const { slug } = useParams<{ slug: string }>();
  const [credential, setCredential] = useState<PublicCredential | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const shareToLinkedIn = () => {
    if (!credential) return;
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, "_blank");
  };

  const shareToX = () => {
    if (!credential) return;
    const text = encodeURIComponent(`Check out my verified skill credential on PlaceIQ! 🎓 Tier: ${credential.tier.toUpperCase()} | Overall PRS: ${credential.overall_prs}%\n\n`);
    const url = encodeURIComponent(window.location.href);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank");
  };

  const fetchPublicProfile = async () => {
    setIsLoading(true);
    try {
      const res = await client.get(`/credentials/verify/${slug}`);
      setCredential(res.data);
    } catch (e) {
      toast.error("Failed to load public verify parameters. Link may be invalid or set to private.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (slug) {
      fetchPublicProfile();
    }
  }, [slug]);

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Verifying credential signatures...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-primary/10 border border-primary/20 rounded-full text-xs font-bold text-primary uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" /> Secure Verification Signature Matches
        </div>
        <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">PlaceIQ Verified Credential</h2>
        <p className="text-[#9CA3AF] text-sm uppercase tracking-widest font-semibold">Decentralized, tamper-proof proof-of-work profiles</p>
      </header>

      {credential ? (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Badge Display */}
          <div className="glass-panel p-6 rounded-3xl flex flex-col items-center justify-between text-center relative min-h-[300px]">
            <div>
              <Award className="w-16 h-16 text-amber-500 mb-4 mx-auto" />
              <h3 className="text-lg font-bold text-white uppercase tracking-wider capitalize">{credential.tier} Tier</h3>
              <div className="text-xs text-slate-400 mt-1">Stated PRS: {credential.overall_prs}% &bull; {credential.sessions_completed} sessions</div>
            </div>
            
            <div className="w-full space-y-2 mt-4 pt-4 border-t border-slate-800">
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Share Credential</span>
              <div className="flex gap-2">
                <button
                  onClick={shareToLinkedIn}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-[#0077B5]/10 hover:bg-[#0077B5]/20 border border-[#0077B5]/20 rounded-xl text-[10px] font-bold text-[#0077B5] transition-colors"
                >
                  <LinkedinIcon className="w-3.5 h-3.5" /> LinkedIn
                </button>
                <button
                  onClick={shareToX}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-[10px] font-bold text-white transition-colors"
                >
                  <TwitterIcon className="w-3.5 h-3.5" /> X / Twitter
                </button>
              </div>
            </div>

            <div className="text-[10px] text-slate-500 mt-4 leading-relaxed border-t border-slate-800 pt-4 w-full">
              Issued at: {new Date(credential.issued_at).toLocaleDateString()}<br />
              Last verified: {new Date(credential.last_updated_at).toLocaleDateString()}
            </div>
          </div>

          {/* Metrics breakdown */}
          <div className="glass-panel p-6 rounded-3xl md:col-span-2 space-y-6">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-850 pb-4">Verified Candidate Performance</h4>
            
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
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-2">Verified Skill Summary Pitch</span>
              <p className="text-xs text-slate-350 leading-relaxed italic bg-slate-950/40 border border-slate-900 p-4 rounded-xl">
                "{credential.recruiter_summary}"
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-sm text-slate-500 py-12">Credential verify link is invalid or set to private.</div>
      )}
    </div>
  );
};
