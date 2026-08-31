import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  CreditCard, 
  TrendingUp, 
  Zap, 
  ArrowRight, 
  CheckCircle2, 
  MessageSquare,
  Sparkles,
  Building2,
  Send,
  DollarSign,
  ShieldCheck,
  RotateCcw,
  Scale
} from "lucide-react";
import client from "@/api/client";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const PRESET_OFFERS = [
  {
    id: "google_sde",
    company: "Google",
    role: "Software Engineer (L3)",
    base_salary: 2400000,
    currency: "INR",
    joining_bonus: 400000,
    equity_text: "₹14,00,000 GSU/year (4-year vesting schedule)",
    benefits: ["Free Gourmet Meals", "₹10L Health Insurance", "Wellness Budget", "Hybrid 3/2"],
    negotiation_leverage: "High",
    tips: [
      "Google recruiters often have flexibility of +10-15% on Base if you present competing tier-1 product offers.",
      "Target an increase in Year-1 signing bonus if base salary hits the standard band ceiling.",
      "Highlight your verified distributed systems micro-internship credentials."
    ]
  },
  {
    id: "stripe_infra",
    company: "Stripe",
    role: "Backend Infrastructure Engineer",
    base_salary: 2800000,
    currency: "INR",
    joining_bonus: 500000,
    equity_text: "₹15,00,000 RSUs/year (Quarterly vesting)",
    benefits: ["100% Remote Flexibility", "₹1.5L Home Office Setup", "Global Offsites", "Comprehensive Medical"],
    negotiation_leverage: "High",
    tips: [
      "Stripe values extreme technical craftsmanship; highlight your reliability and idempotent architecture experience.",
      "Ask for an increase in signing bonus to offset any unvested stock left at your prior company."
    ]
  },
  {
    id: "zepto_core",
    company: "Zepto",
    role: "Core Systems Engineer",
    base_salary: 1800000,
    currency: "INR",
    joining_bonus: 250000,
    equity_text: "₹6,00,000 ESOPs/year (4-year vesting)",
    benefits: ["Fast-Track Promotion Cycle", "Health Insurance", "Late Night Cab/Food Allowance"],
    negotiation_leverage: "Medium",
    tips: [
      "High-growth startups are cash-conscious but equity-generous; request a 25% bump in ESOP allocation.",
      "Request a guaranteed 6-month performance appraisal milestone with predefined promotion metrics."
    ]
  }
];

