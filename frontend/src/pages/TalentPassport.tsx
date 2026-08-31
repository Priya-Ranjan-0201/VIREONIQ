import React, { useState, useEffect } from "react";
import { Award, Globe, FileText, Share2, Compass, CheckCircle, ChevronDown, RefreshCw } from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";

interface Passport {
  passport_id: string;
  country_code: string;
  verified_role: string;
  skill_tier: string;
  prs_score: number;
  english_proficiency_tier: string;
  eligible_company_tiers: string[];
  visa_pathways: string[];
  contractor_rate_min: number;
  contractor_rate_max: number;
  public_passport_url: string;
}

interface Opportunity {
  company_name: string;
  role: string;
  hiring_tier: string;
  timezone_overlap_percentage: number;
  salary_usd: number;
  salary_localized_ppp: number;
  application_path: string;
  visa_type: string;
}

interface Translation {
  professional_summary: string;
  top_dimensions: string[];
  key_skills: string[];
  downplay_advice: string;
}

export const TalentPassport = () => {
  const [passport, setPassport] = useState<Passport | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [targetMarket, setTargetMarket] = useState("US");
  const [translation, setTranslation] = useState<Translation | null>(null);
  const [countryGuide, setCountryGuide] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPassportData = async () => {
    setIsLoading(true);
    try {
      // 1. Generate/Fetch passport
      const passRes = await client.post("/global/generate-passport");
      setPassport(passRes.data);
      
      // 2. Fetch opportunities
      const oppRes = await client.get("/global/opportunities");
      setOpportunities(oppRes.data);

      // 3. Fetch country guide
      const guideRes = await client.get(`/global/country-guide/${passRes.data.country_code}`);
      setCountryGuide(guideRes.data);
    } catch (e) {
      toast.error("Failed to load global talent passport metrics.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTranslate = async () => {
    try {
      const res = await client.post("/global/translate-credential", { target_market: targetMarket });
      setTranslation(res.data);
      toast.success(`Profile translated for ${targetMarket} market!`);
    } catch (e) {
      toast.error("Translation reframe failed.");
    }
  };

  const handleDownloadPDF = async () => {
    try {
      toast.info("Generating and downloading your passport PDF...");
      const response = await client.get("/global/my-passport.pdf", {
        responseType: "blob"
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `passport_${passport?.passport_id || "global"}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("PDF passport downloaded successfully! 📄");
    } catch (e) {
      console.error(e);
      toast.error("PDF generation failed.");
    }
  };

  useEffect(() => {
    fetchPassportData();
  }, []);

  useEffect(() => {
    if (passport) {
      handleTranslate();
    }
  }, [targetMarket, passport]);

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Booting global parity engines...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-750">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-[#9CA3AF] bg-clip-text text-transparent">Global Parity Talent Passport</h2>
          <p className="text-[#9CA3AF] mt-2 text-sm uppercase tracking-widest font-semibold">Verified talent passport for cross-border opportunities</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleDownloadPDF}
            className="px-4 py-2 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-bold text-slate-300 flex items-center gap-2"
          >
            <FileText className="w-4 h-4 text-primary" /> Download PDF Passport
          </button>
        </div>
      </header>

      {passport && (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Passport Digital Card */}
          <div className="bg-gradient-to-br from-[#1E293B] to-[#0F172A] border border-amber-500/20 p-6 rounded-3xl relative overflow-hidden shadow-2xl flex flex-col justify-between min-h-[360px]">
            {/* Background seal */}
            <div className="absolute right-0 bottom-0 translate-x-10 translate-y-10 opacity-5 pointer-events-none">
              <Globe className="w-64 h-64 text-amber-500" />
            </div>

            <div>
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[10px] font-bold tracking-widest uppercase text-amber-500">PlaceIQ Global Passport</span>
                  <h3 className="text-sm font-semibold text-slate-300 uppercase mt-1">Talent Credential</h3>
                </div>
                <span className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/25 text-amber-500 text-[10px] font-bold rounded-lg uppercase tracking-wider">
                  {passport.skill_tier} Tier
                </span>
              </div>

              <div className="mt-8 space-y-4">
                <div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Passport ID</div>
                  <div className="text-sm font-mono text-white mt-0.5">{passport.passport_id}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Verified Role</div>
                  <div className="text-sm font-bold text-white mt-0.5">{passport.verified_role}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">English Level</div>
                  <div className="text-xs font-semibold text-emerald-400 mt-0.5">{passport.english_proficiency_tier}</div>
                </div>
              </div>
            </div>

            <div className="border-t border-slate-800 pt-4 mt-8 flex justify-between items-end">
              <div>
                <div className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Contractor Rate Range</div>
                <div className="text-sm font-bold text-white mt-0.5">${passport.contractor_rate_min} - ${passport.contractor_rate_max}/hr</div>
              </div>
              <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center p-1">
                {/* QR Code Placeholder */}
                <div className="w-full h-full border-2 border-slate-900 bg-slate-900 flex items-center justify-center">
                  <span className="text-[6px] text-white">QR</span>
                </div>
              </div>
            </div>
          </div>

          {/* Market Translation Reframing */}
          <div className="glass-panel p-6 rounded-3xl md:col-span-2 space-y-6">
            <div className="flex justify-between items-center border-b border-slate-850 pb-4">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider">Recruiter Localization Reframe</h4>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-medium">Target Market: </span>
                <select
                  value={targetMarket}
                  onChange={(e) => setTargetMarket(e.target.value)}
                  className="px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-slate-300 outline-none"
                >
                  <option value="US">United States (US)</option>
                  <option value="EU">European Union (EU)</option>
                  <option value="UK">United Kingdom (UK)</option>
                  <option value="SG">Singapore (SG)</option>
                  <option value="AE">United Arab Emirates (AE)</option>
                  <option value="AU">Australia (AU)</option>
                </select>
              </div>
            </div>

            {translation ? (
              <div className="space-y-4">
                <div>
                  <div className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">Local Summary Pitch</div>
                  <p className="text-xs text-slate-300 leading-relaxed font-medium bg-slate-950/40 border border-slate-900 p-4 rounded-2xl">{translation.professional_summary}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">Key Highlight Dimensions</div>
                    <ul className="space-y-1">
                      {translation.top_dimensions.map((dim, i) => (
                        <li key={i} className="text-xs text-slate-300 flex items-center gap-1.5">
                          <CheckCircle className="w-3.5 h-3.5 text-primary" /> {dim}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-2">Reframed Skills list</div>
                    <div className="flex flex-wrap gap-1.5">
                      {translation.key_skills.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-slate-850 text-slate-400 text-[10px] font-bold rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="border-t border-slate-850 pt-4">
                  <div className="text-xs text-amber-500 font-bold uppercase tracking-wider mb-1">Phrasing to Downplay/Reframe</div>
                  <p className="text-xs text-slate-400 leading-relaxed">{translation.downplay_advice}</p>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-500">Reframing data...</div>
            )}
          </div>
        </div>
      )}

      {/* Global Opportunities Panel */}
      <div className="glass-panel p-6 rounded-3xl space-y-6">
        <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Compass className="w-4.5 h-4.5 text-primary" /> Eligible Remote-First Opportunities
        </h4>
        <div className="grid md:grid-cols-2 gap-6">
          {opportunities.map((opp, idx) => (
            <div key={idx} className="bg-slate-950/40 border border-slate-850 p-5 rounded-2xl flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="font-bold text-white text-sm">{opp.company_name}</h5>
                    <span className="text-xs text-slate-400 mt-0.5 block">{opp.role}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-slate-850 text-slate-300 text-[9px] font-bold rounded uppercase tracking-wider">
                    {opp.hiring_tier.replace("_", " ")}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div>
                    <div className="text-[10px] text-slate-500">Stated USD rate</div>
                    <div className="text-xs font-bold text-white mt-0.5">${opp.salary_usd.toLocaleString()} / yr</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500">Local PPP Equivalent</div>
                    <div className="text-xs font-bold text-emerald-400 mt-0.5">${opp.salary_localized_ppp.toLocaleString()} / yr</div>
                  </div>
                </div>
              </div>
              <div className="border-t border-slate-850 pt-4 mt-6 flex justify-between items-center text-xs">
                <span className="text-slate-400 font-semibold">Overlap: <strong className="text-white">{opp.timezone_overlap_percentage}%</strong></span>
                <button className="px-3 py-1.5 bg-primary hover:opacity-90 font-bold rounded-lg text-white text-[11px]">
                  Apply via {opp.application_path.replace("_", " ")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