export const OfferNegotiatorPage = () => {
  const [activeOffer, setActiveOffer] = useState<any>(PRESET_OFFERS[0]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTactic, setSelectedTactic] = useState<string>("competing");
  const [counterResponse, setCounterResponse] = useState<any>(null);
  const [isCountering, setIsCountering] = useState(false);
  const [sessionId, setSessionId] = useState("");

  const handleSelectPreset = (preset: any) => {
    setActiveOffer(preset);
    setCounterResponse(null);
    toast.success(`Loaded ${preset.company} offer simulation!`);
  };

  const handleCustomGenerate = async () => {
    if (!sessionId.trim()) {
      toast.info("Select one of the 1-click MNC simulation presets below or enter an ID.");
      return;
    }
    setIsLoading(true);
    try {
      const res = await client.post(`/offers/generate/${sessionId}`);
      if (res.data) {
        setActiveOffer({
          ...res.data,
          company: "Partner MNC",
          role: "Software Engineer"
        });
        toast.success("Offer generated from interview session!");
      }
    } catch (e) {
      toast.info("Using calibrated senior SDE offer package.");
      setActiveOffer(PRESET_OFFERS[0]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateCounter = async () => {
    setIsCountering(true);
    try {
      const payload = {
        tactic: selectedTactic,
        target_company: activeOffer.company || "Google",
        current_base: activeOffer.base_salary,
        current_bonus: activeOffer.joining_bonus,
        current_equity: activeOffer.equity_text
      };
      const res = await client.post("/offers/simulate-counter", payload);
      setCounterResponse(res.data);

      // Dynamically update active offer compensation
      setActiveOffer((prev: any) => ({
        ...prev,
        base_salary: res.data.negotiated_base,
        joining_bonus: res.data.negotiated_bonus
      }));

      toast.success("Recruiter responded to your counter! +50 XP 🎯");
    } catch (e) {
      // Fallback simulation
      const newBase = Math.round(activeOffer.base_salary * 1.12);
      setCounterResponse({
        status: "counter_received",
        recruiter_response: `We discussed with the Engineering VP and hiring committee. Given your strong technical scores and verified portfolio, we have received approval to adjust your base salary to ₹${(newBase / 100000).toFixed(1)}L CTC.`,
        negotiated_base: newBase,
        negotiated_bonus: activeOffer.joining_bonus,
        outcome_summary: "Accepted +12% Base Bump"
      });
      setActiveOffer((prev: any) => ({
        ...prev,
        base_salary: newBase
      }));
      toast.success("Counter-offer simulation updated! +50 XP 🎯");
    } finally {
      setIsCountering(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 tracking-wide uppercase mb-1">
            <Zap className="w-3.5 h-3.5" /> High-Stakes Career Strategy
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shadow-lg shadow-amber-500/10">
              <Scale className="w-5 h-5" />
            </div>
            AI Offer Negotiator
          </h1>
          <p className="text-slate-400 mt-1 text-sm max-w-xl">
            Simulate recruiter pushback, test real-world counter-offer scripts, and optimize your CTC package with AI HR intelligence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/30 px-3 py-1.5 font-bold text-xs rounded-xl">
            BAR-RAISER NEGOTIATION AI ACTIVE
          </Badge>
        </div>
      </header>

      {/* Preset Selector */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Select 1-Click Company Offer Simulation
          </span>
          <span className="text-xs text-slate-500">Live compensation bands</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {PRESET_OFFERS.map((preset) => {
            const isSelected = activeOffer?.id === preset.id;
            return (
              <button
                key={preset.id}
                onClick={() => handleSelectPreset(preset)}
                className={cn(
                  "p-4 rounded-2xl border text-left transition-all flex flex-col justify-between",
                  isSelected
                    ? "bg-amber-500/10 border-amber-500/50 shadow-lg shadow-amber-500/10"
                    : "bg-slate-950 border-white/10 hover:border-white/20"
                )}
              >
                <div>
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-black text-white">{preset.company}</span>
                    <Badge variant="outline" className="text-[10px] border-white/10 text-slate-400">
                      {preset.negotiation_leverage} Leverage
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-400 font-medium mt-0.5">{preset.role}</p>
                </div>
                <div className="mt-3 pt-2 border-t border-white/5 flex justify-between items-center text-xs">
                  <span className="text-slate-500">Base + Sign-on</span>
                  <span className="font-black text-emerald-400">
                    ₹{((preset.base_salary + preset.joining_bonus) / 100000).toFixed(1)}L
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Offer Package + Live Negotiation Counter Lab */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Active Offer Details Card */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="bg-slate-950 border border-white/10 rounded-3xl shadow-2xl overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500/20 via-cyan-500/10 to-transparent p-6 sm:p-8 border-b border-white/5 flex justify-between items-center">
              <div>
                <span className="text-[10px] font-bold text-emerald-400 tracking-wider uppercase">Active Offer Package</span>
                <h3 className="text-2xl sm:text-3xl font-black text-white mt-1">{activeOffer.role}</h3>
                <p className="text-xs text-slate-400 font-semibold mt-0.5">{activeOffer.company} • Tier-1 Engineering</p>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
            </div>

            <CardContent className="p-6 sm:p-8 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-slate-900/70 border border-white/5">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                    Fixed Base Salary
                  </span>
                  <p className="text-2xl sm:text-3xl font-black text-white">
                    ₹{(activeOffer.base_salary / 100000).toFixed(1)}L
                  </p>
                  <span className="text-[10px] text-slate-400">Monthly: ~₹{Math.round(activeOffer.base_salary / 12).toLocaleString()}</span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/70 border border-white/5">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                    Sign-on / Joining Bonus
                  </span>
                  <p className="text-2xl sm:text-3xl font-black text-emerald-400">
                    ₹{(activeOffer.joining_bonus / 100000).toFixed(1)}L
                  </p>
                  <span className="text-[10px] text-slate-400">Disbursed with Month 1 Payroll</span>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">
                  Equity & Long-Term Incentive
                </span>
                <div className="text-sm font-semibold text-slate-200 bg-slate-900/50 p-4 rounded-2xl border border-white/5">
                  {activeOffer.equity_text}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">
                  Benefits & Perks Included
                </span>
                <div className="flex flex-wrap gap-2">
                  {activeOffer.benefits.map((b: string, i: number) => (
                    <span key={i} className="text-xs bg-slate-900 text-slate-300 px-3 py-1.5 rounded-xl border border-white/5 font-medium">
                      {b}
                    </span>
                  ))}
                </div>
              </div>

              {/* Recruiter Negotiation Tips */}
              <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-2">
                <span className="text-xs font-black text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" /> High-Leverage Counter Tips
                </span>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {activeOffer.tips?.map((tip: string, i: number) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-amber-400">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Live Negotiation Counter Lab */}
        <div className="space-y-6">
          <Card className="bg-slate-950 border border-amber-500/30 rounded-3xl shadow-2xl p-6 space-y-5">
            <div>
              <div className="flex items-center gap-2 text-xs font-black text-amber-400 uppercase tracking-wider">
                <MessageSquare className="w-4 h-4" /> AI Recruiter Negotiation Lab
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Select your negotiation leverage tactic and submit your counter to the AI HR Director.
              </p>
            </div>

            <div className="space-y-2.5">
              <label className="text-xs font-bold text-slate-300 block">Choose Your Strategy:</label>
              {[
                { id: "competing", label: "Counter with Competing Product Offer", desc: "Requests +12% base bump to match market benchmark" },
                { id: "bonus", label: "Ask for Higher Upfront Sign-on Bonus", desc: "Safest route when base salary bands are strictly fixed (+₹2L)" },
                { id: "remote", label: "Negotiate Flexible Remote Work & Stipend", desc: "Secures 3-day WFH schedule + ₹1L home ergonomics allowance" }
              ].map((tac) => (
                <div
                  key={tac.id}
                  onClick={() => setSelectedTactic(tac.id)}
                  className={cn(
                    "p-3 rounded-xl border cursor-pointer transition-all",
                    selectedTactic === tac.id
                      ? "bg-amber-500/10 border-amber-500 text-white"
                      : "bg-slate-900 border-white/5 text-slate-400 hover:text-white"
                  )}
                >
                  <p className="text-xs font-black">{tac.label}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">{tac.desc}</p>
                </div>
              ))}
            </div>

            <Button
              onClick={handleSimulateCounter}
              disabled={isCountering}
              className="w-full py-6 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-xl font-black text-xs shadow-lg shadow-amber-600/30 flex items-center justify-center gap-2"
            >
              {isCountering ? (
                <span>Negotiating with AI HR...</span>
              ) : (
                <>
                  <span>Dispatch Counter-Offer</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </Button>

            {/* Recruiter Live Response Feed */}
            {counterResponse && (
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 space-y-2 animate-fade-in">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                    HR Director Response:
                  </span>
                  <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px]">
                    {counterResponse.outcome_summary}
                  </Badge>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed italic">
                  "{counterResponse.recruiter_response}"
                </p>
                <div className="pt-2 border-t border-emerald-500/20 flex justify-between text-xs font-bold">
                  <span className="text-slate-400">Updated Base CTC:</span>
                  <span className="text-emerald-400">
                    ₹{(counterResponse.negotiated_base / 100000).toFixed(1)}L
                  </span>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
